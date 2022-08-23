import re
from collections.abc import Iterable
from datetime import datetime, date
from enum import Enum
from itertools import zip_longest
from typing import Union

import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from speedtab.enums import MergeType, BorderStyle, HorizontalAlignment, VerticalAlignment, WrapStrategy, ShareRole, \
    ChartType, StackedType, LegendPosition, AxisPosition
from speedtab.formats import Color, Border, Number, BaseNumberFormat

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
BORDER_SIDES = ('top', 'bottom', 'left', 'right', 'innerHorizontal', 'innerVertical')
SHIFT_DIM = {
    'startRowIndex': 0,
    'startColumnIndex': 0,
    'endRowIndex': 1,
    'endColumnIndex': 1,
}

TYPE_ORDER = {b: i for b, i in zip(('clear', 'format', 'chart', 'data'), (0, 0, 0, 1))}

DIMENSION = {
    'ROWS': 'ROWS',
    'COLUMNS': 'COLUMNS',
    0: 'ROWS',
    1: 'COLUMNS'
}


def create_token(input_cred: str = 'creds.json', output_token: str = 'token.json'):
    flow = InstalledAppFlow.from_client_secrets_file(input_cred, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(output_token, 'w') as token:
        token.write(creds.to_json())


def col_num_to_string(n, start_from_0=True):
    string = ''
    if not isinstance(n, int):
        return string
    n += int(start_from_0)
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def num_to_string(n):
    if isinstance(n, int):
        return str(n + 1)
    else:
        return ''


def get_col_num(col):
    n = 0
    for position, character in zip(range(len(col) - 1, -1, -1), col):
        n += 26 ** position * (ord(character) - 64)
    return n - 1


def sheet_cell_to_index(cell):
    letter = re.search(r'[A-Z]+', cell)
    num = re.search(r'[0-9]+', cell)
    return int(num.group()) - 1 if num else num, get_col_num(letter.group()) if letter else letter


def datetime_to_xls(input_date):
    if isinstance(input_date, datetime):
        return (input_date - datetime(1899, 12, 30)).total_seconds() / 86400
    elif isinstance(input_date, date):
        return (input_date - date(1899, 12, 30)).days
    else:
        return input_date


def apply(iterable, f):
    if isinstance(iterable, list):
        return [apply(w, f) for w in iterable]
    else:
        return f(iterable)


def parse_range(input_range):
    if isinstance(input_range, str):
        input_range = input_range.split(':') + [''] if len(input_range.split(':')) == 1 else input_range.split(':')
        cells = sum(tuple(sheet_cell_to_index(x) for x in input_range), ())
    else:
        cells = input_range + (None,)*4
    return cells

depth = lambda l: isinstance(l, list) and max(map(depth, l)) + 1


class Task:
    def __init__(self, task_type, position, sheetId, task, data_cell=None):
        self.task_type = task_type
        self.position = position
        self.sheetId = sheetId
        self.task = task
        self.data_cell = data_cell


class SpreedSheet:
    def __init__(self, spreadsheet_id, token_path, credentials, connect):
        self.spreadsheet_id = spreadsheet_id
        self.token_path = token_path
        self.credentials = credentials
        self.connect = connect
        self._get_metadata()
        self._task_queue = []

    def _regroup_tasks(self):
        groups = []
        for id in [x.get('sheetId') for x in self.sheets.values()]:
            current_id_tasks = [x for x in self._task_queue if x.sheetId == id]
            clear_ids = [0] + [i for i, x in enumerate(current_id_tasks) if x.task_type == 'clear']
            groups_ids = clear_ids[:1] + [clear_ids[i] for i in range(1, len(clear_ids))
                              if clear_ids[i] - clear_ids[i - 1] > 1] + [len(current_id_tasks)]

            merged_group = []
            shift = []
            for elem in [current_id_tasks[i:j] for i, j in [groups_ids[i:i + 2] for i in range(0, len(groups_ids) - 1, 1)]]:
                if not any(d.task_type == 'data' for d in elem):
                    shift += elem
                else:
                    merged_group.append(elem + shift)
                    shift = []
            if shift:
                merged_group.append(shift)

            groups.append(merged_group)

        full_groups = [sorted(sum(x, []), key=lambda x: (TYPE_ORDER[x.task_type], x.position)) for x in zip_longest(*groups, fillvalue=[])]
        curr_size = {}
        for sheet in self.sheets.values():
            curr_size[sheet.get('sheetId')] = [sheet.get('max_row'), sheet.get('max_column')]

        for group in full_groups:
            for task in group:
                if task.task_type == 'clear' and 'updateSheetProperties' in task.task.keys():
                    vals = task.task.get('updateSheetProperties').get('properties').get('gridProperties')
                    curr_size[task.sheetId] = [vals.get('rowCount'), vals.get('columnCount')]
                elif task.task_type == 'clear' and 'appendDimension' in task.task.keys():
                    vals = task.task.get('appendDimension')
                    if vals.get('dimension') == 'ROWS':
                        curr_size[task.sheetId][0] += vals.get('length')
                    if vals.get('dimension') == 'COLUMNS':
                        curr_size[task.sheetId][1] += vals.get('length')
                elif task.task_type == 'data':
                    curr_size[task.sheetId] = [max(curr_size[task.sheetId][0], task.data_cell[0]),
                                               max(curr_size[task.sheetId][1], task.data_cell[1])]
            for key, (rows, columns) in curr_size.items():
                self._set_sheet_size(rows, columns, key, group)

        return [sorted(group, key=lambda x: (TYPE_ORDER[x.task_type], x.position)) for group in full_groups]

    def _set_sheet_size(self, rows: int, columns: int, sheet_id, group):
        group.append(Task('format', len(self._task_queue), sheet_id, {
            'updateSheetProperties': {
                'properties': {
                    'gridProperties': {
                        'rowCount': rows,
                        'columnCount': columns,
                    },
                    'sheetId': sheet_id,
                },
                'fields': 'gridProperties',
            }}))

    def _get_metadata(self):
        metadata = self.connect.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        self.sheets = dict(
            [(prop.get('title'), {
                'max_column': prop.get('gridProperties').get('columnCount'),
                'max_row': prop.get('gridProperties').get('rowCount'),
                'sheetId': prop.get('sheetId'),
                'position': prop.get('index'),
            }) for prop in [sheet.get('properties') for sheet in metadata.get('sheets')]]
        )

    def sheets_list(self):
        return list(self.sheets.keys())

    def exec(self):
        batch_update_chart_list = []
        for group in self._regroup_tasks():
            batch_update_data_list = []
            batch_update_list = []
            for task in group:
                if task.task_type == 'data':
                    batch_update_data_list.append(task.task)
                elif task.task_type == 'chart':
                    batch_update_chart_list.append(task.task)
                else:
                    batch_update_list.append(task.task)
            if batch_update_list:
                self.connect.spreadsheets().batchUpdate(**{
                    'spreadsheetId': self.spreadsheet_id,
                    'body': {
                        'requests': batch_update_list
                    }}).execute()

            if batch_update_data_list:
                self.connect.spreadsheets().values().batchUpdate(**{
                    'spreadsheetId': self.spreadsheet_id,
                    'body': {
                        'valueInputOption': 'RAW',
                        'data': batch_update_data_list,
                    }}).execute()
        if batch_update_chart_list:
            self.connect.spreadsheets().batchUpdate(**{
                'spreadsheetId': self.spreadsheet_id,
                'body': {
                    'requests': batch_update_chart_list
                }}).execute()

    def add_sheets(self, sheets):
        self.connect.spreadsheets().batchUpdate(**{
            'spreadsheetId': self.spreadsheet_id,
            'body': {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 100,
                            }}}} for title in sheets]
            }}).execute()
        self._get_metadata()
        return self

    def delete_sheets(self, sheets):
        for sheet in sheets:
            self._task_queue.append(Task('format', len(self._task_queue), self.sheets.get(sheet).get('sheetId'), {
                'deleteSheet': {
                    'sheetId': self.sheets.get(sheet).get('sheetId')}}))
        return self

    def sheet(self, sheet_name):
        return Sheet(sheet_name, self.sheets.get(sheet_name).get('sheetId'), self._task_queue, self.sheets, self)


