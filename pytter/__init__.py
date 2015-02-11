import logging
from logging.handlers import SysLogHandler

__name__ = 'Pytter'
__version__ = '0.1'
__author__ = 'Emilio S. Carmo'
__website__ = 'http://github.com/emilio2hd/pytter'
__comment__ = 'A simple twitter watcher.'
__license__ = 'MIT'

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sh = SysLogHandler(address='/dev/log')
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger = logging.getLogger("Pytter")
logger.setLevel(logging.ERROR)
logger.addHandler(sh)