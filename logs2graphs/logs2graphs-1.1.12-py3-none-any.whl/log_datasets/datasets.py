import datetime
import re
from abc import ABC, abstractmethod
from os import mkdir, makedirs
from os.path import exists, join
from typing import List, Mapping, Union

import gdown
import networkx
import pandas as pd

from utils.Drain import LogParser
from utils.graphs_util import GraphFromSessionWindowCreator, GraphFromSlidingWindowCreator, \
    GraphFromTumblingWindowCreator, create_networkx_graph


class LogDataset(ABC):
    """
    Class for representation of a Dataset. The Dataset should be stored as a Pandas Data Frame
    with the following 4 columns:
    - timestamp
    - session_id (probably only possible in the HDFS dataset)
    - test_id (probably applicable only for the NOVA dataset)
    - event_id (string)
    """

    def __init__(self, data_folder_path="../data"):
        self.logs = pd.DataFrame()
        self.templates = pd.DataFrame()
        self.anomalous_logs = None
        self.data_folder_path = data_folder_path

    @abstractmethod
    def load_logs(self):
        """
        Method that will load the corresponding logs dataset and store it into self.logs
        This method should be able to download the dataset from some line (on the first run of the application) i.e
        check first if we currently have the dataset in some location, and if we don't, download it.
        :return: void
        """
        pass

    @abstractmethod
    def load_event_templates(self):
        """
        Method that will perform the DRAIN events extraction
        :return:
        """
        pass

    @abstractmethod
    def assign_event_id_to_logs(self):
        """
        Method that will assign an event_id
        :return:
        """
        pass

    def initialize_dataset(self):
        self.load_logs()
        self.load_event_templates()
        self.assign_event_id_to_logs()

    def create_graphs(self, window_type, window_size, window_slide, test_id=None, include_last=True,
                      include_all_event_ids=False) \
            -> List[Mapping[str, Union[str, Mapping[str, Mapping[str, float]]]]]:
        """
        :param include_positional_embeddings:
        :param include_all_event_ids: A bool value that represents whether all detected event IDs should be included in the graph
        :param window_type: string that represents the window type, possible values are: session, tumbling, sliding
        :param window_size: the size of the window in milliseconds
        :param window_slide: the size of the slide of the window in milliseconds
        :param test_id: an integer that represent the test_id of a experiment. applicable only for the nova dataset
        :param include_last: A bool value that represents whether the last event ID should be included in the graph generation
        :return: result: list of dictionaries where each dictionary represents the data for one graph created by this
        method. Each dictionary has three key,value pairs. The first two (str,datetime.datetime) represent the start
        and the end of the window for which the graph was generated and the third one `graph_dic` represents the dictionary
        representation of the graph as obtained from the create_graph_as_dict method.
        """
        logs = self.logs[self.logs['test_id'] == test_id] if 'test_id' in self.logs.columns else self.logs
        if window_type == 'session' and "session_id" not in self.logs.columns:
            raise Exception("Session windows are not allowed for this dataset")

        if window_type == 'tumbling':
            graph_creator = GraphFromTumblingWindowCreator(
                logs=logs,
                templates=self.templates,
                include_last=include_last,
                include_all_event_ids=include_all_event_ids,
                window_size=window_size)
        elif window_type == 'sliding':
            graph_creator = GraphFromSlidingWindowCreator(
                logs=logs,
                templates=self.templates,
                include_last=include_last,
                include_all_event_ids=include_all_event_ids,
                window_size=window_size,
                window_slide=window_slide
            )
        else:
            graph_creator = GraphFromSessionWindowCreator(
                logs=logs,
                templates=self.templates,
                include_last=include_last,
                include_all_event_ids=include_all_event_ids
            )

        return graph_creator.create_graphs()

    def create_networkx_graphs(self, window_type,
                               window_size,
                               window_slide,
                               test_id=None,
                               include_last=True,
                               include_all_event_ids=False,
                               include_positional_embeddings=False) -> List[networkx.Graph]:

        graphs = self.create_graphs(window_type, window_size, window_slide, test_id, include_last,
                                    include_all_event_ids)

        results = []
        for graph in graphs:
            graph_dict = graph['graph_dict']
            positional_embeddings = graph['positional_embeddings'] if include_positional_embeddings else dict()
            results.append(create_networkx_graph(
                graph_dict,
                positional_embeddings,
                self.anomalous_logs,
                list(self.templates['EventId'])
            ))
        return results


