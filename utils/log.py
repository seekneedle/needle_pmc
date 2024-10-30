import logging
import os
from .config import config


def get_log():
    path = os.path.join(os.path.dirname(__file__), '..', 'output')
    if not os.path.exists(path):
        os.mkdir(path)
    level = logging.INFO if config['log_level'] == 'info' else logging.DEBUG
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(os.path.dirname(__file__), '..', 'output', 'server.log')
    )
    return logging


log = get_log()