class Range:
    def __init__(self, sheet_id, _task_queue, work_zone, start_data_index, start_data_cell, base, data_cell):
        self.sheet_id = sheet_id
        self._task_queue = _task_queue
        self.work_zone = work_zone
        self.start_data_index = start_data_index
        self.start_data_cell = start_data_cell
        self.base = base
        self.data_cell = data_cell

    def _increment_task(self):
        return len(self._task_queue)

    def merge_cells(self, merge_type: MergeType = MergeType.MERGE_ALL):
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'mergeCells': {
                    'mergeType': merge_type.value,
                    'range': self.work_zone
                }}))
        return self

    def delete_axis(self, axis: Union[str, int] = 1):
        axis = axis.upper() if isinstance(axis, str) else DIMENSION.get(axis)
        self._task_queue.append(Task('clear', self._increment_task(), self.sheet_id, {
                'deleteDimension': {
                    'range': {
                        'sheetId': self.sheet_id,
                        'dimension': axis,
                        'startIndex': self.work_zone.get('startRowIndex') if axis == 'ROWS' else self.work_zone.get('startColumnIndex'),
                        'endIndex': self.work_zone.get('endRowIndex') if axis == 'ROWS' else self.work_zone.get('endColumnIndex')
                    }}}))

        return self

    def write_range(self, values, axis: Union[str, int] = 0):
        values = list(values) if not isinstance(values, list) else values
        while depth(values) < 2:
            values = [values]
        values = apply(values, datetime_to_xls)
        self._task_queue.append(Task('data', self._increment_task(), self.sheet_id, {
                'range': self.start_data_cell,
                'values': values,
                'majorDimension': DIMENSION.get(axis.upper() if isinstance(axis, str) else axis),
              }, self.start_data_index))

        return self

    def write_dataframe(self, df: pd.DataFrame, header=True, index=True):
        df = df.applymap(datetime_to_xls).where(pd.notnull(df), None)
        df = df.reset_index() if index else df

        if header:
            if isinstance(df.columns, pd.MultiIndex):
                values = [[str(elem) for elem in level] for level in list(zip(*df.columns.to_list()))] + df.values.tolist()
            else:
                values = [[str(elem) for elem in df.columns.to_list()]] + df.values.tolist()
        else:
            values = df.values.tolist()

        self._task_queue.append(Task('data', self._increment_task(), self.sheet_id, {
                'range': self.start_data_cell,
                'values': values,
                'majorDimension': 'ROWS',
        }, self.start_data_index))
        return self

    def read_range(self):
        return (self.base._connect().spreadsheets().values()
                .get(spreadsheetId=self.sheet_id,
                     range=self.data_cell,
                     valueRenderOption='UNFORMATTED_VALUE').execute()
                .get('values', []))

    def read_dataframe(self):
        rows = self.read_range()
        return pd.DataFrame(data=rows[1:], columns=rows[0])

    def clear(self, values=True, formats=True):
        field = None
        if values and formats:
            field = '*'
        elif formats:
            field = 'userEnteredFormat'
        elif values:
            field = 'userEnteredValue'

        self._task_queue.append(Task('clear', self._increment_task(), self.sheet_id, {
                'updateCells': {
                    'range': self.work_zone,
                    'fields': field,
                }}))

        return self

    def set_sheet_size(self, rows: int, columns: int):
        self._task_queue.append(Task('clear', self._increment_task(), self.sheet_id, {
                'updateSheetProperties': {
                    'properties': {
                        'gridProperties': {
                            'rowCount': rows,
                            'columnCount': columns,
                        },
                        'sheetId': self.sheet_id,
                    },
                    'fields': 'gridProperties',
                }}))

        return self

    def extend_sheet(self, rows: int = None, cols: int = None):
        if cols:
            self._task_queue.append(Task('clear', self._increment_task(), self.sheet_id, {
                'appendDimension': {
                    'sheetId': self.sheet_id,
                    'dimension': 'COLUMNS',
                    'length': cols,
                }}))
        if rows:
            self._task_queue.append(Task('clear', self._increment_task(), self.sheet_id, {
                'appendDimension': {
                    'sheetId': self.sheet_id,
                    'dimension': 'ROWS',
                    'length': rows,
                }}))

        return self

    def unmerge_cells(self):
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'unmergeCells': {
                    'range': self.work_zone,
                }}))
        return self

    def auto_size(self, axis: Union[str, int] = 1):
        axis = axis.upper() if isinstance(axis, str) else DIMENSION.get(axis)
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': self.sheet_id,
                        'dimension': axis,
                        'startIndex': self.work_zone.get('startRowIndex') if axis == 'ROWS' else self.work_zone.get('startColumnIndex'),
                        'endIndex': self.work_zone.get('endRowIndex') if axis == 'ROWS' else self.work_zone.get('endColumnIndex')
                    }}}))
        return self

    def add_chart(self, columns,
                  target_axis: AxisPosition = AxisPosition.LEFT_AXIS,
                  index_column: int = 0,
                  chart_type: ChartType = ChartType.LINE,
                  stacked_type: StackedType = StackedType.NONE,
                  title: str = None,
                  legend_position: LegendPosition = LegendPosition.BOTTOM_LEGEND,
                  x_axis_name: str = None,
                  y_left_axis_name: str = None,
                  y_right_axis_name: str = None,
                  y_left_axis_min: float = None,
                  y_right_axis_min: float = None,
                  y_left_axis_max: float = None,
                  y_right_axis_max: float = None,
                  x_scale: int = 1,
                  y_scale: int = 1,
                  offset_x_pixels: int = 0,
                  offset_y_pixels: int = 0,
                  header_count: int = 1,
                  data_start: tuple = (0, 0),
                  last_row: int = None):

        data_start_cell = parse_range(data_start)
        target_axis = [target_axis] if not isinstance(target_axis, Iterable) else target_axis
        series = [{
            'series': {
                'sourceRange': {
                    'sources': [
                        {
                            'sheetId': self.sheet_id,
                            'startRowIndex': data_start_cell[0],
                            'endRowIndex': last_row if last_row is not None else None,
                            'startColumnIndex': data_start_cell[1] + column,
                            'endColumnIndex': data_start_cell[1] + column + 1,
                        }
                    ]
                }
            },
            'targetAxis': axis.value
        } for column, axis in zip_longest(columns, target_axis, fillvalue=target_axis[0])]

        self._task_queue.append(Task('chart', self._increment_task(), self.sheet_id, {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': title,
                        'basicChart': {
                            'chartType': chart_type.value,
                            'stackedType': stacked_type.value,
                            'legendPosition': legend_position.value,
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': x_axis_name,
                                },
                                {
                                    'position': AxisPosition.LEFT_AXIS.value,
                                    'title': y_left_axis_name,
                                    'viewWindowOptions': {
                                        'viewWindowMode': 'EXPLICIT',
                                        'viewWindowMin': y_left_axis_min,
                                        'viewWindowMax': y_left_axis_max,
                                    },
                                },
                                {
                                    'position': AxisPosition.RIGHT_AXIS.value,
                                    'title': y_right_axis_name,
                                    'viewWindowOptions': {
                                        'viewWindowMode': 'EXPLICIT',
                                        'viewWindowMin': y_right_axis_min,
                                        'viewWindowMax': y_right_axis_max,
                                    },
                                },
                            ],
                            'domains': [
                                {
                                    'domain': {
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': self.sheet_id,
                                                    'startRowIndex': data_start_cell[0],
                                                    'endRowIndex': last_row if last_row is not None else None,
                                                    'startColumnIndex': data_start_cell[1] + index_column,
                                                    'endColumnIndex': data_start_cell[1] + index_column + 1,
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            'series': [*series],
                            'headerCount': header_count,
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {
                                'sheetId': self.sheet_id,
                                'rowIndex': self.work_zone.get('startRowIndex'),
                                'columnIndex': self.work_zone.get('startColumnIndex'),
                            },
                            'offsetXPixels': offset_x_pixels,
                            'offsetYPixels': offset_y_pixels,
                            'widthPixels': 800 * x_scale,
                            'heightPixels': 400 * y_scale,
                        }
                    }}}}))

        return self

    def set_size(self, size: int = None, axis: Union[str, int] = 1):
        axis = axis.upper() if isinstance(axis, str) else DIMENSION.get(axis)
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': self.sheet_id,
                        'dimension': axis,
                        'startIndex': self.work_zone.get('startRowIndex') if axis == 'ROWS' else self.work_zone.get('startColumnIndex'),
                        'endIndex': self.work_zone.get('endRowIndex') if axis == 'ROWS' else self.work_zone.get('endColumnIndex'),
                    },
                    'properties': {
                        'pixelSize': size,
                    },
                    'fields': 'pixelSize',
                }}))
        return self

    def set_num_format(self, default_format: BaseNumberFormat = Number):
        default_format = default_format.value if isinstance(default_format, Enum) else default_format
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'repeatCell': {
                    'range': self.work_zone,
                    **default_format.__dict__,
                }}))
        return self

    def set_text_format(self, horizontal_alignment: HorizontalAlignment = None,
                        vertical_alignment: VerticalAlignment = None,
                        wrap_strategy: WrapStrategy = None,
                        font_size: int = None,
                        bold: bool = None,
                        italic: bool = None,
                        strikethrough: bool = None,
                        underline: bool = None,
                        font_family: str = None,
                        text_color: Color = None):
        """
        Function to set cell text format for Google Sheet
        :param horizontal_alignment: 'LEFT', 'CENTER', 'RIGHT'
        :param vertical_alignment: 'TOP', 'MIDDLE', 'BOTTOM'
        :param wrap_strategy: 'OVERFLOW_CELL', 'LEGACY_WRAP', 'CLIP', 'WRAP'
        :param font_size: font size
        :param bold: True or False
        :param italic: True or False
        :param strikethrough: True or False
        :param underline: True or False
        :param font_family: font family
        :param text_color: foreground color of the text in rgb format
        """
        text_color = text_color.value if isinstance(text_color, Enum) else text_color
        list_of_inputs = ', '.join(
            [f'textFormat.{s}' for s, x in
             zip(('fontFamily', 'fontSize', 'bold', 'italic', 'strikethrough', 'underline', 'foregroundColor'),
                 (font_family, font_size, bold, italic, strikethrough, underline, text_color)) if x is not None]
            + [s for s, x in zip(('horizontalAlignment', 'verticalAlignment', 'wrapStrategy'),
                                 (horizontal_alignment, vertical_alignment, wrap_strategy)) if x is not None])

        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'repeatCell': {
                    'range': self.work_zone,
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': horizontal_alignment.value if horizontal_alignment is not None else None,
                            'verticalAlignment': vertical_alignment.value if vertical_alignment is not None else None,
                            'wrapStrategy': wrap_strategy.value if wrap_strategy is not None else None,
                            'textFormat': {
                                'foregroundColor': text_color.color if text_color is not None else None,
                                'fontFamily': font_family,
                                'fontSize': font_size,
                                'bold': bold,
                                'italic': italic,
                                'strikethrough': strikethrough,
                                'underline': underline,
                            }}},
                    'fields': f'userEnteredFormat({list_of_inputs})',
                }}))
        return self

    def set_borders(self, border_style: BorderStyle = BorderStyle.SOLID,
                    border_width: int = 1,
                    color: Color = Color((0, 0, 0)),
                    border_sides: list = BORDER_SIDES,
                    ):
        color = color.value if isinstance(color, Enum) else color
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'updateBorders': {
                    'range': self.work_zone,
                    **dict((x, Border(border_style, border_width, color).__dict__) for x in border_sides),
                }}))
        return self

    def set_background_color(self, color: Color = Color((255, 255, 255))):
        color = color.value if isinstance(color, Enum) else color
        self._task_queue.append(Task('format', self._increment_task(), self.sheet_id, {
                'repeatCell': {
                    'range': self.work_zone,
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': color.color
                        }},
                    'fields': 'userEnteredFormat(backgroundColor)',
                }}))
        return self


