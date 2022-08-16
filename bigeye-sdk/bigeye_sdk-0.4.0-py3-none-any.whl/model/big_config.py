from __future__ import annotations

from typing import List, Optional, Dict, Tuple, Any

from bigeye_sdk.yaml_validation.YamlValidationErrorMessages import DUPLICATE_SAVED_METRIC_ID_EXISTS_ERRMSG, \
    DUPLICATE_TAG_EXISTS_ERRMSG, TAG_ID_NOT_EXISTS_IN_TAG_DEFINITION_ERRMSG, \
    SAVED_METRIC_ID_NOT_EXISTS_IN_SAVED_METRICS_DEFINITION_ERRMSG, FQ_COL_NOT_RESOLVES_TO_COLUMN_ERRMSG, \
    WILD_CARDS_NOT_SUPPORT_IN_FQ_TABLE_NAMES_ERRMSG, FQ_TABLE_NAME_MUST_RESOLVE_TO_TABLE_ERRMSG, \
    SRC_NOT_EXISTS_FOR_DEPLOYMENT_ERRMSG
from bigeye_sdk.exceptions.exceptions import InvalidConfigurationException
from bigeye_sdk.functions.search_and_match_functions import wildcard_search
from bigeye_sdk.generated.com.torodata.models.generated import Source, CohortAndMetricDefinition, CohortDefinition, \
    MetricSuite, CatalogEntityType
from bigeye_sdk.log import get_logger
from pydantic import Field, PrivateAttr, validator

from bigeye_sdk.yaml_validation.yaml_model_base import YamlModelWithValidatorContext
from bigeye_sdk.model.protobuf_message_facade import SimpleMetricDefinition, SimpleSLA
from bigeye_sdk.serializable import File

log = get_logger(__file__)


def _explode_fq_name(fq_name: str) -> List[str]:
    """
    Explodes a fully qualifeid name into a list of names.  Supports wild cards as *. Supports single and double-quoted
    names containing periods.  Will force concatenation of database and schema names per Bigeye standard.
        Example: wh."my.database".table.column resolves to ['wh', 'my.database', 'table', 'column']
        Example wh.my_database.my_schema.table.colum resolves to ['wh', 'my_database.myschema', 'table', 'column']
    Args:
        fq_name: fully qualified asset name.

    Returns: list of names from the fully qualified name.
    """
    import re
    splt_unquoted_period_pattern = re.compile(r'''((?:[^."']|"[^"]*"|'[^']*')+)''')
    remove_quotes_pattern = re.compile(r"\"|'")
    r = [remove_quotes_pattern.sub('', i) for i in splt_unquoted_period_pattern.split(fq_name)[1::2]]

    return r


def _explode_fq_column_selectors(fq_column_selector: str) -> List[str]:
    names = _explode_fq_name(fq_column_selector)

    if len(names) == 5:
        """Accommodates source types that have a source/instance, database, and schema in the fully 
        qualified name"""
        names[1:3] = ['.'.join(names[1:3])]
        return names
    elif len(names) == 4:
        """Accommodates source types that have a source/instance/database and schema in the fully qualified
        name"""
        return names
    else:
        """Other patterns not currently supported."""
        raise InvalidConfigurationException(f"Fully qualified column selectors must resolve to a column.  Names "
                                            f"must have either 3 elements or 4 elements.  For example: "
                                            f"source.schema.table.column OR "
                                            f"source.database.schema.table.column.  Wild cards are accepted.  "
                                            f"The fully qualified name given is {fq_column_selector}")


def _explode_fq_table_name(fq_table_name: str) -> List[str]:
    names = _explode_fq_name(fq_table_name)

    if len(names) == 4:
        """Accommodates source types that have a source/instance, database, and schema in the fully 
        qualified name"""
        names[1:3] = ['.'.join(names[1:3])]
        return names
    elif len(names) == 3:
        """Accommodates source types that have a source/instance/database and schema in the fully qualified
        name"""
        return names
    else:
        """Other patterns not currently supported."""
        raise InvalidConfigurationException(f"Fully qualified table names must have 3 elements or 4 elements.  For"
                                            f"example: source.schema.table OR source.database.schema.table.  "
                                            f"Wild cards are accepted.  The fully qualified name given "
                                            f"is {fq_table_name}")


