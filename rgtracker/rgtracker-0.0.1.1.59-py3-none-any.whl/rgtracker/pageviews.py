from rgtracker.common import *
import math
import pandas as pd
from redisgears import executeCommand as execute
from redisgears import log


def extract(record, dimension):
    return record['value']['dimension'] == dimension


def transform(records, number_of_rotated_keys):
    # log(f'MegaStar - Transform -> {len(records)} {records}')

    df = pd.DataFrame(records)
    df_ts = df.drop_duplicates('ts').sort_values('ts')
    df_id = df.drop_duplicates('id')['id']

    expected_rows = number_of_rotated_keys
    chunks = math.floor(len(df_ts['ts']) / expected_rows + 1)
    i = 0
    j = expected_rows
    results = {
        'id': df_id.values.tolist(),
        'merge': [],
        'reinject': []
    }
    for x in range(chunks):
        df_sliced = df_ts[i:j]
        if df_sliced.shape[0] >= number_of_rotated_keys:
            results.get('merge').append({
                'name': create_key_name(
                    Type.CMS.value,
                    '',
                    df_sliced["dimension"].iloc[0],
                    '',
                    get_ts_df(df_sliced["ts"].iloc[0], df_sliced["ts"]),
                    Metric.PAGEVIEWS.value
                ),
                'keys': [create_key_name(Type.CMS.value, '', row[0], '', row[1], Metric.PAGEVIEWS.value) for row in
                         zip(df_sliced['dimension'], df_sliced['ts'])]
            })
        else:
            [results.get('reinject').append({
                # Todo: create merge key
                'key': create_key_name(
                    Type.CMS.value,
                    '',
                    row[0],
                    '',
                    row[1],
                    Metric.PAGEVIEWS.value
                ),
                'dimension': row[0],
                'ts': row[1]
            }) for row in zip(df_sliced['dimension'], df_sliced['ts'])]

        i += expected_rows
        j += expected_rows

    return results


def load(job_name, records, dimension, write_to_ts, timeseries_name, key_expire_duration_sc, reinject_stream_name,
         output_stream_name):
    def get_ts(ts):
        if len(ts.split('_')) > 1:
            return ts.split("_")[-1]
        else:
            return ts

    capped_stream = get_maxlen_capped_stream(timeseries_name, dimension)

    tracker_log(f'PG - MAXLEN {type(capped_stream)} {capped_stream}')

    for cms_reinject in records.get('reinject'):
        for id in records.get('id'):
            execute('XADD', reinject_stream_name, 'MAXLEN', f'{capped_stream}', '*',
                    'id', id,
                    'dimension', cms_reinject.get('dimension'),
                    'ts', cms_reinject.get('ts'),
                    'merged_key', cms_reinject.get('key'))

    for cms_merge in records.get("merge"):
        if execute('EXISTS', cms_merge.get('name')) != 1:
            execute('CMS.INITBYDIM', cms_merge.get('name'), 2000, 5)
            execute('CMS.MERGE', cms_merge.get('name'), len(cms_merge.get('keys')), *cms_merge.get('keys'))
            tracker_log(f'Merge Pageviews {cms_merge.get("name")}', f'{job_name} ')

            parsed_key_name = parse_key_name(cms_merge.get('name'))

            if write_to_ts:
                for id in records.get('id'):
                    pageviews = execute('CMS.QUERY', cms_merge.get('name'), id)[0]
                    index_name = create_key_name(
                        type=Type.INDEX.value,
                        name='',
                        dimension=dimension,
                        record_id='',
                        ts='',
                        metric='')
                    timeseries_key_name = create_key_name(
                        type=Type.TIMESERIES.value,
                        name=timeseries_name,
                        dimension=dimension,
                        record_id=id,
                        metric=Metric.PAGEVIEWS.value)

                    if dimension == Dimension.WEBSITE.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '3',
                                               'name', 'AS', 'website_name')
                        # tracker_log(f'Get {dimension} infos - {record_infos}', f'{job_name} ')
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get('ts')), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'ts_name', timeseries_name,
                                'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'website_id', id, *record_infos[-1])
                        tracker_log(f'Write to Timeseries {id}->{timeseries_key_name}', f'{job_name} ')
                    elif dimension == Dimension.SECTION.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '5',
                                               'name', 'AS', 'section_name', 'website_id', 'website_name')
                        # tracker_log(f'Get {dimension} infos - {record_infos}', f'{job_name} ')
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'ts_name', timeseries_name,
                                'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'section_id', id, *record_infos[-1])
                        tracker_log(f'Write to Timeseries {id}->{timeseries_key_name}', f'{job_name} ')
                    elif dimension == Dimension.PAGE.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '5',
                                               'website_id', 'website_name', 'section_id', 'section_name', 'article_id')
                        # tracker_log(f'Get {dimension} infos - {record_infos}', f'{job_name} ')
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'ts_name', timeseries_name,
                                'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'page_id', id, *record_infos[-1])
                        tracker_log(f'Write to Timeseries {id}->{timeseries_key_name}', f'{job_name} ')

            for id in records.get('id'):
                execute('XADD', output_stream_name, 'MAXLEN', f'{capped_stream}', '*',
                        'dimension', dimension,
                        'id', id,
                        'ts', parsed_key_name.get('ts'),
                        'merged_key', cms_merge.get('name'))

                tracker_log(f'Write to OutputStream {id}->{output_stream_name}', f'{job_name} ')

            execute('EXPIRE', cms_merge.get('name'), key_expire_duration_sc)
