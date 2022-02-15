import logging, os
from datetime import date

dir = os.path.dirname(__file__)

def call_logger():
    logger_uses = setup_logger('logger_uses', os.path.join(dir, 'logs/{}/uses.log'.format(date.today())))
    logger_visits = setup_logger('logger_visits', os.path.join(dir, 'logs/{}/visits.log'.format(date.today())))

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # Checking if the folder exists or not
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger