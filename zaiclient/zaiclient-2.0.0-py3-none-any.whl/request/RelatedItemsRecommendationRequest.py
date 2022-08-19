from zaiclient import config
from zaiclient.request.RecommendationRequest import MultipleMeta, RecommendationRequest

class RelatedItemsRecommendationRequest(RecommendationRequest, metaclass=MultipleMeta):
    
    __default_offset = 0
    __default_recommendation_type = "product_detail_page"
    
    def __init__(self, item_id: str, limit: int):
        super().__init__(limit, self.__default_offset, self.__default_recommendation_type, None, item_id)
    
    def __init__(self, item_id: str, limit: int, offset: int):
        super().__init__(limit, offset, self.__default_recommendation_type, None, item_id)
        
    def __init__(self, item_id: str, limit: int, recommendation_type: str):
        super().__init__(limit, self.__default_offset, recommendation_type, None, item_id)
    
    def __init__(self, item_id: str, limit: int, offset: int, recommendation_type: str):
        super().__init__(limit, offset, recommendation_type, None, item_id)
    
    def get_path(self, client_id: str) -> str:
        return config.ML_API_PATH_PREFIX.format(client_id) + config.RELATED_ITEMS_RECOMMENDATION_PATH_PREFIX