class Sheet(Range):
    def __init__(self, sheet_name, sheet_id, task_query, sheets, base, cells=(0, 0, None, None)):
        self.base = base
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self._task_queue = task_query
        self.sheets = sheets
        cells = parse_range(cells)

        self.start_data_cell = f'{sheet_name}!{col_num_to_string(cells[1])}{num_to_string(cells[0])}'
        self.data_cell = self.start_data_cell + f':{col_num_to_string(cells[3])}{num_to_string(cells[2])}'
        self.start_data_index = cells[:2]
        self.work_zone = dict([(key, val + SHIFT_DIM.get(key) if val is not None else val)
                               for key, val in zip(SHIFT_DIM.keys(), cells)]
                              + [('sheetId', self.sheet_id)])

        super().__init__(self.sheet_id, self._task_queue, self.work_zone, self.start_data_index,
                         self.start_data_cell, self.base, self.data_cell)

    def sheet(self, sheet_name):
        return Sheet(sheet_name, self.sheet_id, self._task_queue, self.sheets, self.base)

    def cell_range(self, input_range):
        return Sheet(self.sheet_name, self.sheet_id, self._task_queue, self.sheets, self.base, input_range)


class Client:
    def __init__(self, token_path='token.json'):
        self.token_path = token_path
        self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        self.list_of_spreadsheets = []
        self.connect = self._connect()
        self.connect_v3 = self._connect_v3()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.exec()

    def create_spreadsheet(self, title, sheets: list = ['Sheet1']):
        ss = SpreedSheet(build('sheets', 'v4', credentials=self.credentials).spreadsheets()
                         .create(fields='spreadsheetId',
                                 body={
                                     'properties': {'title': title},
                                     'sheets': [{'properties': {'title': sheet_name}} for sheet_name in sheets]})
                         .execute().get('spreadsheetId'), token_path=self.token_path,
                         credentials=self.credentials, connect=self.connect)
        self.list_of_spreadsheets.append(ss)
        return ss

    def move_spreadsheet_to_folder(self, ss: SpreedSheet, real_folder_id):
        previous_parents = ','.join(self.connect_v3.files().get(fileId=ss.spreadsheet_id, fields='parents').execute().get('parents'))
        self.connect_v3.files().update(fileId=ss.spreadsheet_id, addParents=real_folder_id,
                                       removeParents=previous_parents, fields='id, parents').execute()

    def share_spreadsheet_with_domain(self, ss: SpreedSheet, domain, role: ShareRole):
        self.connect_v3.permissions().create(**{
            'fileId': ss.spreadsheet_id,
            'body': {
                'type': 'domain',
                'role': role.value,
                'domain': domain,
                'allowFileDiscovery': True,
            },
            'fields': 'id',
        }).execute()

    def share_spreadsheet_with_user(self, ss: SpreedSheet, user: str, role: ShareRole):
        self.connect_v3.permissions().create(**{
            'fileId': ss.spreadsheet_id,
            'body': {
                'type': 'user',
                'role': role.value,
                'emailAddress': user,
            },
            'fields': 'id',
        }).execute()

    def get_spreadsheet(self, spreadsheet_id):
        ss = SpreedSheet(spreadsheet_id=spreadsheet_id, token_path=self.token_path,
                         credentials=self.credentials, connect=self.connect)
        self.list_of_spreadsheets.append(ss)
        return ss

    def _connect(self):
        return build('sheets', 'v4', credentials=self.credentials)

    def _connect_v3(self):
        return build('drive', 'v3', credentials=self.credentials)

    def exec(self):
        for st in self.list_of_spreadsheets:
            st.exec()