class HDFSDataset(LogDataset):
    def __init__(self, data_folder_path="../data"):
        LogDataset.__init__(self, data_folder_path)

    @staticmethod
    def __find(params):
        for x in eval(params):
            if "blk" in x:
                match = re.search('(.*)(blk_(-*\d*))(.*)', x)
                return match.group(2)
        return None

    def load_logs(self):

        # download raw logs
        output_path = f"{self.data_folder_path}/hdfs/HDFS.log"
        # 189R1qzhTMLQYo2llwse5F-InsFxBbxr-
        url = 'https://drive.google.com/uc?id=189R1qzhTMLQYo2llwse5F-InsFxBbxr-'
        if not exists(output_path):
            mkdir(join(f"{self.data_folder_path}/hdfs"))
            gdown.download(url, output_path, quiet=False)

        if not exists(f"{self.data_folder_path}/hdfs/HDFS.log_structured.csv"):
            input_dir = f"{self.data_folder_path}/hdfs/"
            output_dir = f"{self.data_folder_path}/hdfs/"
            log_file = 'HDFS.log'
            log_format = "<Date> <Time> <Pid> <Level> <Component>: <Content>"

            # Regular expression list for optional preprocessing (default: [])
            regex = [
                r'blk_(|-)[0-9]+',  # block id
                r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',  # IP
                r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$',  # Numbers
            ]
            st = 0.5  # Similarity threshold
            depth = 2  # Depth of all leaf nodes

            parser = LogParser(log_format, indir=input_dir, outdir=output_dir, depth=depth, st=st, rex=regex)
            parser.parse(log_file)

        self.logs = pd.read_csv(f"{self.data_folder_path}/hdfs/HDFS.log_structured.csv")
        self.logs = self.logs.iloc[1:, :]
        dates = {81109: "2008-11-9", 81110: "2008-11-10", 81111: "2008-11-11"}
        self.logs['Date'] = self.logs['Date'].apply(lambda x: dates[x])
        self.logs['Time'] = self.logs['Time'].apply(
            lambda x: datetime.datetime.strptime(str(x).zfill(6), "%H%M%S").strftime("%H:%M:%S"))
        self.logs['timestamp'] = pd.to_datetime(self.logs['Date'] + " " + self.logs['Time'])
        self.logs['EventId'] = self.logs['EventId'].astype('str')
        self.logs['block_id'] = self.logs['ParameterList'].apply(lambda x: self.__find(x))
        self.logs['block_id'] = self.logs['block_id'].astype('str')
        self.logs.sort_values(['timestamp'], inplace=True)

        self.logs = self.logs[['timestamp', 'EventId', 'block_id']]
        self.logs.rename(columns={'timestamp': 'timestamp', 'EventId': 'event_id', 'block_id': 'session_id'},
                         inplace=True)

    def load_event_templates(self):
        output_path = f'{self.data_folder_path}/hdfs/HDFS.log_templates.csv'
        # TODO work on this (this should be a list of event IDs not a pandas dataframe)
        self.templates = pd.read_csv(output_path)

    def assign_event_id_to_logs(self):
        """
        This dataset already has event IDs attached to the logs
        :return:
        """
        pass

    # def print_sample(self):
    #     # print(self.logs.head(20))


