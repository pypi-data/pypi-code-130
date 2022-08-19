from rgtracker.common import *
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar
from redisgears import executeCommand as execute
from redisgears import log


@dataclass
class Page:
    id: str
    url: str = None
    article_id: str = None
    last_visited: str = None
    dimension_key: field(init=False) = None
    dimension_ts_key: field(init=False) = None
    metric_pageviews_key: field(init=False) = None
    metric_unique_device_key: field(init=False) = None
    cms_width: ClassVar[int] = 2000
    cms_depth: ClassVar[int] = 5

    def __post_init__(self):
        if len(self.last_visited.split('_')) > 1:
            self.dimension_key = f'{Type.JSON.value}::{Dimension.PAGE.value}:{self.id}::'
            self.dimension_ts_key = f'::{Dimension.PAGE.value}:{self.id}:{self.last_visited}:'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.PAGE.value}::{self.last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.PAGE.value}:{self.id}:{self.last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ len(last_visited) > 1  \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_unique_device_key}')
        else:
            dt = datetime.fromtimestamp(int(self.last_visited) / 1000) if self.last_visited is not None else None
            rounded_last_visited = int(round_time(dt).timestamp() * 1000)
            self.dimension_key = f'{Type.JSON.value}::{Dimension.PAGE.value}:{self.id}::'
            self.dimension_ts_key = f'::{Dimension.PAGE.value}:{self.id}:{rounded_last_visited}:'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.PAGE.value}::{rounded_last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.PAGE.value}:{self.id}:{rounded_last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ len(last_visited) > 1  \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_unique_device_key}')

    def create(self, website, section):
        execute('SADD', Dimension.PAGE.value, f'{self.id}:{self.url}')
        # log(f'SADD {Dimension.SECTION.value} {self.id}:{self.name}')
        execute('JSON.SET', self.dimension_key, '.', json.dumps({
            'id': self.id,
            'url': self.url,
            'website': {
                'id': website.id,
                'name': website.name
            },
            'section': {
                'id': section.id,
                'name': section.name,
                'levels': section.levels
            },
            'article_id': self.article_id,
            'last_visited': self.last_visited
        }))
        # log(f'JSON.SET {self.dimension_key})
        execute('JSON.ARRAPPEND', section.dimension_key, '$.pages', json.dumps({
            'id': self.id,
            'url': self.url,
            'article_id': self.article_id,
            'last_visited': int(self.last_visited)
        }))
        # log(f'JSON.ARRAPPEND {section.dimension_key} $.sections')
        execute('JSON.ARRAPPEND', website.dimension_key, '$.pages', json.dumps({
            'id': self.id,
            'url': self.url,
            'article_id': self.article_id,
            'last_visited': int(self.last_visited)
        }))
        # log(f'JSON.ARRAPPEND {website.dimension_key} $.sections')

    def create_metrics(self):
        try:
            execute('CMS.INITBYDIM', self.metric_pageviews_key, self.cms_width, self.cms_depth)
            # log(f'CMS.INITBYDIM {self.metric_pageviews_key} {self.cms_width} {self.cms_depth}')
        except Exception:
            # log(f'S-create_metrics: key {self.metric_pageviews_key} already exists')
            pass

    def incr_metrics(self, device_id):
        execute('CMS.INCRBY', self.metric_pageviews_key, self.id, 1)
        # log(f'CMS.INCRBY {self.metric_pageviews_key} {self.id} {1}')
        execute('PFADD', self.metric_unique_device_key, device_id)
        # log(f'PFADD {self.metric_unique_device_key} {device_id}')

    def expire_metrics(self):
        # Todo: put expire in method params
        execute('EXPIRE', self.metric_pageviews_key, 900)
        execute('EXPIRE', self.metric_unique_device_key, 900)

    def is_exists(self):
        x = execute('EXISTS', self.dimension_key)
        # log(f'EXISTS {self.dimension_key} => {x}')
        return x

    def has_metrics(self):
        # Todo: check if all metrics exists?
        x = execute('EXISTS', self.metric_pageviews_key)
        # log(f'EXISTS {self.metric_pageviews_key} => {x}')
        z = execute('EXISTS', self.metric_unique_device_key)
        return x + z

    def update_last_visited(self):
        execute('JSON.SET', self.dimension_key, '.last_visited', self.last_visited)
        # log(f'update_last_visited: JSON.SET {self.dimension_key} .last_visited {self.last_visited}')

    # Fixme: change method name
    def write_metadata(self, stream_names):
        parsed_key = parse_key_name(self.dimension_ts_key)

        execute('XADD', stream_names.get('page_pageviews'), 'MAXLEN', '86400000', '*',
                'dimension', Dimension.PAGE.value,
                'id', self.id,
                'ts', parsed_key.get('ts'),
                'merged_key', self.metric_pageviews_key)
        # tracker_log(f'XADD {stream_names.get("page_pageviews")} * dimension {Dimension.PAGE.value} id {self.id} ts {parsed_key.get("ts")}')
        execute('XADD', stream_names.get('page_unique_devices'), 'MAXLEN', '86400000', '*',
                'dimension', Dimension.PAGE.value,
                'id', self.id,
                'ts', parsed_key.get('ts'),
                'merged_key', self.metric_unique_device_key)

    def send_to_enrich(self):
        execute('XADD', 'ST:ENRICH:P:::', 'MAXLEN', '86400000', '*', 'key', self.dimension_key, 'article_id', self.article_id)


def load_page(website, section, page, device, output_stream_names):
    if page.is_exists() != 1:
        page.create(website, section)
        page.create_metrics()
        page.incr_metrics(device.id)
        page.expire_metrics()
        page.update_last_visited()
        page.write_metadata(stream_names=output_stream_names)
        page.send_to_enrich()
    else:
        if page.has_metrics() < 2:
            page.create_metrics()
            page.incr_metrics(device.id)
            page.expire_metrics()
            page.update_last_visited()
            page.write_metadata(stream_names=output_stream_names)
        else:
            page.incr_metrics(device.id)
            page.update_last_visited()
