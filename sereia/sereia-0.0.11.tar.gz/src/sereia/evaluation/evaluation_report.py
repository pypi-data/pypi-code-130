import csv
import json



BASE_EXPERIMENT_FILE = '../results/cns_from_golden_qms/{}-standard.json'

class CSVReport(object):

    def __init__(self, dataset_name, results):
        self.dataset_name = dataset_name
        self.results = results

    def _load_results(self):
        dataset_results_filename = BASE_EXPERIMENT_FILE.format(
            self.dataset_name,
        )

        with open(dataset_results_filename) as f:
            self.results = json.load(f)

    def generate(self):

        if 'retrieval_score' not in self.results['evaluation']:
            return

        result_per_query = self.results['results']
        evaluation_results = self.results['evaluation']['retrieval_score']

        overall_results = {}

        for item in result_per_query:
            keyword_query = item['keyword_query']
            query_generation_time = item['query_generation_time']
            query_execution_time = item['query_execution_time']
            query_number = item['query_number']

            overall_results[keyword_query] = {
                'query_gen_time': query_generation_time,
                'query_exec_time': query_execution_time,
                'query_number': query_number
            }
        
        for item in evaluation_results:
            keyword_query = item['keyword_query']
            precision = item['precision']
            recall = item['recall']
            retrieved_count = item['num_documents_retrieved']
            expected_count = item['num_documents_expected']

            overall_results[keyword_query]['precision'] = precision
            overall_results[keyword_query]['recall'] = recall
            overall_results[keyword_query]['retrieved_count'] = retrieved_count
            overall_results[keyword_query]['expected_count'] = expected_count
        
        print('Generating CSV report')
        from pprint import pprint as pp
        pp(overall_results)

        report_filepath = '../query_results.csv'

        with open(report_filepath, 'w') as f:
            field_names = [
                'Keyword Query',
                'Query Number',
                'Precision',
                'Recall',
                'Gen Time (s)',
                'Exec Time (s)',
                '# Doc. Retrieved',
                '# Doc. Expected',
            ]

            writer = csv.DictWriter(f, fieldnames=field_names, quoting=csv.QUOTE_ALL)

            writer.writeheader()

            for keyword_query in overall_results:
                writer.writerow(
                    {
                        'Keyword Query': keyword_query,
                        'Query Number': overall_results[keyword_query]['query_number'] + 1,
                        'Precision': overall_results[keyword_query]['precision'],
                        'Recall': overall_results[keyword_query]['recall'],
                        'Gen Time (s)': overall_results[keyword_query]['query_gen_time'],
                        'Exec Time (s)': overall_results[keyword_query]['query_exec_time'],
                        '# Doc. Retrieved': overall_results[keyword_query]['retrieved_count'],
                        '# Doc. Expected': overall_results[keyword_query]['expected_count']
                    }
                )
            