class ColumnSelector(YamlModelWithValidatorContext):
    name: str

    # types: List[SimpleFieldType] TODO V1

    @validator('name')
    def must_have_split_length_4_or_5(cls, v):
        if v == '' or len(v) == 0 or len(_explode_fq_name(v)) not in [4, 5]:
            error_message = FQ_COL_NOT_RESOLVES_TO_COLUMN_ERRMSG.format(fq_column_name=v)
            cls.raise_validation_error(error_lines=[v], error_message=error_message)

        return v

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, ColumnSelector):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.name == other.name


class TagDefinition(YamlModelWithValidatorContext):
    tag_id: str
    column_selectors: List[ColumnSelector]

    def __hash__(self):
        return hash((repr(self.tag_id), self.column_selectors))


# @dataclass
# class SavedMetricCollection:
#     collection_name: str
#     saved_metric_ids: List[str]


class SavedMetricDefinitions(YamlModelWithValidatorContext):
    # metric_collections: SavedMetricCollection
    metrics: List[SimpleMetricDefinition]

    # TODO: V1 define rule for validating that every saved MetricCollection `saved_metric_id` references a saved_metric
    # TODO: in the saved Metrics section.


class RowCreationTimes(YamlModelWithValidatorContext):
    tag_ids: Optional[List[str]] = Field(default_factory=lambda: [])
    column_selectors: Optional[List[ColumnSelector]] = Field(default_factory=lambda: [])

    def to_cohorts(self, sources: Dict[str, Source]) -> Dict[int, List[CohortDefinition]]:
        r: Dict[int, List[CohortDefinition]] = {}

        for cs in self.column_selectors:
            split: List[str] = _explode_fq_column_selectors(cs.name)
            source_pattern = split[0]
            schema_pattern = split[1]
            table_pattern = split[2]
            column_pattern = split[3]

            matching_source_ids = [source.id
                                   for source_name, source in sources.items()
                                   if source_name in wildcard_search(search_string=source_pattern,
                                                                     content=[source_name])
                                   ]

            for id in matching_source_ids:
                cd = CohortDefinition(schema_name_pattern=schema_pattern, table_name_pattern=table_pattern,
                                      column_name_pattern=column_pattern,
                                      entity_type=CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD)
                if id in r.keys():
                    r[id].append(cd)
                else:
                    r[id] = [cd]

        return r


class TagDeployment(YamlModelWithValidatorContext):
    metrics: List[SimpleMetricDefinition]
    tag_id: Optional[str] = None
    column_selectors: Optional[List[ColumnSelector]] = Field(default_factory=lambda: [])

    def explode_fq_column_selectors(self) -> List[List[str]]:
        """
        Explodes a fully qualifeid column selectors into a list of names.  Supports wild cards as *. Supports single and
        double quoted  names containing periods.  Supports fully qulified names with either source.database.schema or
        source.schema convention.

            Example: wh."my.*".some_*_table.* resolves to ['wh', 'my.*', 'some_*_table', '*']

        Returns: list of names from each fully qualified column selector in the Tag Deployment
        """
        return [_explode_fq_column_selectors(i.name) for i in self.column_selectors]

    def to_cohort_and_metric_def(self, sources: Dict[str, Source],
                                 deployment_sla: SimpleSLA = None) -> Dict[int, List[CohortAndMetricDefinition]]:
        """
        Builds a Cohort and MetricDefinition from a TagDeployment object
        Args:
            sources: An index of Sources by Source Name.
            deployment_sla: The sla associated with the deployment.

        Returns: Dict[source_id: int, List[CohortAndMetricDefinition]] matched based on source_id to consolidate to
        a single metric suite object.
        """

        cmds: Dict[int, List[CohortAndMetricDefinition]] = {}
        metrics = []

        for m in self.metrics:
            if deployment_sla.id not in m.sla_ids:
                m.sla_ids.append(deployment_sla.id)
            mdwo = m.to_datawatch_object()
            metrics.append(mdwo)

        for cs in self.explode_fq_column_selectors():
            source_pattern = cs[0]
            schema_pattern = cs[1]
            table_pattern = cs[2]
            column_pattern = cs[3]

            this_cohort = CohortDefinition(schema_name_pattern=schema_pattern, table_name_pattern=table_pattern,
                                           column_name_pattern=column_pattern,
                                           entity_type=CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD)

            matching_source_ids = [source.id
                                   for source_name, source in sources.items()
                                   if source_name in wildcard_search(search_string=source_pattern,
                                                                     content=[source_name])
                                   ]

            if metrics:
                """Only append cohorts if metrics actually exist."""
                for sid in matching_source_ids:
                    """Tag deployments support source patterns.  Each source id becomes a key in the returned dictionary 
                    with the exact same cohorts and metrics."""
                    cmd = CohortAndMetricDefinition(cohorts=[this_cohort], metrics=metrics)
                    if sid in cmds:
                        cmds[sid].append(cmd)
                    else:
                        cmds[sid] = [cmd]

        return cmds


