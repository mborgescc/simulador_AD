# -*- coding: utf-8 -*-

import logging

# Este método retorna um cliente de log
def get_client(module):
    logger = logging.getLogger(module)
    logger.setLevel(logging.INFO)

    op = logging.FileHandler("{}.log".format(module))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    op.setFormatter(formatter)

    logger.addHandler(op)
    return logger