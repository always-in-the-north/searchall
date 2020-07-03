import logging
import sys

_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s " + "filename: " + " %(filename)s " 
                                                                + "module: " + "%(module)s " 
                                                                + "funcName: " + "%(funcName)s " 
                                                                + "lineno: " + "%(lineno)d : %(message)s",
                               datefmt="%Y-%m-%d - %H:%M:%S")

_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s : %(message)s",
                               datefmt="%Y-%m-%d - %H:%M:%S")

_ch = logging.StreamHandler(sys.stdout)
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_formatter)

_fh = logging.FileHandler("E:\\python\\manhua\\mylog.log", "w")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(_formatter)

logger = logging.getLogger('manhua')
logger.setLevel(logging.DEBUG)

logger.addHandler(_ch)
logger.addHandler(_fh)