class TagDeploymentSuite(YamlModelWithValidatorContext):
    deployments: List[TagDeployment]
    sla: Optional[SimpleSLA] = None

    @validator('deployments', each_item=True)
    def validate_metric_business_rules(cls, v: TagDeployment):
        for m in v.metrics:
            m.deployment_validations(config_error_lines=v.get_error_lines())

        return v


class ColumnMetricDeployment(YamlModelWithValidatorContext):
    column_name: str
    metrics: List[SimpleMetricDefinition]


class TableDeployment(YamlModelWithValidatorContext):
    fq_table_name: str
    columns: List[ColumnMetricDeployment]
    table_metrics: Optional[List[SimpleMetricDefinition]] = Field(default_factory=lambda: [])
    row_creation_time: Optional[str] = None

    @validator('fq_table_name')
    def fq_table_name_must_not_have_wildcards(cls, v):
        if '*' in v:
            error_message = WILD_CARDS_NOT_SUPPORT_IN_FQ_TABLE_NAMES_ERRMSG.format(fq_table_name=v)
            cls.raise_validation_error(error_lines=[v], error_message=error_message)

        return v

    @validator('fq_table_name')
    def must_have_split_length_3_or_4(cls, v):
        if v == '' or len(v) == 0 or len(_explode_fq_name(v)) not in [3, 4]:
            error_message = FQ_TABLE_NAME_MUST_RESOLVE_TO_TABLE_ERRMSG.format(fq_table_name=v)
            cls.raise_validation_error(error_lines=[v], error_message=error_message)
        return v

    @validator('columns', each_item=True)
    def validate_metric_business_rules_for_columns(cls, v: ColumnMetricDeployment):
        """Document in deployment_validations()"""
        error_config_lines = v.get_error_lines()

        for m in v.metrics:
            m.deployment_validations(error_config_lines)

        return v

    def explode_fq_table_name(self):
        """
        Explodes a fully qualifeid table name into a list of names.  Supports single and double quoted  names
        containing periods.  Supports fully qulified names with either source.database.schema or source.schema
        conventions.  DOES NOT support wild cards.

            Example: wh."my.schema".some_table resolves to ['wh', 'my.schema', 'some_table']

        Returns: list of names from the fully qualified table name
        """

        return _explode_fq_table_name(self.fq_table_name)

    def to_cohort_and_metric_def(self, sources: Dict[str, Source],
                                 deployment_sla: SimpleSLA = None) -> Dict[int, List[CohortAndMetricDefinition]]:
        """
        Builds a Cohort and MetricDefinition from a TableDeployment object
        Args:
            sources: An index of Sources by Source Name.
            deployment_sla: SLA to which metrics will be added.

        Returns: Dict[warehouse_id: int, CohortAndMetricDefinition]
        """

        result: Dict[int, List[CohortAndMetricDefinition]] = {}

        fq_names_list = self.explode_fq_table_name()
        source_name = fq_names_list[0]
        schema_name = fq_names_list[1]
        table_name = fq_names_list[2]

        if source_name in sources:
            sid = sources[source_name].id
        else:
            sid = 0
            error_message = SRC_NOT_EXISTS_FOR_DEPLOYMENT_ERRMSG.format(fq_name=self.fq_table_name)
            self.raise_validation_error(error_context_lines=self.get_error_lines(),
                                        error_lines=[self.fq_table_name],
                                        error_message=error_message)

        cmds: List[CohortAndMetricDefinition] = []

        table_metrics = []
        table_cohort = CohortDefinition(schema_name_pattern=schema_name, table_name_pattern=table_name,
                                        entity_type=CatalogEntityType.CATALOG_ENTITY_TYPE_DATASET)

        for m in self.table_metrics:
            "process table metrics"
            if deployment_sla and deployment_sla.id not in m.sla_ids:
                m.sla_ids.append(deployment_sla.id)
            mdwo = m.to_datawatch_object()
            table_metrics.append(mdwo)

        if table_metrics:
            "Only add the cohort if metrics actually exist for it."
            cmds.append(
                CohortAndMetricDefinition(cohorts=[table_cohort], metrics=table_metrics)
            )

        for c in self.columns:
            "Process Column Metrics"
            cohort = CohortDefinition(schema_name_pattern=schema_name, table_name_pattern=table_name,
                                      column_name_pattern=c.column_name,
                                      entity_type=CatalogEntityType.CATALOG_ENTITY_TYPE_FIELD)
            col_metrics = []

            for m in c.metrics:
                if deployment_sla and deployment_sla.id not in m.sla_ids:
                    m.sla_ids.append(deployment_sla.id)
                mdwo = m.to_datawatch_object()
                col_metrics.append(mdwo)

            if col_metrics:
                "Only add the cohort if metrics actually exist for it."
                cmds.append(
                    CohortAndMetricDefinition(cohorts=[cohort], metrics=col_metrics))

        result[sid] = cmds

        return result


