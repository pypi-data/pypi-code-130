from csv import DictWriter, QUOTE_ALL
import json
from sys import maxsize as SYS_MAXSIZE
import os

INPUT_DATA_FILES = [
    #('results/1cns_per_qm/yelp-standard.json', 'yelp',),
    ('../../../results/cns_from_golden_qms/imdb-standard.json', 'imdb.json',),
    ('../../../results/cns_from_golden_qms/nba-standard.json', 'nba.json',),
    ('../../../results/cns_from_golden_qms/dblp-standard.json', 'dblp.json',),
    ('../../../results/cns_from_golden_qms/twitter-standard.json', 'twitter.json',),
    ('../../../results/cns_from_golden_qms/yelp_expanded-standard.json', 'yelp_expanded.json',),
]

print(os.getcwd())

for file, dataset_name in INPUT_DATA_FILES:

    print(f'Formatting evaluation results from {dataset_name} dataset')

    with open(file) as f:
        evaluation_results = json.load(f)

    header = [
        'query_number',
        'vkm_count',
        'skm_count',
        'qm_count',
        'cn_count',
        # 'max(cn_count)',
        # 'min(cn_count)',
    ]

    # for i in range(29):
    #     header.append(str(i + 1))

    with open(f'parsed_results_{dataset_name}.csv', 'w') as f:
        writer = DictWriter(f, fieldnames=header)
        writer.writeheader()

        results = evaluation_results['results']
        for n, result in enumerate(results):
            data = {}
            data['query_number'] = f'Query {n}'

            if 'vkm_count' in result:
                data['vkm_count'] = result['vkm_count']
            else:
                data['vkm_count'] = 0
            if 'skm_count' in result:
                data['skm_count'] = result['skm_count']
            else:
                data['skm_count'] = 0

            data['qm_count'] = result['qm_count']
            data['cn_count'] = result['cn_count']

            max_cn_count = 0
            min_cn_count = SYS_MAXSIZE

            # for qm in result['statistics']:
            #     current_cn_count = result['statistics'][qm]['generated_cns_qty']
            #     if current_cn_count > max_cn_count:
            #         max_cn_count = current_cn_count

            #     if current_cn_count < min_cn_count:
            #         min_cn_count = current_cn_count

            # data['max(cn_count)'] = max_cn_count
            # data['min(cn_count)'] = min_cn_count
            writer.writerow(data)

    header = [
        'query_number',
        'correct_qm_rank',
        'correct_cn_rank',
    ]

    with open(f'formatted_evaluation_{dataset_name}.csv', 'w') as f:
        writer = DictWriter(f, fieldnames=header)
        writer.writeheader()

        qm_relevant_positions = evaluation_results['evaluation']['query_matches']['relevant_positions']
        cn_relevant_positions = evaluation_results['evaluation']['candidate_networks']['relevant_positions']
        qm_relevant_positions_len = len(qm_relevant_positions)
        cn_relevant_positions_len = len(cn_relevant_positions)

        if qm_relevant_positions_len != cn_relevant_positions_len:
            print(f'Different list lengths for QMs ({qm_relevant_positions_len}) and CNs ({cn_relevant_positions_len})!')
            exit(-1)

        number_of_queries = qm_relevant_positions_len
        for n in range(number_of_queries):
            data = {}
            data['query_number'] = f'Query {n + 1}'
            data['correct_qm_rank'] = qm_relevant_positions[n]
            data['correct_cn_rank'] = cn_relevant_positions[n]
            writer.writerow(data)

    # header = [
    #     'qm_evaluation_metric',
    #     'qm_result',
    #     'cn_evaluation_metric',
    #     'cn_result',
    # ]

    # with open(f'formatted_metric_results_{dataset_name}.csv', 'w') as f:
    #     writer = DictWriter(f, fieldnames=header)
    #     writer.writeheader()

    #     lathe_steps = [
    #         'query_matches',
    #         'candidate_networks'
    #     ]

    #     evaluation_metric_keys = evaluation_results['evaluation']['query_matches'].keys()

    #     for key in evaluation_metric_keys:
    #         if key == 'relevant_positions':
    #             continue

    #         data = {}
    #         data['qm_evaluation_metric'] = key
    #         data['qm_result'] = evaluation_results['evaluation']['query_matches'][key]
    #         data['cn_evaluation_metric'] = key
    #         data['cn_result'] = evaluation_results['evaluation']['candidate_networks'][key]
    #         writer.writerow(data)

    # header = [
    #     'query_number',
    #     'vkm_phase',
    #     'skm_phase',
    #     'qm_phase',
    #     'cn_phase',
    #     'total_time'
    # ]

    # with open(f'formatted_per_phase_time_{dataset_name}.csv', 'w') as f:
    #     writer = DictWriter(f, fieldnames=header, quoting=QUOTE_ALL)
    #     writer.writeheader()

    #     results = evaluation_results['results']
    #     for n, result in enumerate(results):
    #         data = {}
    #         data['query_number'] = f'Query Number {n + 1}'
    #         data['vkm_phase'] = '{:.3f}'.format(result['elapsed_time']['vkm']).replace('.', ',')
    #         data['skm_phase'] = '{:.3f}'.format(result['elapsed_time']['skm']).replace('.', ',')
    #         data['qm_phase'] = '{:.3f}'.format(result['elapsed_time']['qm']).replace('.', ',')
    #         data['cn_phase'] = '{:.3f}'.format(result['elapsed_time']['cn']).replace('.', ',')
    #         data['cn_phase'] = '{:.3f}'.format(result['elapsed_time']['cn']).replace('.', ',')
    #         data['total_time'] = '{:.3f}'.format(result['elapsed_time']['total']).replace('.', ',')
    #         writer.writerow(data)

    # results = evaluation_results['results']
    # vkm_phase = []
    # skm_phase = []
    # qm_phase = []
    # cn_phase = []
    # total_time = []
    # for n, result in enumerate(results):
    #     print(result['elapsed_time']['vkm'], result['elapsed_time']['skm'], result['elapsed_time']['qm'], result['elapsed_time']['cn'], result['elapsed_time']['total'])
    #     vkm_phase.append(result['elapsed_time']['vkm'])
    #     skm_phase.append(result['elapsed_time']['skm'])
    #     qm_phase.append(result['elapsed_time']['qm'])
    #     cn_phase.append(result['elapsed_time']['cn'])
    #     total_time.append(result['elapsed_time']['total'])

    # print('Avg VKM time: {}'.format(sum(vkm_phase)/len(vkm_phase)))
    # print('Avg SKM time: {}'.format(sum(skm_phase)/len(skm_phase)))
    # print('Avg QM time: {}'.format(sum(qm_phase)/len(qm_phase)))
    # print('Avg CN time: {}'.format(sum(cn_phase)/len(cn_phase)))
    # print('Avg total time: {}'.format(sum(total_time)/len(total_time)))
