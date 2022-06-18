import logging
import os

LOGGING_BASE_DIR = "/tmp/dekk-logs"


def logger_main(file_name):

    os.makedirs(os.path.join(LOGGING_BASE_DIR, file_name), exist_ok=True)

    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        os.path.join(LOGGING_BASE_DIR, file_name, f"{os.path.basename(file_name)}.log")
    )
    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
