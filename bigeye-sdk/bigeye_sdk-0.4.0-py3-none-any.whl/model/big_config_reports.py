from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, TypeVar, Any

from bigeye_sdk.serializable import DatawatchObject
from pydantic import Field
from pydantic_yaml import YamlStrEnum

from bigeye_sdk.exceptions.exceptions import BigConfigValidationException
from bigeye_sdk.generated.com.torodata.models.generated import MetricSuiteResponse, Source
from bigeye_sdk.serializable import File

BIGCONFIG_REPORT = TypeVar('BIGCONFIG_REPORT', bound='BigConfigReport')

# TODO: Add error stats to API Execution Messages.
FAILED_API_EXECUTION_MSG = '\nBigConfig plan includes errors and report files have been generated.\n' \
                           'Report files: \n{report_file_list}'

SUCCESSFUL_API_EXECUTION_MSG = '\nBigConfig plan executed successfully and report files have been generated.\n' \
                               'Report files: \n{report_file_list}'

FILES_CONTAIN_ERRORS_EXCEPTION_STATEMENT = '\nBigConfig plan includes errors and FIXME files have been generated.\n' \
                                           'Number of Errors: {err_cnt}\n' \
                                           'FIXME files: \n{fixme_file_list}'

REPORTS: List[BIGCONFIG_REPORT] = []


def process_reports(output_path: str, sources_ix: Dict[int, Source]):
    report_files = []
    errors_reported = False

    for report in REPORTS:
        file_name = f'{output_path}/{sources_ix[report.source_id].name}_{report.process_stage}.yml'
        report.save(file_name)
        report_files.append(file_name)
        errors_reported = errors_reported or report.has_errors()

    if errors_reported:
        raise BigConfigValidationException(
            FAILED_API_EXECUTION_MSG.format(report_file_list=report_files)
        )
    else:
        print(
            SUCCESSFUL_API_EXECUTION_MSG.format(report_file_list=report_files)
        )


class BigConfigReport(File, ABC):
    @classmethod
    @abstractmethod
    def from_datawatch_object(cls, obj: DatawatchObject, source_id: int,
                              process_stage: ProcessStage) -> BIGCONFIG_REPORT:
        pass

    @abstractmethod
    def tot_error_count(self) -> int:
        """returns a total error count for this report."""
        pass

    def has_errors(self):
        return self.tot_error_count() > 0

    # TODO
    # @abstractmethod
    # def get_stats(self) -> str:
    #     """Returns string formatted stats for this report."""
    #     pass


def raise_files_contain_error_exception(err_cnt: int, fixme_file_list: List[str]):
    raise BigConfigValidationException(FILES_CONTAIN_ERRORS_EXCEPTION_STATEMENT.format(
        err_cnt=str(err_cnt),
        fixme_file_list=", \n".join(fixme_file_list)
    ))


class ProcessStage(YamlStrEnum):
    APPLY = 'APPLY'
    PLAN = 'PLAN'


class MetricSuiteReport(BigConfigReport, type='BIG_CONFIG_REPORT'):
    type = 'BIG_CONFIG_REPORT'
    process_stage: ProcessStage
    source_id: int

    created_metric_count: int = 0
    updated_metric_count: int = 0
    deleted_metric_count: int = 0

    total_error_count: int = 0

    row_creation_time_upserted_count: int = 0
    row_creation_time_upsert_failure_count: int = 0
    invalid_row_creation_time_column_type_count: int = 0
    invalid_row_creation_time_column_count: int = 0
    tables_with_multiple_row_creation_times_count: int = 0

    columns_set_as_row_creation_time: List[int] = Field(default_factory=lambda: [])
    columns_having_invalid_column_type: List[int] = Field(default_factory=lambda: [])
    columns_having_invalid_column_identifier: List[int] = Field(default_factory=lambda: [])
    tables_having_multiple_specified_columns: List[dict] = Field(default_factory=lambda: [])
    row_creation_time_upsert_failures: List[dict] = Field(default_factory=lambda: [])

    created_metrics: List[dict] = Field(default_factory=lambda: [])
    updated_metrics: List[dict] = Field(default_factory=lambda: [])
    deleted_metrics: List[dict] = Field(default_factory=lambda: [])

    def tot_error_count(self) -> int:
        return self.total_error_count

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.created_metric_count = len(self.created_metrics)
        self.updated_metric_count = len(self.updated_metrics)
        self.deleted_metric_count = len(self.deleted_metrics)
        self.row_creation_time_upserted_count = len(self.columns_set_as_row_creation_time)
        self.row_creation_time_upsert_failure_count = len(self.row_creation_time_upsert_failures)
        self.invalid_row_creation_time_column_type_count = len(self.columns_having_invalid_column_type)
        self.invalid_row_creation_time_column_count = len(self.columns_having_invalid_column_identifier)
        self.tables_with_multiple_row_creation_times_count = len(self.tables_having_multiple_specified_columns)

        self.total_error_count = self.row_creation_time_upserted_count + \
                                 self.row_creation_time_upsert_failure_count + \
                                 self.invalid_row_creation_time_column_type_count + \
                                 self.invalid_row_creation_time_column_count + \
                                 self.tables_with_multiple_row_creation_times_count

        REPORTS.append(self)

    @classmethod
    def from_datawatch_object(cls, obj: MetricSuiteResponse, source_id: int,
                              process_stage: ProcessStage) -> MetricSuiteReport:
        pr = MetricSuiteReport(
            process_stage=process_stage,
            source_id=source_id,
            created_metrics=[i.to_dict() for i in obj.created_metrics],
            updated_metrics=[i.to_dict() for i in obj.updated_metrics],
            deleted_metrics=[i.to_dict() for i in obj.deleted_metrics],
            columns_set_as_row_creation_time=obj.row_creation_time_response.column_ids_set_as_metric_time,
            columns_having_invalid_column_type=obj.row_creation_time_response.column_ids_not_valid_metric_time,
            columns_having_invalid_column_identifier=obj.row_creation_time_response.cohort_matches_actually_table_ids,
            tables_having_multiple_specified_columns=
            [i.to_dict() for i in obj.row_creation_time_response.table_ids_with_multiple_specified_columns],
            row_creation_time_upsert_failures=
            [i.to_dict() for i in obj.row_creation_time_response.column_ids_failed_to_set_as_metric_time]
        )

        return pr
