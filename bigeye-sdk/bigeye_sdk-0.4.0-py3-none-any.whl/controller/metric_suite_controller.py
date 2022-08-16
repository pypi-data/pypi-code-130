from pathlib import Path
from typing import List, TypeVar, Dict

from bigeye_sdk.generated.com.torodata.models.generated import Source, CohortDefinition

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.exceptions.exceptions import FileLoadException, BigConfigValidationException
from bigeye_sdk.model.big_config import BigConfig
from bigeye_sdk.model.big_config_reports import raise_files_contain_error_exception, MetricSuiteReport, \
    process_reports, ProcessStage
from bigeye_sdk.model.protobuf_message_facade import SimpleSLA
from bigeye_sdk.serializable import File
from bigeye_sdk.yaml_validation.validation_context import get_validation_errors, process_validation_errors

BIGCONFIG_FILE = TypeVar('BIGCONFIG_FILE', bound='File')


def get_fq_name_from_cohort(cohort: CohortDefinition, source_name: str = None):
    """
    Args:
        cohort: cohort for which to get fully_qualified_name
        source_name: (optional) if available will prepend source name.

    Returns: fully qualified name
    """
    if cohort.column_name_pattern:
        r = f'{cohort.schema_name_pattern}.{cohort.table_name_pattern}.{cohort.column_name_pattern}'
    else:
        r = f'{cohort.schema_name_pattern}.{cohort.table_name_pattern}'

    if not source_name:
        return r
    else:
        return f'{source_name}.{r}'


def _find_bigconfig_files(source_path: str = None) -> List[BIGCONFIG_FILE]:
    """
    Finds bigconfig files either in specified source path or in working directory
    Args:
        source_path: specify a source path or working directory will be used.

    Returns: None

    """
    files: List[Path]
    if source_path:
        files = list(Path(source_path).glob('*.y*ml'))
    else:
        """Assumes driver run in directory containing BigConfig YAML."""
        files = list(Path.cwd().glob('*.y*ml'))

    bigeye_files: List[BIGCONFIG_FILE] = []
    file: BIGCONFIG_FILE
    for file in files:
        try:
            """Loading BigConfig YAML.  If file is not of BigConfig type then the error will be caught and passed."""
            bigeye_files.append(File.load(str(file)))
        except FileLoadException:
            pass

    return bigeye_files


def _upsert_slas(client: DatawatchClient, bigconfig: BigConfig) -> List[SimpleSLA]:
    existing_slas = {sla.name: sla for sla in client.get_collections().collections}
    deployment_slas = []

    for sla in bigconfig.get_slas():
        if sla.name in existing_slas.keys():
            existing = SimpleSLA.from_datawatch_object(existing_slas[sla.name])
            merged = sla.merge_for_upsert(existing=existing)
            deployment_slas.append(merged)
            client.update_collection(collection=merged.to_datawatch_object())
        else:
            c = sla.to_datawatch_object()
            c = client.create_collection(
                collection_name=c.name,
                description=c.description,
                metric_ids=c.metric_ids,
                notification_channels=c.notification_channels,
                muted_until_timestamp=c.muted_until_timestamp
            ).collection
            deployment_slas.append(SimpleSLA.from_datawatch_object(c))

    return deployment_slas


def execute_bigconfig(client: DatawatchClient, input_path: str = None,
                      output_path: str = None, apply: bool = False):
    """
    Executes an Apply or Plan for a Big Config.
    Args:
        client: Datawatch Client
        input_path: path of source files.  If no path is given the current working directory will be used.
        output_path: path where reports will be placed.
        apply: If true then Big Config will be applied to the workspace.  If false then a plan will be generated.

    Returns: None

    """

    if not input_path:
        input_path = Path.cwd()

    if not output_path:
        output_path = Path.cwd()
    files: List[BIGCONFIG_FILE] = _find_bigconfig_files(input_path)

    if len(files) > 1 or files[0].type != 'BIG_CONFIG_FILE':
        raise BigConfigValidationException(f'Multiple files not currently supported.')
    else:
        bigconfig: BigConfig = files[0]

    ves = get_validation_errors()

    if ves:
        """Processing validation errors if any exist and throw exception."""
        fixme_file_list = process_validation_errors(output_path)
        raise_files_contain_error_exception(err_cnt=len(ves), fixme_file_list=fixme_file_list)

    sources_by_name_ix: Dict[str, Source] = client.get_sources_by_name()
    sources_by_id_ix: Dict[int, Source] = {v.id: v for k, v in sources_by_name_ix.items()}

    deployment_slas = {sla.name: sla for sla in _upsert_slas(client, bigconfig)}

    metric_suites = bigconfig.to_metric_suites(sources=sources_by_name_ix,
                                               deployment_slas=deployment_slas)

    for metric_suite in metric_suites:
        j = metric_suite.to_json()
        print(j)
        response = client.post_metric_suite(metric_suite=metric_suite, apply=apply)
        process_stage = ProcessStage.APPLY if apply else ProcessStage.PLAN
        MetricSuiteReport.from_datawatch_object(response, source_id=metric_suite.source_id, process_stage=process_stage)

    process_reports(output_path=output_path, sources_ix=sources_by_id_ix)
