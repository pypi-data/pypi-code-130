from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from google.cloud import bigquery
import json
import logging

class AuditBaseOperator(BaseOperator):
    """
    Base class for DNA custom audit operators.
    """

    template_fields = ['sql']
    ui_color = '#33adff'

    sql_formatted = """
    select 
    TO_JSON_STRING(a) json
        from (
        {inner_sql}
    ) a    
    """

    @apply_defaults
    def __init__(
            self,
            results_table_project_id,
            bigquery_conn_id,   
            aud_sql, 
            source_table,            
            delegate_to=None,
            *args,
            **kwargs):

        super().__init__(*args, **kwargs)      

        self.results_table_project_id = results_table_project_id
        self.bigquery_conn_id = bigquery_conn_id
        self.delegate_to = delegate_to
        self.aud_sql = aud_sql
        self.source_table = source_table        
        self.cls_name = self.__class__.__name__
        self.sql = self.sql_formatted.format(inner_sql=aud_sql)   

        print('Audit SQL --->'+self.aud_sql)
        print('Final SQL --->'+self.sql)                

    def execute(self, context):
        """
        Get BQ results and log to audit table
        """

        job_results = self._query_bigquery(self.sql)

        all_rows = []
        json_rows_out = {}
        for row in job_results:
            all_rows.append(json.loads(row['json']))

        json_rows_out['data'] = all_rows

        # Log audit results
        self._query_bigquery(self.log_to_audit_table_sql(json_rows_out))

    def _query_bigquery(self,sql):
        """
        Execute query against BQ
        """

        hook = BigQueryHook(bigquery_conn_id=self.bigquery_conn_id, delegate_to=None, use_legacy_sql=False)     
        client = bigquery.Client(project=hook._get_field("project"), credentials=hook._get_credentials())
        query_job = client.query(sql).result()

        return query_job

    def log_to_audit_table_sql(self,audit_results):
        sql = """
        insert into `{results_table_project_id}.dataops.audit_smart_alert`
        (
          audit_type,
          audit_timestamp,
          audit_date,
          audit_results,
          audit_table_name,
          audit_dataset,
          audit_project_id
        )
        values
        (
          '{audit_type}',
          current_timestamp(),
          current_date(),
          '''{audit_results}''',
          '{audit_table_name}',
          '{audit_dataset}',
          '{audit_project_id}'
        )
        """.format(
            results_table_project_id=self.results_table_project_id,
            audit_type=self.cls_name,
            audit_results=audit_results,
            audit_table_name=self.source_table.split('.')[2],
            audit_dataset=self.source_table.split('.')[1],
            audit_project_id=self.source_table.split('.')[0]
        )

        return sql
