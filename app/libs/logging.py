import logging
import logging.handlers as handlers


def create_logger():
    # create a logger object
    logger = logging.getLogger('www_webserver')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    log_handler = handlers.TimedRotatingFileHandler(
        'logs/server.log', when='D', interval=1, backupCount=0
    )
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(formatter)

    error_log_handler = handlers.RotatingFileHandler(
        'logs/server_err.log', maxBytes=5000, backupCount=0
    )
    error_log_handler.setLevel(logging.ERROR)
    error_log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)
    logger.addHandler(error_log_handler)

    return logger


logger = create_logger()
