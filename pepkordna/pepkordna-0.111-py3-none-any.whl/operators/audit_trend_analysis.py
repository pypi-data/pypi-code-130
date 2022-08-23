from pepkordna.operators.audit_base_operator import AuditBaseOperator
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, SupportsAbs, Union, Type
import logging
from inspect import cleandoc

class AuditTrendAnalysis(AuditBaseOperator):
    """
    Does trend analyis checks on source table.

    :param results_table_project_id: 
        Project name where audit results will get logged to. Expect table in dataset named dataops.

    :param bigquery_conn_id: 
        Airflow Bigquery connection id.

    :param source_table:
        Source table to be audited.

    :param measure_cols:
        List of columns names to be aggregated.

    :param partition_col: 
        Column name table is partioned on.

    :param group_by_cols:
        List of column names to group by result set. 
        Do not add partition_col value to parameter `group_by_cols` list. Gets appended by default.

    :param only_where_value_is_zero:
        ONLY check for days where the measure column value is 0 - i.e no data found for that day.

    Examples
    -------- 
    test_aud_trend_analysis = AuditTrendAnalysis(
        task_id='test_aud_trend_analysis',
        results_table_project_id='gcp_project_id',
        bigquery_conn_id='default_conn_id',
        source_table='gcp_project_id.dataset_id.table_name',
        measure_cols=['no_of_sales','no_of_pings','no_of_sim_cls_base'],
        group_by_cols=['_m_network_name'],
        partition_col='_m_snapshot_date'
    )               
    """

    aud_sql = cleandoc("""
    select 
    {struct_cols}
    from(
        select
            {partition_col},
            {case_statements},
            {group_by_cols}
        from (
            select 
                {partition_col},    
                {outer_select_cols},
                {group_by_cols}
            from 
                (select
                    dates.dt {partition_col},
                    {inner_select_cols},
                    {group_by_cols}
                from 
                    (select distinct
                    case
                    when 'MONTHLY' = 'MONTHLY' then last_day(dt)
                    when 'DAILY' = 'DAILY' then dt
                    end dt                    
                    from 
                    unnest(generate_date_array(date_sub(current_date(), INTERVAL 8 MONTH),date_sub(current_date(), interval 1 MONTH))) dt
                    ) dates                
                    left join `{source_table}` a
                    on a._m_snapshot_date = dates.dt            
                    --where {partition_col} > date_sub(current_date(), interval 8 MONTH)
                group by 
                    dates.dt,
                    {group_by_cols}
                )
        ) 
        where 
            {where_clause}
        and 
            {filter_on_zero_values}
        )
    """)

    def __init__(self,
            results_table_project_id: str,
            bigquery_conn_id: str,
            source_table: str,
            measure_cols: List[str],
            group_by_cols: List[str],
            partition_col: str,      
            only_where_value_is_zero: bool = False,            
            delegate_to = None,
            *args,
            **kwargs) -> None:               

        self.delegate_to = delegate_to
        self.results_table_project_id = results_table_project_id
        self.bigquery_conn_id = bigquery_conn_id
        self.source_table = source_table
        self.partition_col = partition_col     
        self.measure_col_list = measure_cols      
        self.measure_col_list_dict = self.convert_measure_col_list_to_dict()
        self.group_by_cols = group_by_cols
        self.group_by_cols_str = ',\n'.join(self.group_by_cols)
        self.short_table_name = self.source_table.split('.')[2]
        self.dataset_id = self.source_table.split('.')[1]
        self.project_id = self.source_table.split('.')[0]

        if len(self.group_by_cols) != len(set(self.group_by_cols)):
            raise ValueError('Duplicate column names found in parameter group_by_cols')

        if len(self.measure_col_list) != len(set(self.measure_col_list)):
            raise ValueError('Duplicate column names found in parameter measure_cols')

        if self.partition_col in self.group_by_cols:
            raise ValueError('Remove partition_col value `{partition_col}` from group_by_cols list.'.format(partition_col=self.partition_col))

        if only_where_value_is_zero == True:
            filter_zero_where_clause = 'values = 0'
        else:
            filter_zero_where_clause = '1=1'
        
        # Construct SQL
        self.aud_sql_fmt = self.aud_sql.format(
            source_table=self.source_table,
            outer_select_cols=self.generate_outer_select_sql(),
            inner_select_cols=self.generate_inner_select_sql(),
            where_clause=self.generate_where_clause_sql(),
            case_statements=self.generate_case_statements_sql(),
            struct_cols=self.generate_struct_sql(),
            partition_col=partition_col,
            group_by_cols=self.group_by_cols_str,
            filter_on_zero_values=filter_zero_where_clause
        )

        print(self.aud_sql_fmt)

        super().__init__(
            results_table_project_id=self.results_table_project_id,
            bigquery_conn_id=self.bigquery_conn_id,     
            delegate_to=self.delegate_to,  
            source_table=self.source_table,                      
            aud_sql=self.aud_sql_fmt,
            *args,
            **kwargs)         

        self.derived_part_freq = self.get_derived_partition_freq()        

        if self.derived_part_freq == 'UNKNOWN':
            raise ValueError('derived_part_freq value of ({partition_frequency}) not supported. Only MONTHLY and DAILY partitioned tables currently supported.'.format(partition_frequency=self.derived_part_freq))                         

    def generate_outer_select_sql(self):
        window_col = 'cast(round(AVG({col_name}) OVER(ORDER BY UNIX_DATE({part_col_name}) RANGE BETWEEN 90 PRECEDING AND 1 PRECEDING)) as numeric) {col_alias}'
        col_alias_prefix = 'rolling_avg_{col_name}'
        all_cols_sql = ''

        for obj in self.measure_col_list_dict:
            col = obj['col_name']
            col_alias = col_alias_prefix.format(col_name=col)
            all_cols_sql += col + ',\n' + window_col.format(col_name=col,part_col_name=self.partition_col,col_alias=col_alias)+',\n'
        all_cols_sql = all_cols_sql.rstrip(',\n')

        return all_cols_sql

    def generate_inner_select_sql(self):
        all_cols_sql = ''

        for obj in self.measure_col_list_dict:
            col = obj['col_name']
            col_type = obj['col_type']

            if col_type == 'bq_agg_func':
                col_agg = 'count(a) {col_name}'
            else:
                col_agg = 'sum({col_name}) {col_name}'

            all_cols_sql += col_agg.format(col_name=col)+',\n'
        all_cols_sql = all_cols_sql.rstrip(',\n')

        return all_cols_sql        

    def generate_where_clause_sql(self):
        sql = '('
        for obj in self.measure_col_list_dict:
            col = obj['col_name']            
            sql += col+' < rolling_avg_'+col+' \n or \n'
        sql = sql.rstrip('or \n')+')'

        return sql

    def generate_case_statements_sql(self):
        sql = ''
        case = cleandoc("""
            {col_name},
            rolling_avg_{col_name},
            case
                when '{col_type}' = 'bq_agg_func' then 'count'
                else 'sum'
            end {col_name}_aggregate_type,                
            case
                when {col_name} < rolling_avg_{col_name} then 'true'
            else 'false'
            end {col_name}_is_less_than_avg,""") 

        for obj in self.measure_col_list_dict:
            col = obj['col_name']   
            col_type = obj['col_type'] 
            sql += case.format(col_name=col,col_type=col_type)
        sql = sql.rstrip(',\n')

        return sql

    def convert_measure_col_list_to_dict(self):
        col_list_dict = []
        for col in self.measure_col_list:
            if col == 'count(*)':
                col_type = 'bq_agg_func'
                col_name = 'record_count'
            else:
                col_type = 'bq_col'
                col_name = col

            col_list_dict.append({'col_name':col_name,'col_type':col_type})   
        
        return col_list_dict 

    def generate_struct_sql(self):
        group_by_cols_str = 'struct('
        for col in self.group_by_cols:
            group_by_cols_str += col + ' as ' + col + ',\n'

        group_by_cols_str = group_by_cols_str.rstrip(',\n')  
        group_by_cols_str += ')'

        sql = ''
        array = cleandoc("""
        array_agg(
            struct(
                '{col_name}' as column_name,
                {partition_col} as partition_col_value,
                [{group_by_cols}] as group_by_cols,
                {col_name} as value,
                rolling_avg_{col_name} as rolling_avg_value,
                {col_name}_is_less_than_avg as value_is_less_than_avg,
                {col_name}_aggregate_type as aggregate_value_type 
        )) {col_name} ,""")

        for obj in self.measure_col_list_dict:
            col = obj['col_name']   
            sql += array.format(partition_col=self.partition_col,col_name=col,group_by_cols=group_by_cols_str)
        sql = sql.rstrip(',\n')      

        return sql    

    def get_derived_partition_freq(self):
        sql = """
        select 
        case
        when MONTHLY > DAILY then 'MONTHLY'
        when DAILY > MONTHLY then 'DAILY'
        else 'UNKNOWN'
        end derived_part_freq
        from (
        select 
        countif(partition_check = 'MONTHLY') MONTHLY,
        countif(partition_check = 'DAILY') DAILY
        FROM 
        (
        SELECT
        case
        when PARSE_DATE('%Y%m%d',partition_id) = last_day(PARSE_DATE('%Y%m%d',concat(substr(partition_id,1,6),'01'))) then
        'MONTHLY'
        else 'DAILY'
        end partition_check  
        from `{project_id}.{dataset_id}.INFORMATION_SCHEMA.PARTITIONS`
        where table_name = '{table_name}'
        and partition_id not in ('__NULL__','__UNPARTITIONED__')
        order by partition_id
        limit 10))        
        """.format(dataset_id=self.dataset_id, table_name=self.short_table_name, project_id=self.project_id)

        results = self._query_bigquery(sql)

        for row in results:
            derived_part_freq = row.derived_part_freq

        return derived_part_freq
