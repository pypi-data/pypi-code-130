import json
from collections import Counter
from queue import deque

from sereia.keyword_match import KeywordMatch
from sereia.utils import (
    Graph,
    MongoQueryBuilder,
    AttributeTreeGenerator,
    load_datasets_ids_from_json,
)


class CandidateNetwork(Graph):
    def __init__(self, graph_dict=None):
        self.score = None
        self.__root = None

        super().__init__(graph_dict)

        if len(self)>0:
            self.set_root()

    def get_root(self):
        return self.__root

    def set_root(self,vertex=None):
        if len(self) == 0:
            return None

        if vertex is not None:
            keyword_match,_ = vertex
            if not keyword_match.is_free():
                self.__root = vertex
                return vertex
            else:
                return None
        else:         
            for candidate in self.vertices():
                keyword_match,_ = candidate
                if not keyword_match.is_free():
                    self.__root = candidate
                    return candidate
        
        print('The root of a Candidate Network cannot be a Keyword-Free Match.')
        print(self)
        raise ValueError('The root of a Candidate Network cannot be a Keyword-Free Match.')
    
    def reset_root(self, to_value=True):
        if to_value:
            for leaf in self.leaves():
                keyword_match, _ = leaf
                if keyword_match.has_value_mappings():
                    self.__root = leaf

    def get_starting_vertex(self):
        if len(self)==0:
            return None

        if self.__root is None:
            self.set_root()
        return self.__root

    def get_starting_vertex(self, rev):
        if len(self) == 0:
            return None

        if self.__root is None:
            self.set_root()
        return self.__root
        
    def add_vertex(self, vertex):
        results = super().add_vertex(vertex)
        if self.__root is None:
            self.set_root(vertex)
        return results

    def add_keyword_match(self, heyword_match, **kwargs):
        alias = kwargs.get('alias', 't{}'.format(self.__len__()+1))
        vertex = (heyword_match, alias)
        return self.add_vertex(vertex)

    def add_adjacent_keyword_match(self,parent_vertex,keyword_match,edge_direction='>',**kwargs):
        child_vertex = self.add_keyword_match(keyword_match,**kwargs)
        self.add_edge(parent_vertex,child_vertex,edge_direction=edge_direction)

    def keyword_matches(self):
        for keyword_match,_ in self.vertices():
            yield keyword_match

    def non_free_keyword_matches(self):
        for keyword_match,_ in self.vertices():
            if not keyword_match.is_free():
                yield keyword_match

    def num_free_keyword_matches(self):
        i=0
        for keyword_match,_ in self.vertices():
            if keyword_match.is_free():
                i+=1
        return i

    def reciprocal_neighbors(self,schema_graph,vertex):
        keyword_match,_ = vertex
        for neighbor_vertex in self.incoming_neighbors(vertex):
            neighbor_km,_ = neighbor_vertex

            edge_info = schema_graph.get_edge_info(
                neighbor_km.table,
                keyword_match.table
            )            
            for _,(cardinality,_) in edge_info.items():
                if cardinality=='1:1':
                    yield neighbor_vertex
        

    def is_sound(self,schema_graph):
        if len(self) < 3:
            return True

        def has_duplicate_tables(neighbors):
            if len(neighbors)>=2:
                tables = set()
                for neighbor_km,_ in neighbors:
                    if neighbor_km.table not in tables:
                        tables.add(neighbor_km.table)
                    else:
                        return True
            return False

        for vertex in self.vertices():
            outgoing_neighbors = list(self.outgoing_neighbors(vertex))
            if has_duplicate_tables(outgoing_neighbors):
                return False

            reciprocal_neighbors = list(self.reciprocal_neighbors(schema_graph,vertex))
            if has_duplicate_tables(reciprocal_neighbors):
                return False
        return True


    def remove_vertex(self,vertex):
        _,incoming_neighbors = self._graph_dict[vertex]
        for neighbor in incoming_neighbors:
            self._graph_dict[neighbor][0].remove(vertex)
        self._graph_dict.pop(vertex)

    def is_total(self,query_match):
        return set(self.non_free_keyword_matches())==set(query_match)

    def contains_keyword_free_match_leaf(self):
        for vertex in self.leaves():
            keyword_match,_ = vertex
            if keyword_match.is_free():
                return True
        return False

    def minimal_cover(self,query_match):
        return self.is_total(query_match) and not self.contains_keyword_free_match_leaf()

    def unaliased_edges(self):
        for (keyword_match,_),(neighbor_keyword_match,_) in self.edges():
            yield (keyword_match,neighbor_keyword_match)

    def calculate_score(self, query_match):
        self.score = query_match.total_score/len(self)

    def get_qm_score(self):
        return self.score*len(self)

    def __eq__(self, other):

        if not isinstance(other,CandidateNetwork):
            return False
        
        self_root_km,_  = self.__root
        other_root_km,_= other.get_root()

        other_hash = None

        if self_root_km==other_root_km:
            other_hash = hash(other)
        else:            
            for keyword_match,alias in other.vertices():
                if self_root_km == keyword_match:
                    root = (keyword_match,alias)
                    other_hash = other.hash_from_root(root)
        
        if other_hash is None:
            return False

        return hash(self)==other_hash

    def __hash__(self):
        if len(self)==0:
            return hash(None)
        if self.__root is None:
            self.set_root()
        return self.hash_from_root(self.__root)   


    def hash_from_root(self,root):
        hashable = []

        level = 0       
        visited = set()

        queue = deque()
        queue.append( (level,root) )

        while queue:
            level,vertex = queue.popleft()
            keyword_match,alias = vertex
            children = Counter()
            visited.add(alias)
            
            for adj_vertex in self.neighbors(vertex):
                adj_km,adj_alias = adj_vertex
                if adj_alias not in visited:
                    queue.append( (level+1,adj_vertex) )
                    children[adj_km]+=1
                
            if len(hashable)<level+1:
                hashable.append(set())
            
            hashable[level].add( (keyword_match,frozenset(children.items())) )

        hashcode = hash(tuple(frozenset(items) for items in hashable))
        return hashcode   

    def __repr__(self):
        if len(self)==0:
            return 'EmptyCN'
        print_string = ['\t'*level+direction+str(vertex[0])  for direction,level,vertex in self.leveled_dfs_iter()]
        return '\n'.join(print_string)

    def to_json_serializable(self):
        return [{'keyword_match':keyword_match.to_json_serializable(),
            'alias':alias,
            'outgoing_neighbors':[alias for (km,alias) in outgoing_neighbors],
            'incoming_neighbors':[alias for (km,alias) in incoming_neighbors]}
            for (keyword_match,alias),(outgoing_neighbors,incoming_neighbors) in self._graph_dict.items()]

    def to_json(self):
        return json.dumps(self.to_json_serializable())

    @staticmethod
    def from_json_serializable(json_serializable_cn):
        alias_hash ={}
        edges=[]
        for vertex in json_serializable_cn:
            keyword_match = KeywordMatch.from_json_serializable(vertex['keyword_match'])
            alias_hash[vertex['alias']]=keyword_match

            for outgoing_neighbor in vertex['outgoing_neighbors']:
                edges.append( (vertex['alias'],outgoing_neighbor) )

        candidate_network = CandidateNetwork()
        for alias,keyword_match in alias_hash.items():
            candidate_network.add_vertex( (keyword_match,alias) )
        for alias1, alias2 in edges:
            vertex1 = (alias_hash[alias1],alias1)
            vertex2 = (alias_hash[alias2],alias2)
            candidate_network.add_edge(vertex1,vertex2)

        return candidate_network

    @staticmethod
    def from_json(json_cn):
        return CandidateNetwork.from_json_serializable(json.loads(json_cn))

    def get_mongo_query_from_cn(self, database_name, schema_graph):
        selected_attributes = set()
        selected_tables = []

        next_step_lookup_field = None
        last_added_collection = None

        datasets_collection_ids_dict = load_datasets_ids_from_json()

        query = MongoQueryBuilder(database_name)
        self.reset_root(to_value=True)

        fields_to_project = []

        for prev_vertex, direction, vertex in self.dfs_pair_iter(root_predecessor=True, rev=False, start_vertex=self.__root):
            keyword_match, alias = vertex
            project_fields = []
            value_fields = []

            tree_generator = AttributeTreeGenerator()

            for type_km, _, attribute, keywords in keyword_match.mappings():
                selected_attributes.add(f'{alias}.{attribute}')
                if type_km == 'v':
                    for keyword in keywords:
                        if isinstance(keyword, str):
                            sql_keyword = keyword.replace('\'', '\'\'')
                            value_fields.append((attribute, sql_keyword))
                        elif isinstance(keyword, frozenset):
                            # print('Found froze: {}'.format(keyword))
                            value_fields.append((attribute, keyword))
                            # exit(0)
                    continue

            if prev_vertex is None:
                query.set_starting_collection(keyword_match.table)
                selected_tables.append(f'{keyword_match.table} {alias}')
                edge_info = schema_graph.get_edge_info(keyword_match.table,
                                                       keyword_match.table)
                if edge_info:
                    for constraint in edge_info:
                        _, attribute_mappings = edge_info[constraint]
                        if type(attribute_mappings) != list:
                            l = []
                            l.append(attribute_mappings)
                            attribute_mappings = l
                        for constraint_column, foreign_column in attribute_mappings:
                            project_fields.append(constraint_column)
                for value_field in value_fields:
                    tree_generator.add_attribute(value_field[0], value_field[1])
                tree_generator.generate()
                query.new_match_v3(keyword_match.table, tree_generator.generate())
            else:
                _, prev_alias = prev_vertex
                if direction == '>':
                    constraint_keyword_match, constraint_alias = prev_vertex
                    foreign_keyword_match, foreign_alias = vertex
                else:
                    constraint_keyword_match, constraint_alias = vertex
                    foreign_keyword_match, foreign_alias = prev_vertex

                edge_info = schema_graph.get_edge_info(constraint_keyword_match.table,
                                                       foreign_keyword_match.table)

                for constraint in edge_info:
                    _, attribute_mappings = edge_info[constraint]

                    if type(attribute_mappings) != list:
                        l = []
                        l.append(attribute_mappings)
                        attribute_mappings = l

                    if last_added_collection == keyword_match.table:
                        continue

                    if not next_step_lookup_field:
                        constraint_column, foreign_column = attribute_mappings[0]
                        query.lookup(constraint_column, foreign_column,
                                     keyword_match.table, keyword_match.table)
                    else:
                        constraint_column, foreign_column = attribute_mappings[0]
                        query.lookup(f'{next_step_lookup_field}.{constraint_column}',
                                     foreign_column, keyword_match.table, keyword_match.table)

                if last_added_collection != keyword_match.table:
                    query.unwind(keyword_match.table, insert=True)
                    if value_fields:
                        for attribute, sql_keyword in value_fields:
                            attribute_name = keyword_match.table + '.' + attribute
                            tree_generator.add_attribute(attribute, sql_keyword)
                        query.new_match_v3(keyword_match.table, tree_generator.generate())
                        next_step_lookup_field = keyword_match.table
                    else:
                        next_step_lookup_field = keyword_match.table
                else:
                    for attribute, sql_keyword in value_fields:
                        tree_generator.add_attribute(attribute, sql_keyword)
                    query.new_match_v3(keyword_match.table, tree_generator.generate())

            if next_step_lookup_field:
                if keyword_match.table in datasets_collection_ids_dict[database_name]:
                    for attribute in datasets_collection_ids_dict[database_name][keyword_match.table]:
                        fields_to_project.append(
                            next_step_lookup_field + '.' + attribute,
                        )
            else:
                fields_to_project.append(datasets_collection_ids_dict[database_name][keyword_match.table][0])
            
            last_added_collection = keyword_match.table

        query.project(
            fields_to_project,
        )

        return query
