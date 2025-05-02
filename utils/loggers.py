import logging

DJANGO_LOGGER = 'django_logger'
DEBUG_LOGGER = 'debug_logger'
INFO_LOGGER = 'info_logger'
WARNING_LOGGER = 'warning_logger'
ERROR_LOGGER = 'error_logger'

logger_info = logging.getLogger(INFO_LOGGER)
logger_debug = logging.getLogger(DEBUG_LOGGER)
logger_warning = logging.getLogger(WARNING_LOGGER)
logger_error = logging.getLogger(ERROR_LOGGER)
logger_django = logging.getLogger(DJANGO_LOGGER)


logger_info.log(logging.INFO, 'This is an info message')

def log_debug(message):
    logger_debug.log(logging.DEBUG, message)

def log_info(message):
    logger_info.log(logging.INFO, message)

def log_warning(message):
    logger_warning.log(logging.WARNING, message)

def log_error(message):
    logger_error.log(logging.ERROR, message)

def log_django(message):
    logger_django.log(logging.INFO, message)

