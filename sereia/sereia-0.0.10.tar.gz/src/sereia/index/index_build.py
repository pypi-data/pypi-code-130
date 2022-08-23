from pathlib import Path

from sereia.index.index_handler import IndexHandler
from sereia.database import MongoHandler
from sereia.utils import ConfigHandler


if __name__ == "__main__":
    database = 'imdb'
    print(f'Indexing database {database}')
    
    # TODO: check if the tmp/datasets/ folder path exist
    index_folder = './tmp/datasets/{}/'.format(
        database,
    )
    Path(index_folder).mkdir(parents=True, exist_ok=True)

    dataset_config_filepath = f'./datasets_config/{database}.json'
    config = ConfigHandler(
        config_directory='./config/',
        reset=True, dataset_config_filepath=dataset_config_filepath)
    config.set_logging_level('INFO')
    
    indexHandler = IndexHandler(
        MongoHandler(
            database,
        ), 
        config=config,
    )
    indexHandler.create_indexes()
