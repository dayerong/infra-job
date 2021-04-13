#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from config.conf import log_config
import logging
import os


class Log(object):
    def __init__(self):
        self.logformat = log_config['logformat']
        self.filename = log_config['file']
        self.datefmt = log_config['datefmt']

    def info(self, loggername, logcontent):
        path = self.filename[0:self.filename.rfind("/")]
        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isfile(self.filename):
            f = open(self.filename, 'w')
            f.close()
        logging.basicConfig(filename=self.filename, format=self.logformat, datefmt=self.datefmt, level=logging.INFO)
        logger = logging.getLogger(loggername)
        logger.info(logcontent)
