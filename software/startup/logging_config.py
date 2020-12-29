import logging


def config_logging(filename=None, level=logging.WARN):
    if filename is not None:
        # noinspection PyArgumentList
        logging.basicConfig(level=level,
                            handlers=[
                                logging.FileHandler(filename),
                                logging.StreamHandler()
                            ],
                            format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s : %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S'
                            )
    else:
        # noinspection PyArgumentList
        logging.basicConfig(level=level,
                            format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s : %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S'
                            )
