import sys
from os.path import dirname

home_dir = dirname(dirname(__file__))
sys.path.append(home_dir)

from core.scraper import Scraper

scrp = Scraper()