class BGLDataset(LogDataset):
    def __init__(self, data_folder_path="../data"):
        LogDataset.__init__(self, data_folder_path)

    def load_logs(self):
        output_file = f'{self.data_folder_path}/bgl/unparsed/logs.log'
        url = 'https://drive.google.com/uc?id=1qlYZB26biKt7jlxL8YmIXHlqqeMDv-iX'

        if not exists(f'{self.data_folder_path}/bgl/'):
            print(f'Creating main directory for BGL logs on path {self.data_folder_path}/bgl/')
            makedirs(f'{self.data_folder_path}/bgl/')

        if not exists(f'{self.data_folder_path}/bgl/unparsed'):
            print(f'Creating directory {self.data_folder_path}/bgl/unparsed')
            makedirs(f'{self.data_folder_path}/bgl/unparsed')

            if not exists(f'{self.data_folder_path}/bgl/unparsed/logs.log'):
                print(f"Downloading BGL logs to path: {self.data_folder_path}/bgl/unparsed/logs.log")
                gdown.download(url, output_file, quiet=False)
            else:
                print(
                    f'BGL logs are already downloaded and saved on path {self.data_folder_path}/bgl/unparsed/logs.log')

        else:
            print(f'Directory {self.data_folder_path}/bgl/unparsed already exists')

        output_dir = f'{self.data_folder_path}/bgl/'

        if not exists(f'{self.data_folder_path}/bgl/processed_logs.log_structured.csv'):
            # Replace the commas with semicolons
            # commas cause problems with DRAIN and writing to csv
            log_file = f'{self.data_folder_path}/bgl/unparsed/processed_logs.log'

            lf = open(log_file, 'a')

            with open(output_file) as of:
                for line in of:
                    lf.write(line.replace(',', ';'))

            lf.close()

            # Parse the logs with DRAIN
            log_file = 'processed_logs.log'
            input_dir = f'{self.data_folder_path}/bgl/unparsed/'
            log_format = "<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>"

            regex = [
                r'core\.\d+', r'(?<=r)\d{1,2}', r'(?<=fpr)\d{1,2}', r'(0x)?[0-9a-fA-F]{8}',
                r'(?<=\.\.)0[xX][0-9a-fA-F]+', r'(?<=\.\.)\d+(?!x)', r'\d+(?=:)', r'^\d+$', r'(?<=\=)\d+(?!x)',
                r'(?<=\=)0[xX][0-9a-fA-F]+', r'(?<=\ )[A-Z][\+|\-](?= |$)', r'(?<=:\ )[A-Z](?= |$)',
                r'(?<=\ [A-Z]\ )[A-Z](?= |$)'
            ]
            st = 0.4
            depth = 3

            parser = LogParser(log_format, indir=input_dir, outdir=output_dir, rex=regex, st=st, depth=depth)
            parser.parse(log_file)

            print("BGL logs parsing is complete!")

            print("Starting to clean up the logs!")
            self.logs = pd.read_csv(output_dir + 'processed_logs.log_structured.csv')
            self.templates = pd.read_csv(output_dir + 'processed_logs.log_templates.csv')
            self.logs['Time'] = pd.to_datetime(self.logs['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            self.logs.sort_values(['Time'])

            anomalous_event_ids_dict = {k: 0 for k in list(self.logs[self.logs['Label'] != '-']['EventId'].unique())}

            normal_event_ids = list(self.logs[self.logs['Label'] == '-']['EventId'].unique())

            mutual_event_ids = []
            for event_id in normal_event_ids:
                if event_id in anomalous_event_ids_dict.keys():
                    mutual_event_ids.append(event_id)

            for event_id in mutual_event_ids:
                tmp_df = self.logs[self.logs['EventId'] == event_id]
                total_count = len(tmp_df)
                normal_count = len(tmp_df[tmp_df['Label'] == '-'])
                anomalous_count = total_count - normal_count
                anomalous_percentage = anomalous_count * 100.0 / total_count
                normal_percentage = normal_count * 100.0 / total_count
                diff = abs(anomalous_percentage - normal_percentage)

                if normal_percentage > 90.0:  # threshold
                    print(f"Logs with eventID {event_id} have mixed types but more than 90% normal logs. "
                          f"Dropping the anomalous logs from this event type and removing the event id "
                          f"from the list of anomalous event ids")
                    del anomalous_event_ids_dict[event_id]
                    self.logs = self.logs.drop(
                        self.logs[(self.logs['EventId'] == event_id) & (self.logs['Label'] != '-')].index)
                elif anomalous_percentage > 90.0:
                    print(f"Logs with eventID {event_id} have mixed types but more than 90% anomalous logs. "
                          f"Dropping the normal logs from this event type")
                    self.logs = self.logs.drop(
                        self.logs[(self.logs['EventId'] == event_id) & (self.logs['Label'] == '-')].index)
                elif diff < 30.0:  # Split the event templates into two separate templates if the difference is less than 25%
                    print(f"Logs with event ID {event_id} have less that 30% difference in the count of anomalous "
                          f"and normal logs. Splitting the event to 2 events: {event_id}_n for all the normal logs and "
                          f"{event_id}_a for all the anomalous logs.")
                    self.logs['EventId'] = self.logs.apply(lambda row: split_row(row, event_id), axis=1)
                    del anomalous_event_ids_dict[event_id]
                    self.templates = self.templates.drop(self.templates[self.templates['EventId'] == event_id].index)
                    # Add the anomalous template in the anomalous templates dict
                    anomalous_event_ids_dict[f'{event_id}_a'] = 1
                    anomalous_event_ids_dict[f'{event_id}_n'] = 1

                    self.templates = pd.concat(
                        [self.templates,
                         pd.DataFrame([
                             {"EventId": f'{event_id}_a'},
                             {"EventId": f'{event_id}_n'}
                         ])
                         ]
                    )

                else:  #
                    del anomalous_event_ids_dict[event_id]
                    self.logs = self.logs.drop(self.logs[self.logs['EventId'] == event_id].index)
                    self.templates = self.templates.drop(self.templates[self.templates['EventId'] == event_id].index)

                self.anomalous_logs = list(anomalous_event_ids_dict.keys())

                self.logs.to_csv(output_dir + 'processed_logs.log_structured.csv')
                self.templates.to_csv(output_dir + 'processed_logs.log_templates.csv')

                self.logs = self.logs[['Time', 'EventId']]
                self.logs.rename(columns={'Time': 'timestamp', 'EventId': 'event_id'}, inplace=True)

        if not exists(f'{self.data_folder_path}/bgl/processed_logs.log_structured_short.csv'):
            print(f"Short processed logs not found at f'{self.data_folder_path}/bgl/processed_logs"
                  f".log_structured_short.csv. Will process them now! Please hold.")
            self.logs = pd.read_csv(output_dir + 'processed_logs.log_structured.csv')

            self.logs = self.logs[['Time', 'EventId', 'Label']]
            self.logs.rename(columns={'Time': 'timestamp', 'EventId': 'event_id'}, inplace=True)

            self.logs.to_csv(f'{self.data_folder_path}/bgl/processed_logs.log_structured_short.csv')

            self.templates = pd.read_csv(output_dir + 'processed_logs.log_templates.csv')

            self.anomalous_logs = list(self.logs[self.logs['Label'] != '-']['event_id'].unique())

            self.logs = self.logs[['timestamp', 'event_id']]

            print(
                f'Saving short processed structured logs for BGL at path {self.data_folder_path}/bgl'
                f'/processed_logs.log_structured_short.csv')
        else:
            print(f"The short processed file is found at {self.data_folder_path}/bgl/"
                  f"processed_logs.log_structured_short.csv. Loading the short stuff to optimize time and memory!")
            self.logs = pd.read_csv(f'{self.data_folder_path}/bgl/processed_logs.log_structured_short.csv')
            # self.
            self.anomalous_logs = list(self.logs[self.logs['Label'] != '-']['event_id'].unique())
            self.templates = pd.read_csv(output_dir + 'processed_logs.log_templates.csv')
            self.logs['timestamp'] = pd.to_datetime(self.logs['timestamp'], format="%Y-%m-%d-%H.%M.%S.%f")
            self.logs = self.logs[['timestamp', 'event_id']]
            print ("Short processed file is loaded up. Have fun.")

    def load_event_templates(self):
        self.templates = pd.read_csv(f'{self.data_folder_path}/bgl/processed_logs.log_templates.csv')

    def assign_event_id_to_logs(self):
        """
        BGL already has event ids, do nothing.
        """
        pass


class NovaDataset(LogDataset):
    def __init__(self, data_folder_path="../data"):
        LogDataset.__init__(self, data_folder_path)
        self.anomalous_logs = ['f680c053', '40206f48', 'c9043c44', 'c03dad2d', 'ef6e7b9e', 'e666ec6f', '6d765f31',
                               '879ea5bb', 'c9c98d3b', '895eb283', 'ec253f87', 'a72188c8', 'a987a892', 'e0d2142b',
                               '0f2ef0f1', 'e58cad65', 'b5d66d95', 'af901f3b', '7a899844', '54eb1be1', '1d12462b',
                               'b8e9463c', '095edf34', 'ec7fa6ce', 'daff47bf', '59e838c8', '53a5a044', '9a2c8541',
                               'd12829f8', '0ab3cef6', '041f292c', 'd6d9af41', 'ba88c7d8', '8df33b2f', '1544fa1c',
                               '6065c610', '485a2872', 'a0c9927d', '8c9b4bef', 'e54a6a63', '1123e884', 'e599e359',
                               '4d89da7e', '808039a9', 'eb99df1b', '8fe5e47c', '9a35f684', '7fd638a9', 'bd1518d3',
                               '85222adb', '875b7935', '29edf214', 'c7af4a07', 'cdc8c0bb', '1289b10d', '525d19dd',
                               '7981fd0c', '7366954a', '252847ed', '6aab68e3', '7d5b1608', '44aebf8e', '9483c621',
                               'e00d67e7', '5b547994', 'b8052b25', '58995305', 'de919eb5', 'b71472cf', '6ec5a18d',
                               'b2ffd2be', 'a0d89467', '73ee123d', '32d1c10f', '54a4f708', '7a1b07cd', '260be159',
                               '9064dde6', 'b216dde5', '072292e8', '090149fe', '2bb55381', '1553c20a', 'a47b8c12',
                               'f9547a6c', 'aa4549b8', '00222bb8', 'd82cb15d', '0a102ea5', '50fcf2f8', '91f835b0',
                               'd95e1207', '0f7a78c1', 'acd26318', '4355a1db', '2e1a0cd9', '57fe8e47', '7b3e2eac',
                               '622b6a3f', '675f1d72', '6d53c0af', 'd793c869', '94f0ba06', 'a2926c3f', '0fd492f7',
                               '0e080610', 'd530dea3', 'a5e60942', '06f86f88', '5d64a93f', '4116c241', '577304d2',
                               '5e2ba79a', 'aa213323', '64637844', 'bac0f26e', 'd1fcc31d', '6899ef8a', 'e0099b85',
                               'bd6f6bbc', 'aadd25f4', 'b8f641dc', '12e244f2', '756f5c03', '05401b4f', 'fd8f1a5e',
                               '02525647', '319130ea', '58591b5c', '02e5bdf8', 'fa83b19b', '8861c737', '3fb2a127',
                               '1adb2a42', '2400b11f', '8ce81960', 'e4060487', '2b548192', '699ceb91', 'f7b46d4a',
                               '7c3e51b9', '3327ffcf', 'b586d301', 'f74207da', '8b699885', '3d635119', 'c8b73b91',
                               '8ecc3813', '5a36a457', 'b5794355', '66cf9d79', '4d3bf8f6', 'ea3a8254', '92dbdc40',
                               '2b3681ad', 'a58526ac', '4cace397', '9193527c', 'd70b9e96', '95e880a1', 'bea1ad5c',
                               '42c593ba', 'ee7f1b31', 'f28720ba', 'b76bada8', '4942406d', '3cb0ad99']

    def load_logs(self):
        output_path = f'{self.data_folder_path}/nova/logs.csv'
        url = 'https://drive.google.com/uc?id=1Lf-kmpf6OP1WpKT_KkZeUT745CV168gb'
        if not exists(output_path):
            mkdir(f"{self.data_folder_path}/nova")
            gdown.download(url, output_path, quiet=False)

        self.logs = pd.read_csv(output_path)
        self.logs = self.logs.iloc[1:, :]
        self.logs['test_id'] = self.logs['test_id'].astype('int')
        self.logs['time_hour'] = pd.to_datetime(self.logs['time_hour'])
        self.logs.sort_values(['time_hour'])

        self.logs = self.logs[['test_id', 'time_hour', 'EventId']]
        self.logs.rename(columns={'time_hour': 'timestamp', 'EventId': 'event_id'}, inplace=True)

    def load_event_templates(self):
        output_path = f'{self.data_folder_path}/nova/event_templates.csv'
        url = 'https://drive.google.com/uc?id=1SZqgSvUhvwZTofKslo21U3z2VEBbU17w'
        if not exists(output_path):
            gdown.download(url, output_path, quiet=False)
        self.templates = pd.read_csv(f'{self.data_folder_path}/nova/event_templates.csv')

    def assign_event_id_to_logs(self):
        """
        This dataset already has event IDs attached to the logs
        :return:
        """
        pass


def split_row(row, event_id):
    if row['EventId'] == event_id:
        if row['Label'] == '-':  # normal event
            return f'{event_id}_n'
        else:
            return f'{event_id}_a'
    else:
        return row['EventId']


if __name__ == '__main__':
    dataset = BGLDataset("../../data")
    dataset.initialize_dataset()
    # Create window of 1 hour * 60 min * 60 secs * 1000 ms
    graphs = dataset.create_graphs(window_type='tumbling', window_size=4 * 60 * 60 * 1000, window_slide=0,
                                   include_last=False, test_id=1)
    for graph in graphs:
        print(graph)
