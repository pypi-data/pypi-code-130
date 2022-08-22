import json
from timeit import default_timer as timer
from pprint import pprint as pp
import itertools

from nltk.data import retrieve
from nltk.corpus import wordnet as wn

from k2db.config import DefaultConfiguration
from k2db.database import DatabaseHandler, MongoHandler, MongoQueryExecutor
from k2db.utils import (
    ConfigHandler,
    KeywordQuery,
    Tokenizer,
    Similarity,
    get_logger,
    next_path,
)
from k2db.utils.utils import DictToSTupleFormatter, modify_retrieved_documents
from k2db.index import IndexHandler
from k2db.keyword_match import KeywordMatchHandler
from k2db.query_match import QueryMatchHandler
from k2db.candidate_network import CandidateNetworkHandler
from k2db.evaluation import EvaluationHandler

s = Similarity('')

logger = get_logger(__name__)
class Mapper:

    DATABASE_HANDLERS = {
        'mongo': MongoHandler,
        'postgres': DatabaseHandler,
    }

    def __init__(self, config = None):
        self.config = config
        if self.config is None:
            self.config = ConfigHandler()

        self.database_handler = self.DATABASE_HANDLERS.get(
            DefaultConfiguration.DATABASE_ENGINE
            )(DefaultConfiguration.DATABASE)
        self.index_handler = IndexHandler(self.database_handler)

        self.tokenizer = Tokenizer(tokenize_method = 'simple')
        self.index_handler.load_indexes()
        # print(f'SCHEMA GRAPH:\n{self.index_handler.schema_graph.str_edges_info()}')

        self.similarity = Similarity(self.index_handler.schema_index)
        self.keyword_match_handler = KeywordMatchHandler(self.similarity)
        self.query_match_handler = QueryMatchHandler()
        self.evaluation_handler = EvaluationHandler()
        self.candidate_network_handler = CandidateNetworkHandler(
            database_handler = self.database_handler
        )
        self.evaluation_handler.load_golden_standards()

    def load_queryset(self):
        with open(self.config.queryset_filepath,mode='r') as f:
            queryset = json.load(f)
        self.queryset = queryset

    def run_queryset(self,**kwargs):
        '''
        results_filename is declared here for sake of readability. But the
        default value is only set later to get a timestamp more accurate.
        '''
        results_filename = kwargs.get('results_filename',None)
        export_results = kwargs.get('export_results',False)
        approach = kwargs.get('approach','standard')
        preprocessed_results = kwargs.get('preprocessed_results',{})

        results =[]

        keywords_to_load = {keyword for item in self.queryset for keyword in set(self.tokenizer.keywords(item['keyword_query']))}

        self.index_handler.load_indexes(keywords = keywords_to_load)

        kwargs['queries_list'] = []

        for query_number, item in enumerate(self.queryset):
            keyword_query = item['keyword_query']
            kwargs['query_number'] = query_number

            # if query_number != 2:
            #     continue

            print(f'Running keyword search for query: {keyword_query}')
            if keyword_query in preprocessed_results:
                print('  Preprocessed results loaded')
                result = preprocessed_results[keyword_query]
            else:
                result = self.keyword_search(keyword_query,**kwargs)
            results.append(result)
        
        with open('generated_queries.json', 'w') as f:
            json.dump(kwargs['queries_list'], f, indent=2)

        data = {
            "database":self.config.connection['database'],
            "queryset":self.config.queryset_filepath,
            "results":results,
        }

        if export_results:
            if results_filename is None:
                results_filename = next_path(f'{self.config.results_directory}{self.config.queryset_name}-{approach}-%03d.json')

            with open(results_filename,mode='w') as f:
                logger.info(f'Writing results in {results_filename}')
                json.dump(data,f, indent = 4)

        return data


    def keyword_search(self,keyword_query,**kwargs):
        repeat = kwargs.get('repeat',1)
        assume_golden_qms = kwargs.get('assume_golden_qms',False)
        max_num_query_matches = kwargs.get('max_num_query_matches',5)
        input_desired_cn = kwargs.get('input_desired_cn',False)
        skip_cn_generations = kwargs.get('skip_cn_generations',False)

        # s.word_similarity('test', 'test', 'test')

        weight_scheme = kwargs.get('weight_scheme',3)
        #preventing to send multiple values for weight_scheme
        if 'weight_scheme' in kwargs:
            del kwargs['weight_scheme']

        elapsed_time = {
            'km':[],
            'skm':[],
            'vkm':[],
            'qm':[],
            'cn':[],
            'total':[],
        }

        keywords = self.tokenizer.extract_keywords(keyword_query)
        keyword_query = KeywordQuery(keywords, keyword_query)

        for _ in range(repeat):
            if not assume_golden_qms:
                start_skm_time = timer()
                sk_matches = self.keyword_match_handler.schema_keyword_match_generator(
                    keyword_query, self.index_handler.schema_index)
                logger.info('%d SKMs generated: %s',len(sk_matches),sk_matches)

                start_vkm_time = timer()
                vk_matches = self.keyword_match_handler.value_keyword_match_generator(
                    keyword_query, self.index_handler.value_index)
                # vk_matches = self.keyword_match_handler.filter_kwmatches_by_compound_keywords(vk_matches,compound_keywords)
                logger.info('%d VKMs generated: %s',len(vk_matches),vk_matches)

                start_qm_time = timer()
                print('Elapsed VKM: {}'.format(start_qm_time - start_vkm_time))
                kw_matches = sk_matches + vk_matches

                pp(kw_matches)

                # exit(1)

                query_matches = self.query_match_handler.generate_query_matches(
                    keyword_query.get_keywords(), kw_matches, **kwargs)
            else:
                start_skm_time = timer()
                start_vkm_time = timer()
                start_qm_time = timer()
                kw_matches = []
                query_matches = self.evaluation_handler.golden_standards[keyword_query]['query_matches']

            # print('Keyword Matches')
            # pp(kw_matches)

            ranked_query_matches = self.query_match_handler.rank_query_matches(query_matches,
                self.index_handler.value_index,
                self.index_handler.schema_index,
                self.similarity,
                weight_scheme,
            )

            # print('Query Matches')
            # for n, qm in enumerate(ranked_query_matches[:5]):
            #     print('QM #{}'.format(n))
            #     pp(qm)

            ranked_query_matches = ranked_query_matches[:max_num_query_matches]        

            logger.info('%d QMs generated: %s',len(ranked_query_matches),ranked_query_matches)

            if input_desired_cn:
                desired_cn = self.evaluation_handler.golden_standards[keyword_query]['candidate_networks'][0]
                kwargs['desired_cn'] = desired_cn
            else:
                kwargs['desired_cn'] = None

            if not skip_cn_generations:
                start_cn_time = timer()

                ranked_cns = self.candidate_network_handler.generate_cns(
                    self.index_handler.schema_index,
                    self.index_handler.schema_graph,
                    ranked_query_matches,
                    keyword_query.get_keywords(),
                    weight_scheme,
                    **kwargs,
                )

                for n, cn in enumerate(ranked_cns[:5]):
                    print('CN #{}'.format(n))
                    pp(cn)

                # exit(0)

                # logger.info('%d CNs generated: %s',len(ranked_cns),[(cn.score,cn) for cn in ranked_cns])
                end_cn_time = timer()

                retrieved_documents = []
                query_gen_time = None
                query_exec_time = None

                # pp(ranked_cns)
                top_cn_validation_size = kwargs.get('top_cn_validation_size', 1)

                for n, cn in enumerate(ranked_cns[:top_cn_validation_size]):
                    print(f"CN #{n}")
                    pp(cn)
                    # pp(cn.get_mongo_query_from_cn(self.index_handler.schema_graph).build())
                    if 'queries_list' in kwargs:
                        generate_query_start_time = timer()
                        base_collection, generated_query = cn.get_mongo_query_from_cn(
                            self.index_handler.schema_graph
                        ).build()
                        pp(generated_query)
                        # continue
                        generate_query_end_time = timer()
                        kwargs['queries_list'].append(
                            {
                                'query_number': kwargs['query_number'] + 1 if 'query_number' in kwargs else None,
                                'input_query': keyword_query.get_value(),
                                'base_collection': base_collection,
                                'mongo_query': generated_query,
                            }
                        )
                        query_executor = MongoQueryExecutor()
                        execute_query_start_time = timer()
                        retrieved_documents.extend(query_executor.execute(base_collection, generated_query))
                        execute_query_end_time = timer()

            else:
                ranked_cns=[]
            
            cn_count = len(ranked_cns)      

            elapsed_time['km'].append(   start_qm_time -start_skm_time)
            elapsed_time['skm'].append(  start_vkm_time-start_skm_time)
            elapsed_time['vkm'].append(  start_qm_time -start_vkm_time)
            elapsed_time['qm'].append(   start_cn_time -start_qm_time)
            elapsed_time['cn'].append(   end_cn_time   -start_cn_time)
            elapsed_time['total'].append(end_cn_time   -start_skm_time)

            print(elapsed_time['skm'])
            print(elapsed_time['vkm'])

        aggregated_elapsed_time = {phase:min(times) for phase,times in elapsed_time.items()}

        if retrieved_documents:
            query_gen_time = generate_query_end_time - generate_query_start_time
            query_exec_time = execute_query_end_time - execute_query_start_time
            modified_documents = modify_retrieved_documents(list(retrieved_documents))

        result = {
            'keyword_query':keyword_query.get_value(),
            'keywords':list(keywords),
            'query_number': kwargs['query_number'],
            # 'keyword_matches': [kw_match.to_json_serializable() 
                                # for kw_match in kw_matches],
            # 'compound_keywords':list(compound_keywords),
            'query_matches':      [query_match.to_json_serializable()
                                  for query_match in ranked_query_matches],
            'candidate_networks': [candidate_network.to_json_serializable()
                                  for candidate_network in ranked_cns],
            'generated_query': kwargs['queries_list'][-1]['mongo_query'] if 'queries_list' in kwargs else None,
            'retrieved_documents': modified_documents if retrieved_documents else retrieved_documents,
            'elapsed_time':       aggregated_elapsed_time,
            'num_keyword_matches':len(kw_matches),
            #consider len of unranked query matches
            'num_query_matches':  len(query_matches),
            'num_candidate_networks':  len(ranked_cns),
            'query_generation_time': query_gen_time,
            'query_execution_time': query_exec_time,
            'num_value_keyword_matches': len(vk_matches),
            'num_schema_keyword_matches': len(sk_matches),
            # 'qm_count': qm_count,
            # 'cn_count': cn_count,
        }

        # print('retrieved_documents')
        # pp(result['retrieved_documents'])

        return result
