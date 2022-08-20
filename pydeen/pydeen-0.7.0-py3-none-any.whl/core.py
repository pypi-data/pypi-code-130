from cmath import exp
import logging

class PyDEEN:
    
    logging_initialized:bool=False
    logger_cache:dict={}
    logger_level = logging.INFO
    logger_filename = 'pydeen.log'
    logger_format = '%(asctime)s: %(levelname)s - %(name)s - %(message)s'

    @classmethod
    def register_connector(self, connector):
        print("connector registered")


    @classmethod
    def is_logging_initialized(cls) -> bool:
        return cls.logging_initialized

    @classmethod
    def set_logging_initialized(cls):
        """
            use this method to inform the PyDEEN Framework, that the logging is configured by an external process 
        """
        cls.logging_initialized = True    

    @classmethod
    def init_logging(cls) -> bool:
        if cls.is_logging_initialized():
            return True
        try:
            logging.basicConfig(level=cls.logger_level, filename=cls.logger_filename, format=cls.logger_format) #filemode='w', 
            logging.info('PyDEEN logger initialized')
            cls.logging_initialized = True
            return True    
        except Exception as exc:
            print(f"Error while initializig pydeen logging: {type(exc)} - {exc}")
            return False

    @classmethod
    def get_logger(cls, logging_id:str, create:bool=True, console_out:bool=True):
        if cls.is_logging_initialized() == False:
            cls.init_logging()
            if console_out == True:
                print("PyDEEN logging initialized")
        
        
        if cls.is_logger_available(logging_id) == True:
            return cls.logger_cache[logging_id]

        if create == False:
            return None

        logger = logging.getLogger(logging_id)
        if logger == None:
            return None

        cls.logger_cache[logging_id] = logger
        logging.debug(f"Logger initialized for {logging_id}")
        return logger    

    @classmethod
    def set_logger(cls, logging_id:str, logger):
        cls.logger_cache[logging_id] = logger

    @classmethod
    def is_logger_available(cls, logging_id:str) -> bool:
        if logging_id in cls.logger_cache.keys():
            return True
        else:
            return False