class TableDeploymentSuite(YamlModelWithValidatorContext):
    deployments: List[TableDeployment]
    sla: Optional[SimpleSLA] = None

    @validator('deployments', each_item=True)
    def validate_metric_business_rules_for_table_metrics(cls, v: TableDeployment):
        for m in v.table_metrics:
            m.deployment_validations(config_error_lines=v.get_error_lines())
        return v


class BigConfig(File, type='BIG_CONFIG_FILE'):
    """
    BigConfig is a canonical model used to collate and compile all definition and deployment files maintained by users
    into a single object that can be used to generate a metric suite.  Tag Definitions and Saved Metric Definitions
    are applied -- and validated -- during the __post_init__ phase of instantiating a BigConfig.
    """
    tag_definitions: Optional[List[TagDefinition]] = Field(
        default_factory=lambda: [])  # only one because we must consolidate if creating BigConfig from multiple files.
    row_creation_times: Optional[RowCreationTimes] = None
    saved_metric_definitions: Optional[
        SavedMetricDefinitions] = None  # only one because we must consolidate if creating BigConfig from multiple files.
    tag_deployments: Optional[List[TagDeploymentSuite]] = Field(default_factory=lambda: [])
    table_deployments: Optional[List[TableDeploymentSuite]] = Field(default_factory=lambda: [])

    _tag_ix_: Dict[str, List[ColumnSelector]] = PrivateAttr({})  # Dict[tag_id, List[ColumnSelector]]
    _saved_metric_ix_: Dict[str, SimpleMetricDefinition] = PrivateAttr(
        {})  # Dict[saved_metric_id, SimpleMetricDefinition]

    # _saved_metric_collection_ix_: Dict[str, List, str] = {}  # Dict[saved_metric_collection_id, List[saved_metric_id]] (V1)

    @validator('saved_metric_definitions')
    def each_saved_metric_must_have_id(cls, v: SavedMetricDefinitions):
        """Located here to capture the full configurations lines for error.  Validators can be weird.  Could use
        root_validator in the future."""
        config_error_lines: List[str] = v.get_error_lines()
        for m in v.metrics:
            m.saved_metrics_must_have_id(config_error_lines=config_error_lines)
        return v

    def __init__(self, **data: Any):
        super().__init__(**data)

        log.info('Applying Tags and Saved Metrics.')
        if self.tag_definitions:
            self._tag_ix_ = self._generate_tag_ix(self.tag_definitions)
            apply_result = self._apply_tags(tag_ix=self._tag_ix_, tag_deps=self.tag_deployments,
                                            row_creation_times=self.row_creation_times)
            self.tag_deployments = apply_result[0]
            self.row_creation_times = apply_result[1]
        if self.saved_metric_definitions:
            self._saved_metric_ix_ = self._generate_saved_metric_def_ix(self.saved_metric_definitions)
            apply_result = self._apply_saved_metrics(saved_metric_ix=self._saved_metric_ix_,
                                                     tag_deps=self.tag_deployments,
                                                     table_deps=self.table_deployments)
            self.tag_deployments = apply_result[0]
            self.table_deployments = apply_result[1]

    @classmethod
    def _generate_tag_ix(cls, tag_definitions: List[TagDefinition]) -> Dict[str, List[ColumnSelector]]:
        """
        Generates an index of Column Selectors by Tag ID and validates no duplicates exist and that column selectors
        is not empty.
        Args:
            tag_definitions: List of Tag Definitions from which an Index will be generated.

        Returns: An index of Column Selectors by Tag ID.
        """
        tix: Dict[str, List[ColumnSelector]] = {}
        for td in tag_definitions:
            if td.tag_id in tix:
                error_message = DUPLICATE_TAG_EXISTS_ERRMSG.format(tag_id=td.tag_id)
                cls.raise_validation_error(error_context_lines=td.get_error_lines(),
                                           error_lines=[td.tag_id],
                                           error_message=error_message)

            tix[td.tag_id] = td.column_selectors

        return tix

    @classmethod
    def _generate_saved_metric_def_ix(cls, smd: SavedMetricDefinitions) -> Dict[str, SimpleMetricDefinition]:
        """
        Generates an index of Saved Metric Definitions by Saved Metric ID and validates no duplicates exist and that
        the Metric Definitions defined have at least a `saved_metric_id` and a `metric_type`.
        Args:
            smd: a Saved Metric Definitions object from which the Saved Metric Definitions IX will be generated.

        Returns: An index of Simple Metric Definitions keyed by `saved_metric_id`.

        """
        smdix: Dict[str, SimpleMetricDefinition] = {}
        for m in smd.metrics:
            if m.saved_metric_id in smdix:
                error_message = DUPLICATE_SAVED_METRIC_ID_EXISTS_ERRMSG.format(
                    saved_metric_id=m.saved_metric_id
                )
                cls.raise_validation_error(error_context_lines=smd.get_error_lines(),
                                           error_lines=m.get_error_lines(),
                                           error_message=error_message)

            smdix[m.saved_metric_id] = m

        return smdix

    @classmethod
    def _tag_id_exists_in_ix(cls, tag_id: str, tag_ix: Dict[str, List[ColumnSelector]]) -> bool:
        if tag_id not in tag_ix:
            error_message = TAG_ID_NOT_EXISTS_IN_TAG_DEFINITION_ERRMSG.format(tag_id=tag_id)
            cls.raise_validation_error(error_lines=[tag_id],
                                       error_message=error_message)
            return False
        else:
            return True

    @classmethod
    def _apply_tags(cls, tag_ix: Dict[str, List[ColumnSelector]],
                    tag_deps: List[TagDeploymentSuite],
                    row_creation_times: RowCreationTimes) -> Tuple[List[TagDeploymentSuite], RowCreationTimes]:
        """
        Applies tags by tag id in all tag deployments and row creation times definitinos.  Validates that all tags
        called in deployments exist in the tags definitions.  Validates that column selectors exist after application.
        Args:
            tag_ix: index of column selectors keyed by tag_id
            tag_deps: list of Tag Deployment Suites to which tags will be applied.
            row_creation_times: row creation times to which tags will be applied

        Returns: list of Tag Deployment Suites to which tags have been applied.

        """

        for td in tag_deps:
            for d in td.deployments:
                if d.tag_id and cls._tag_id_exists_in_ix(d.tag_id, tag_ix):
                    tagged_col_selectors = tag_ix.get(d.tag_id, [])
                    d.column_selectors.extend(tagged_col_selectors)
                    d.column_selectors = sorted(list(set(d.column_selectors)))

        for tag_id in row_creation_times.tag_ids:
            if cls._tag_id_exists_in_ix(tag_id, tag_ix):
                row_creation_times.column_selectors.extend(tag_ix[tag_id])

        row_creation_times.column_selectors = sorted(list(set(row_creation_times.column_selectors)))

        return tag_deps, row_creation_times

    @classmethod
    def _validate_and_apply(cls, m: SimpleMetricDefinition,
                            saved_metric_ix: Dict[str, SimpleMetricDefinition]) -> SimpleMetricDefinition:

        def _apply_overrides(saved_smd: SimpleMetricDefinition,
                             override_smd: SimpleMetricDefinition) -> SimpleMetricDefinition:
            for attr in override_smd.__dict__.keys():
                if attr not in ['saved_metric_id', 'metric_type']:
                    setattr(saved_smd, attr, getattr(override_smd, attr))

            return saved_smd

        if not m.saved_metric_id:
            return m

        if m.saved_metric_id not in saved_metric_ix.keys():
            error_message = SAVED_METRIC_ID_NOT_EXISTS_IN_SAVED_METRICS_DEFINITION_ERRMSG.format(
                saved_metric_id=m.saved_metric_id)
            cls.raise_validation_error(error_lines=m.get_error_lines(),
                                       error_message=error_message)
            return m
        else:
            saved = saved_metric_ix[m.saved_metric_id]
            return _apply_overrides(saved, m)

    @classmethod
    def _apply_saved_metrics(cls, saved_metric_ix: Dict[str, SimpleMetricDefinition],
                             tag_deps: List[TagDeploymentSuite],
                             table_deps: List[TableDeploymentSuite]
                             ) -> Tuple[List[TagDeploymentSuite], List[TableDeploymentSuite]]:

        for tag_dep in tag_deps:
            for d in tag_dep.deployments:
                metrics: List[SimpleMetricDefinition] = []
                for m in d.metrics:
                    metrics.append(cls._validate_and_apply(m, saved_metric_ix))
                d.metrics = metrics

        for table_dep in table_deps:
            for d in table_dep.deployments:
                table_metrics: List[SimpleMetricDefinition] = []
                for m in d.table_metrics:
                    table_metrics.append(cls._validate_and_apply(m, saved_metric_ix))
                d.table_metrics = table_metrics

                for c in d.columns:
                    column_metrics: List[SimpleMetricDefinition] = []
                    for m in c.metrics:
                        column_metrics.append(cls._validate_and_apply(m, saved_metric_ix))
                    c.metrics = column_metrics

        return tag_deps, table_deps

    def get_slas(self) -> List[SimpleSLA]:
        slas: List[SimpleSLA] = []

        for d in self.tag_deployments:
            slas.append(d.sla)

        for d in self.table_deployments:
            slas.append(d.sla)

        return slas

    def to_metric_suites(self,
                         sources: Dict[str, Source],
                         deployment_slas: Dict[str, SimpleSLA]) -> List[MetricSuite]:
        """
        Creates a MetricSuite for each source identified in a BigConfig Table or Tag Deployment.
        Args:
            bigconfig: BigConfig from which MetricSuites will be created.
            sources: Complete list of sources for Bigeye workspace
            deployment_slas: Upserted SLAs (must contain ID)

        Returns: List[MetricSuite]
        """
        cmds: Dict[int, List[CohortAndMetricDefinition]] = {}

        rct_cohorts: Dict[int, List[CohortDefinition]] = self.row_creation_times.to_cohorts(sources=sources)

        for tag_d_suite in self.tag_deployments:
            for tag_d in tag_d_suite.deployments:
                """Process all tag deployments into CohortAndMetricDefinitions.  One tag deployment per CMD"""
                r: Dict[int, List[CohortAndMetricDefinition]] = tag_d.to_cohort_and_metric_def(
                    sources=sources,
                    deployment_sla=deployment_slas[tag_d_suite.sla.name]
                )
                for sid, definitions in r.items():
                    """consolidate based on source"""
                    if sid in cmds:
                        cmds[sid].extend(definitions)
                    else:
                        cmds[sid] = definitions

        for table_d_suite in self.table_deployments:
            for table_d in table_d_suite.deployments:
                "Process all table deployments into CohortAndMetricDefinitions. One table deployment per CMD"
                r = table_d.to_cohort_and_metric_def(sources=sources,
                                                     deployment_sla=deployment_slas[table_d_suite.sla.name])
                for sid, definitions in r.items():
                    """consolidate based on sources"""
                    if sid in cmds:
                        cmds[sid].extend(definitions)
                    else:
                        cmds[sid] = definitions

        deployment_metric_suites: Dict[int, MetricSuite] = {
            source_id: MetricSuite(source_id=source_id, definitions=definitions)
            for source_id, definitions in cmds.items()
        }

        metric_suites: List[MetricSuite] = []

        for source_id, metric_suite in deployment_metric_suites.items():
            if source_id in rct_cohorts.keys():
                metric_suite.row_creation_cohorts = rct_cohorts.pop(source_id)

            metric_suites.append(metric_suite)

        for source_id, rcts in rct_cohorts.items():
            metric_suites.append(
                MetricSuite(source_id=source_id, row_creation_cohorts=rcts)
            )

        return metric_suites
