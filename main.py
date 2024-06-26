import os
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
import requests

from utils.scrapper import Scrapper


def main() :
    os.system("cls")
    s = Scrapper()
    s.get_url_sale()

if __name__ == '__main__':
    main()
