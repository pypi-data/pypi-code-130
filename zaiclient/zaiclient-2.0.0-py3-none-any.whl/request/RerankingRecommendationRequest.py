from zaiclient import config
from zaiclient.request.RecommendationRequest import MultipleMeta, RecommendationRequest

class RerankingRecommendationRequest(RecommendationRequest, metaclass=MultipleMeta):
    
    __default_offset = 0
    __default_recommendation_type = "category_page"
    
    def __init__(self, user_id: None, item_ids: list):
        super().__init__(len(item_ids), self.__default_offset, self.__default_recommendation_type, user_id, None, item_ids)
    
    def __init__(self, user_id: None, item_ids: list, limit: int):
        super().__init__(limit, self.__default_offset, self.__default_recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: None, item_ids: list, limit: int, offset: int):
        super().__init__(limit, offset, self.__default_recommendation_type, user_id, None, item_ids)
    
    def __init__(self, user_id: None, item_ids: list, limit: int, recommendation_type: str):
        super().__init__(limit, self.__default_offset, recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: None, item_ids: list, recommendation_type: str):
        super().__init__(len(item_ids), self.__default_offset, recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: None, item_ids: list, limit: int, offset: int, recommendation_type: str):
        super().__init__(limit, offset, recommendation_type, user_id, None, item_ids)
    
    def __init__(self, user_id: str, item_ids: list):
        super().__init__(len(item_ids), self.__default_offset, self.__default_recommendation_type, user_id, None, item_ids)
    
    def __init__(self, user_id: str, item_ids: list, limit: int):
        super().__init__(limit, self.__default_offset, self.__default_recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: str, item_ids: list, limit: int, offset: int):
        super().__init__(limit, offset, self.__default_recommendation_type, user_id, None, item_ids)
    
    def __init__(self, user_id: str, item_ids: list, limit: int, recommendation_type: str):
        super().__init__(limit, self.__default_offset, recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: str, item_ids: list, recommendation_type: str):
        super().__init__(len(item_ids), self.__default_offset, recommendation_type, user_id, None, item_ids)
        
    def __init__(self, user_id: str, item_ids: list, limit: int, offset: int, recommendation_type: str):
        super().__init__(limit, offset, recommendation_type, user_id, None, item_ids)
        
    def get_path(self, client_id: str) -> str:
        return config.ML_API_PATH_PREFIX.format(client_id) + config.RERANKING_RECOMMENDATION_PATH_PREFIX