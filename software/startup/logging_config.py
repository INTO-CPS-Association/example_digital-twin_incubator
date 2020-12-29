import logging


def config_logging(filename, level=logging.WARN):
    # noinspection PyArgumentList
    logging.basicConfig(level=level,
                        handlers=[
                            logging.FileHandler(filename),
                            logging.StreamHandler()
                        ],
                        format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s : %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )