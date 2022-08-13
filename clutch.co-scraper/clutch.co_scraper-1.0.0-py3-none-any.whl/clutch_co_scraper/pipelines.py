import re
from openpyxl import Workbook
import numpy as np
import os
from openpyxl.workbook.child import INVALID_TITLE_REGEX


class ClutchCoScraperPipeline:

    def __init__(self):
        self.items = {}
        self.path = 'clutch.co_data'

    def open_spider(self, spider):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    # Collect data about firms in self.items
    def process_item(self, item, spider):
        item_category = re.sub(INVALID_TITLE_REGEX, '_', item['category'][0])
        item_subcategory = re.sub(INVALID_TITLE_REGEX, '_', item['subcategory'][0])

        if item_category in self.items.keys():
            if item_subcategory in self.items[item_category].keys():
                main_category = self.items[item_category][item_subcategory]
            else:
                main_category = self.items[item_category][item_subcategory] = {}
        else:
            self.items[item_category] = {}
            main_category = self.items[item_category][item_subcategory] = {}

        if bool(main_category.keys()):
            for k, v in main_category.items():
                main_category[k].extend(item[k])

        else:
            for k, v in item.items():
                if k == 'category' or k == 'subcategory':
                    continue
                main_category[k] = []
                main_category[k].extend(v)

    # Save data from self.items to spreadsheets
    def close_spider(self, spider):
        items = self.items

        for category, subcategories in items.items():
            wb = Workbook()
            del wb[wb.active.title]

            for subcategory, item in subcategories.items():
                ws = wb.create_sheet(subcategory)
                ws.append(list(item.keys()))

                table_values = list(item.values())
                table_values = np.array(table_values).transpose()
                for value in table_values:
                    ws.append(list(value))

            wb.save(f'{self.path}/{category}.xlsx')
