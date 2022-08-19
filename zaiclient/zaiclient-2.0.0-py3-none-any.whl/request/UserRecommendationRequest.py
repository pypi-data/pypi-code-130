from typing import Union
from zaiclient import config
from zaiclient.request.RecommendationRequest import MultipleMeta, RecommendationRequest

class UserRecommendationRequest(RecommendationRequest, metaclass=MultipleMeta):
    
    __default_offset = 0
    __default_recommendation_type = "homepage"
    
    def __init__(self, user_id: None, limit: int):
        super().__init__(limit, self.__default_offset, self.__default_recommendation_type, user_id)
    
    def __init__(self, user_id: None, limit: int, offset: int):
        super().__init__(limit, offset, self.__default_recommendation_type, user_id)
        
    def __init__(self, user_id: None, limit: int, recommendation_type: str):
        super().__init__(limit, self.__default_offset, recommendation_type, user_id)
    
    def __init__(self, user_id: None, limit: int, offset: int, recommendation_type: str):
        super().__init__(limit, offset, recommendation_type, user_id)
    
    def __init__(self, user_id: str, limit: int):
        super().__init__(limit, self.__default_offset, self.__default_recommendation_type, user_id)
    
    def __init__(self, user_id: str, limit: int, offset: int):
        super().__init__(limit, offset, self.__default_recommendation_type, user_id)
        
    def __init__(self, user_id: str, limit: int, recommendation_type: str):
        super().__init__(limit, self.__default_offset, recommendation_type, user_id)
    
    def __init__(self, user_id: str, limit: int, offset: int, recommendation_type: str):
        super().__init__(limit, offset, recommendation_type, user_id)
        

    def get_path(self, client_id: str) -> str:
        return config.ML_API_PATH_PREFIX.format(client_id) + config.USER_RECOMMENDATION_PATH_PREFIX