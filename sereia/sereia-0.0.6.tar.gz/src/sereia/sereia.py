import json
from pathlib import Path
from os import listdir
from os.path import isfile, join
from timeit import default_timer as timer

from sereia.candidate_network import CandidateNetworkHandler
from sereia.database import MongoHandler
from sereia.evaluation import EvaluationHandler
from sereia.index import IndexHandler
from sereia.keyword_match import KeywordMatchHandler
from sereia.query_match import QueryMatchHandler
from sereia.utils import ConfigHandler, KeywordQuery, Similarity, Tokenizer
from sereia.utils.result import SereiaResult


class Sereia():
    
    def __init__(self, database_name, database_credentials, config_directory):
        self.config = ConfigHandler(
            config_directory,
        )
        self.queryset_configs = self.config.get_queryset_configs()
        self.max_num_query_matches = 100
        self.max_qm_size = 3
        self.max_cjn_size = 3
        self.topk_cns = 10
        self.topk_cns_per_qm = 1
        self.topk_cns_per_qm_list = [1]
        self.approaches = ['standard']
        self.assume_golden_qms = False
        self.input_desired_cn = False
        self.datasets_configurations = {}
        self.querysets_configurations = {}
        self.current_database = database_name

        #dont forget to choose the Database according to the config file
        self.database_handler = MongoHandler(
            self.current_database,
            database_credentials,
            self.config,
        )
        self.index_handler = IndexHandler(
            self.current_database,
            self.database_handler,
            self.config,
        )
        self.tokenizer = Tokenizer(tokenize_method = 'simple')
        self.similarity = Similarity(self.index_handler.schema_index)
        self.keyword_match_handler = KeywordMatchHandler(self.similarity)
        self.query_match_handler = QueryMatchHandler()
        self.evaluation_handler = EvaluationHandler(self.current_database, self.config)
        self.candidate_network_handler = CandidateNetworkHandler(self.database_handler)
        self.evaluation_handler.load_golden_standards()

    def list_datasets(self):
        datasets = self.database_handler.get_databases()
        print(datasets)
        # datasets_folder = DefaultConfiguration.DATASETS_FOLDER
        # datasets_configurations = [(f.replace('.json', ''), join(datasets_folder, f)) for f in listdir(datasets_folder) if isfile(join(datasets_folder, f))]
        # for configuration in datasets_configurations:
        #     self.datasets_configurations[configuration[0]] = configuration[1] 

        # print(sorted(list(self.datasets_configurations.keys())))
    
    def list_querysets(self):
        querysets_folder = './querysets/' #DefaultConfiguration.QUERYSETS_FOLDER
        querysets_configurations = [(f.replace('.json', ''), join(querysets_folder, f)) for f in listdir(querysets_folder) if isfile(join(querysets_folder, f))]
        for configuration in querysets_configurations:
            self.querysets_configurations[configuration[0]] = configuration[1] 

        print(sorted(list(self.querysets_configurations.keys())))

    def use_database(self, database_name):
        self.current_database = database_name
        self.database_handler.set_database_name(self.current_database)

    def use_queryset(self, queryset_name):
        self.current_queryset = queryset_name
        with open(self.config.queryset_filepath, mode='r') as f:
            self._queryset = json.load(f)

    def create_indexes(self):
        self.index_handler.create_indexes()

    def load_indexes(self):
        self.index_handler.load_indexes()

    def run_queryset(self, **kwargs):
        results_filename = kwargs.get('results_filename',None)
        export_results = kwargs.get('export_results',False)
        approach = kwargs.get('approach','standard')
        preprocessed_results = kwargs.get('preprocessed_results',{})

        results =[]

        keywords_to_load = {keyword for item in self.get_queryset() for keyword in set(self.tokenizer.keywords(item['keyword_query']))}

        self.index_handler.load_indexes(keywords = keywords_to_load)

        for item in self.get_queryset():
            keyword_query = item['keyword_query']

            if keyword_query in preprocessed_results:
                result = preprocessed_results[keyword_query]
            else:
                result = self.keyword_search(keyword_query,**kwargs)
            results.append(result)

        data = {
            "database":self.config.connection['database'],
            "queryset":self.config.queryset_filepath,
            "results":results,
        }

        if export_results:
            if results_filename is None:
                results_filename = 'output.json'#next_path(f'{self.config.results_directory}{self.config.queryset_name}-{approach}-%03d.json')

            with open(results_filename,mode='w') as f:
                print(f'Writing results in {results_filename}')
                json.dump(data,f, indent = 4)

        return data

    def keyword_search(self, keyword_query=None, **kwargs):
        max_qm_size = kwargs.get('max_qm_size', self.max_qm_size)
        max_num_query_matches = kwargs.get('max_num_query_matches', self.max_num_query_matches)
        max_cjn_size = kwargs.get('max_cjn_size', self.max_cjn_size)
        topk_cns = kwargs.get('topk_cns', self.topk_cns)
        topk_cns_per_qm = kwargs.get('topk_cns_per_qm', self.topk_cns_per_qm)
        weight_scheme = kwargs.get('weight_scheme', 0)

        repeat = kwargs.get('repeat', 1)
        assume_golden_qms = kwargs.get('assume_golden_qms', False)
        
        input_desired_cn = kwargs.get('input_desired_cn', False)
        skip_cn_generations = kwargs.get('skip_cn_generations', False)
        show_kms_in_result = kwargs.get('show_kms_in_result', True)
        use_result_class = kwargs.get('use_result_class', True)

        weight_scheme = kwargs.get('weight_scheme', 3)

        if 'weight_scheme' in kwargs:
            del kwargs['weight_scheme']

        generated_query = None
        retrieved_documents = []

        elapsed_time = {
            'km':[],
            'skm':[],
            'vkm':[],
            'qm':[],
            'cn':[],
            'total':[],
        }

        if keyword_query is None:
            print(f'Please input a keyword query or choose one of the queries below:')
            for i,item in enumerate(self._queryset):
                keyword_query = item['keyword_query']
                print(f'{i+1:02d} - {keyword_query}')
            return None

        if isinstance(keyword_query, int):
            keyword_query=self._queryset[keyword_query - 1]['keyword_query']

        keywords = self.tokenizer.extract_keywords(keyword_query)
        keyword_query = KeywordQuery(keywords, keyword_query)

        for _ in range(repeat):
            
            if not assume_golden_qms:
                start_skm_time = timer()
                
                sk_matches = self.keyword_match_handler.schema_keyword_match_generator(
                    keyword_query,
                    self.index_handler.schema_index,
                )
                
                start_vkm_time = timer()
                vk_matches = self.keyword_match_handler.value_keyword_match_generator(
                    keyword_query,
                    self.index_handler.value_index,
                )
                # vk_matches = self.keyword_match_handler.filter_kwmatches_by_compound_keywords(vk_matches,compound_keywords)

                kw_matches = sk_matches + vk_matches
                start_qm_time = timer()

                query_matches = self.query_match_handler.generate_query_matches(
                    keyword_query.get_keywords(),
                    kw_matches,
                )
            else:
                start_skm_time = timer()
                start_vkm_time = timer()
                start_qm_time = timer()
                kw_matches = []
                query_matches = self.evaluation_handler.golden_standards[keyword_query]['query_matches']

            
            ranked_query_matches = self.query_match_handler.rank_query_matches(query_matches,
                self.index_handler.value_index,
                self.index_handler.schema_index,
                self.similarity,
                weight_scheme,
            )

            ranked_query_matches = ranked_query_matches[:max_num_query_matches]

            start_cn_time = timer()

            if input_desired_cn:
                desired_cn = self.evaluation_handler.golden_standards[keyword_query]['candidate_networks'][0]
                kwargs['desired_cn'] = desired_cn
            else:
                kwargs['desired_cn'] = None

            if not skip_cn_generations:
                ranked_cns = self.candidate_network_handler.generate_cns(
                    self.index_handler.schema_index,
                    self.index_handler.schema_graph,
                    ranked_query_matches,
                    keywords,
                    weight_scheme,
                        **kwargs,
                )

                if len(ranked_cns) > 0:
                    top_cn = ranked_cns[0]
                    base_collection, generated_query = top_cn.get_mongo_query_from_cn(
                        self.current_database,
                        self.index_handler.schema_graph,
                    ).build()
                    query_result = self.database_handler.execute(base_collection, generated_query)
                    retrieved_documents.extend(query_result)
            else:
                ranked_cns=[]

            end_cn_time = timer()

            elapsed_time['skm'].append(start_vkm_time - start_skm_time)
            elapsed_time['vkm'].append(start_qm_time - start_vkm_time)
            elapsed_time['km'].append(start_qm_time - start_skm_time)
            elapsed_time['qm'].append(start_cn_time - start_qm_time)
            elapsed_time['cn'].append(end_cn_time - start_cn_time)
            elapsed_time['total'].append(end_cn_time - start_skm_time)

        aggregated_elapsed_time = {phase:min(times) for phase,times in elapsed_time.items()}

        result = {
            # 'keyword_query': keyword_query,
            'keywords': list(keywords),
            # 'compound_keywords':list(compound_keywords),
            'query_matches':      [query_match.to_json_serializable()
                                  for query_match in ranked_query_matches],
            'candidate_networks': [candidate_network.to_json_serializable()
                                  for candidate_network in ranked_cns],
            'elapsed_time':       aggregated_elapsed_time,
            'num_keyword_matches':len(kw_matches),
            #consider len of unranked query matches
            'num_query_matches':  len(query_matches),
            'num_candidate_networks':  len(ranked_cns),
            'generated_query': generated_query,
        }

        if show_kms_in_result:
            result['value_keyword_matches'] = [vkm.to_json_serializable() for vkm in vk_matches]
            result['schema_keyword_matches']= [skm.to_json_serializable() for skm in sk_matches]

        return SereiaResult(self.current_database, self.index_handler, self.database_handler, result)
