import os
import json
from prettytable import PrettyTable
data = PrettyTable(["Col1", "Col2", "Col3"])

data.add_row(["test1", "test2", "test3"])
data.add_row(["test4", "test5", "test6"])
data.add_row(["test7", "test8", "test9"])
print(data)

with open('test_pp.csv', 'w', newline='') as f_output:
    f_output.write(data.get_csv_string())
