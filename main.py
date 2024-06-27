import os
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json
import re

from utils.scrapper import Scrapper


def main() :
    os.system("cls")
    s = Scrapper()
    s.get_url_sale()
    s.save()
    with open('houses.json', 'r') as file:  #just a little script to convert the "houses.json" to a .csv file easier to read
            data = json.load(file)
            df = pd.json_normalize(data, sep='_')
            df.to_csv("houses.csv",index=False)

if __name__ == '__main__':
    main()
