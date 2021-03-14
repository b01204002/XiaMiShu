# coding=utf-8

try:
    from bin.Utility.LittleTool import path_join
    from bin.Utility.Singleton import Singleton
except:
    from Utility.LittleTool import path_join
    from Utility.Singleton import Singleton
from logging import handlers
import logging


def initial_log(module_name, stream=False):
    logger = logging.getLogger(f'{module_name}')
    formatter = logging.Formatter(f'%(asctime)s - {module_name} - %(levelname)s - %(message)s')
    if logger.hasHandlers():
        logger.handlers.clear()

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    f_name = path_join('log', f'{module_name}.log')
    file_handler = handlers.RotatingFileHandler(filename=f_name, encoding='utf-8', maxBytes=2048000,
                                                backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    logger.info('********    Enter log in initial_log      ********')

    return logger


if __name__ == "__main__":
    l = initial_log('TEST')
    l.debug('This is test.')
