import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

from utils.scrapper import Scrapper


def main() :
    s = Scrapper()
    s.set_up()

if __name__ == '__main__':
    main()
