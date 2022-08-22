import pandas as pd
from lxml.etree import XMLParser, parse
from io import StringIO

class NEM12_Parser():
    """
    Class used to parse NEM12 files
    """

    def __init__(self, file_path=''):
        self.file_path = file_path
        self.data = None
        self.root = None

        if file_path.endswith('.csv'):
            self.read_csv()
        elif file_path.endswith('.xml'):
            self.read_xml()

    def read_csv(self, file_path=None):
        """
        Function that parses a NEM12 csv file
        """
        if file_path is None:
            file_path = self.file_path

        self.data = pd.read_csv(file_path, names=list(range(295)), dtype=str)

    def read_xml(self, file_path=None):
        """
        Function that parses a NEM12 xml file
        """
        # set file path to default if not provided
        if file_path is None:
            file_path = self.file_path

        # parse xml file
        parser = XMLParser(huge_tree=True)
        self.root = parse(file_path, parser=parser)

        # store data
        self.csv = self.root.find('.//CSVIntervalData')
        csv_text = StringIO(self.csv.text)
        self.data = pd.read_csv(csv_text, names=list(range(295)), dtype=str)

    def fix_data(self):
        """
        Removes 400 and 500 lines and gets rid of duplicate lines
        """
        # remove lines starting with 400 or 500
        self.data = self.data[self.data[0] != '400']
        self.data = self.data[self.data[0] != '500']
        
        # remove duplicate 300 lines
        self.data = self.data.reset_index(drop=True)
        self.data = self.data.loc[(self.data.fillna(-1) != self.data.shift(-1).fillna(-1)).any(axis=1)]

    def output_xml(self, file_path=None):
        """
        Creates an xml file at the specified file path
        """
        if file_path == None:
            file_path = self.file_path
        
        # convert csv to string
        data = self.data.to_csv(header=False, index=False, line_terminator='\n')

        # remove trailing commas
        output = ''
        for line in data.splitlines():
            output += '\n' +  line.rstrip(',')

        # output fixed xml file
        self.csv.text = output
        self.root.write(file_path, pretty_print=True)

    def get_element(self, element_name):
        """
        Function that finds the specified element
    
        Returns an Element Tree object matching the element name provided
        """

        return self.root.find('.//' + element_name)

    def set_element(self, element_name, value):
        """
        Function that sets the specified element to the given value

        Returns an Element Tree object matching the element name provided
        """

        element = self.get_element(element_name)
        element.text = value
        return element