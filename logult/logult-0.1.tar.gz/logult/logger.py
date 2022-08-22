import logging
import logging.config
from logult.utils import Cfg


def setup_logging(save_dir, exp_name=None, default_level=logging.INFO):
    config = Cfg.load_config_from_name()
    if exp_name is not None:
        config['handlers']['info_file_handler']['filename'] = exp_name
    for _, handler in config['handlers'].items():
        if 'filename' in handler:
            handler['filename'] = str(save_dir / handler['filename'])
    logging.config.dictConfig(config)

