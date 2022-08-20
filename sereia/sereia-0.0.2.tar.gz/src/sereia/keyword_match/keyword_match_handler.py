import itertools
import re
from timeit import default_timer as timer
from pprint import pprint as pp

from nltk.stem import WordNetLemmatizer

from sereia.utils import ConfigHandler,get_logger, Similarity
from .keyword_match import KeywordMatch

w = WordNetLemmatizer()
w.lemmatize('clique')
w.lemmatize('businesses')
w.lemmatize('tips')
w.lemmatize('cities')

logger = get_logger(__name__)
class KeywordMatchHandler:
    def __init__(self, similarity):
        self.config = ConfigHandler()
        self.similarities = similarity

    def get_keyword_matches(self, keywords, value_index, schema_index,**kwargs):
        sk_matches = self.schema_keyword_match_generator(keywords, schema_index)
        vk_matches = self.value_keyword_match_generator(keywords, schema_index)
        return sk_matches+vk_matches

    def value_keyword_match_generator(self, Q,value_index,**kwargs):

        ignored_collections = kwargs.get('ignored_collections',[])
        ignored_attributes = kwargs.get('ignored_attributes',[])

        #Input:  A keyword query Q=[k1, k2, . . . , km]
        #Output: Set of non-free and non-empty tuple-sets Rq

        '''
        The tuple-set Rki contains the tuples of Ri that contain all
        terms of K and no other keywords from Q
        '''

        #Part 1: Find sets of tuples containing each keyword
        P = {}
        logger.debug("Processing keyword values")
        start = timer()
        for keyword in Q.get_parsed_value():

            if isinstance(keyword, list):
                for term in keyword:
                    if not self.is_keyword_stored_in_index(term, value_index):
                        continue
                
                self.generate_compound_value_keyword_match(
                    keyword,
                    value_index,
                    P,
                    ignored_collections,
                    ignored_attributes,
                )

                continue
            elif not self.is_keyword_stored_in_index(keyword, value_index):
                    continue

            #TODO: we have a new condition, that is the ocurrence of compound keywords represented as lists in the parsed keyword query
            #TODO: I think we must use sets to get all ctids from terms in the list, then pass it to P[vkm] as if it were a single keyword query term

            for table in value_index[keyword]:
                if table in ignored_collections:
                    continue

                for (attribute,ctids) in value_index[keyword][table].items():
                    if (table,attribute) in ignored_attributes:
                        continue

                    vkm = KeywordMatch(table, value_filter={attribute:{keyword}})
                    P[vkm] = set(ctids)
        
        # print('Time to generate partial matches: {}'.format(timer() - start))

        #Part 2: Find sets of tuples containing larger termsets
        P = self.disjoint_itemsets(P)

        # print('Total time: {}'.format((timer() - start)* 1000))

        #Part 3: Ignore tuples
        return list(P)

    def generate_compound_value_keyword_match(self, compound_query_segment, value_index, document_set, ignored_collections, ignored_attributes):
        matches_data = {}
        keyword_to_attributes = {}
        attributes_intersection = set([])
        # table to ctids data (the compound keyword matches must have the union of ctids)

        for keyword in compound_query_segment:
            if keyword not in keyword_to_attributes:
                keyword_to_attributes[keyword] = set([])
            for collection in value_index[keyword]:
                if collection in ignored_collections:
                    continue

                if collection not in matches_data:
                    matches_data[collection] = {}

                for (attribute, ctids) in value_index[keyword][collection].items():
                    if (collection, attribute) in ignored_attributes:
                        continue

                    keyword_to_attributes[keyword].add(attribute)

                    if attribute not in matches_data[collection]:
                        # TODO:
                        matches_data[collection][attribute] = set(ctids)
                        continue

                    # TODO: resolver a intersecao dos termos no dict

                    matches_data[collection][attribute] = matches_data[collection][attribute].intersection(
                        set(ctids),
                    )
        
        # TODO: aqui, nao necessariamente eles ocorreram juntos, apenas ocorreram no mesmo atributo mas podem ter sido em documentos diferentes
        for keyword in keyword_to_attributes:
            if len(attributes_intersection) == 0:
                attributes_intersection = keyword_to_attributes[keyword]
                continue

            attributes_intersection = attributes_intersection.intersection(
                keyword_to_attributes[keyword])

        # print('keyword to attribute')
        # pp(keyword_to_attributes)
        # print('attributes intersection')
        # pp(attributes_intersection)
        # print('matched data')
        # pp(matches_data)

        for collection in matches_data:
            for attribute in matches_data[collection]:
                # print(collection, attribute)
                if attribute not in attributes_intersection or len(matches_data[collection][attribute]) == 0:
                    print('attribute not in intersection or empty: {}'.format(attribute))
                    continue
                vkm = KeywordMatch(collection, value_filter={
                                    attribute: {frozenset(compound_query_segment)}})
                document_set[vkm] = matches_data[collection][attribute]

    def disjoint_itemsets(self, pool):
        #Input: A Set of non-empty tuple-sets for each keyword alone P
        #Output: The Set P, but now including larger termsets (process Intersections)

        '''
        Termset is any non-empty subset K of the terms of a query Q
        '''
        
        delayed_removal = {}
        next_stage_pool = {}
        
        for ( vkm_i , vkm_j ) in itertools.combinations(pool,2):
            if vkm_i.table == vkm_j.table:
                joint_tuples = pool[vkm_i] & pool[vkm_j]

                if len(joint_tuples)>0:

                    joint_predicates = {}

                    for attribute, keywords in vkm_i.value_filter:
                        joint_predicates.setdefault(attribute,set()).update(keywords)

                    for attribute, keywords in vkm_j.value_filter:
                        joint_predicates.setdefault(attribute,set()).update(keywords)

                    vkm_ij = KeywordMatch(vkm_i.table,value_filter=joint_predicates)
                    next_stage_pool[vkm_ij] = joint_tuples

                    delayed_removal.setdefault(vkm_i,set()).update(joint_tuples)
                    delayed_removal.setdefault(vkm_j,set()).update(joint_tuples)

        for vkm_k in delayed_removal:
            tuples_to_remove = delayed_removal[vkm_k]
            pool[vkm_k].difference_update(tuples_to_remove)
            if len(pool[vkm_k])==0:
                del pool[vkm_k]

        if len(next_stage_pool)>0:
            pool.update(self.disjoint_itemsets(next_stage_pool))
        return pool

    def schema_keyword_match_generator(self, Q, schema_index,**kwargs):
        ignored_collections = kwargs.get('ignored_collections',[])
        ignored_attributes = kwargs.get('ignored_attributes',[])
        threshold = kwargs.get('threshold',1)
        keyword_matches_to_ignore = kwargs.get('keyword_matches_to_ignore',set())

        S = []
        logger.debug("Processing schema matches")
        start_skm_time = timer()
        lemmatizer = WordNetLemmatizer()
        for keyword in Q.get_parsed_value():
            if isinstance(keyword, list):
                continue

            for table in schema_index:
                if table in ignored_collections:
                    continue

                for attribute in itertools.chain('*', schema_index[table].keys() ):

                    if (
                        attribute=='id' or
                        (table,attribute) in ignored_attributes or
                        attribute==table
                        ):
                        continue

                    leaf_attribute = attribute.split('.')[-1]
                    lemmatized_attribute = lemmatizer.lemmatize(keyword)
                    if attribute == '*' and lemmatized_attribute == table:
                        sim = 1.0
                    elif lemmatized_attribute == leaf_attribute:
                        # print(lemmatized_attribute, table, leaf_attribute)
                        # print('sim 1')
                        sim = 1.0
                    else:
                        sim = 0.0
                        # else:
                        # sim = 0.0
                    # start = timer()
                    # bigger_time = 0.0
                    # for _ in range(2):
                        # sim_start_time = timer()
                            # sim = self.similarities.word_similarity(
                            #     keyword, table, leaf_attribute)
                        # sim_end_time = timer()
                        # if (sim_end_time - sim_start_time) > bigger_time:
                        #     bigger_time = sim_end_time - sim_start_time
                        #     print(bigger_time)
                    # start_skm_time += bigger_time
                    # print('Total time for similarity: {:.5f}'.format(timer() - start))
                    logger.debug("similarity : {} threshold: {}".format(sim, threshold))
                    if sim >= threshold:
                        logger.info(f"found a KWmatch for {keyword} in {table}.{attribute} with score: {sim}")
                        skm = KeywordMatch(table,schema_filter={attribute:{keyword}})
                        if skm not in keyword_matches_to_ignore:
                            S.append(skm)
            
            # print('Total SKM time: {}'.format(timer() - start_skm_time))
        return S

    def filter_kwmatches_by_compound_keywords(self, vk_matches, compound_keywords):
        '''
        Value-keyword matches which contains only part of a compound_keyword are
        pruned.
        '''
        if len(compound_keywords)==0:
            return vk_matches

        filtered_vk_matches = set()
        for value_keyword_match in vk_matches:
            must_remove = False
            set_a = set(value_keyword_match.keywords())

            for compound_keyword in compound_keywords:
                set_b = set(compound_keyword)

                set_ab = set_a | set_b
                if len(set_ab)>0 or len(set_ab)<len(set_a):
                    must_remove = True

            if not must_remove:
                filtered_vk_matches.add(value_keyword_match)

        return filtered_vk_matches

    def is_keyword_stored_in_index(self, keyword, index):
        if keyword in index:
            return True
        
        return False
