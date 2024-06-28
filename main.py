import json
import os
import jsonlines
import pandas as pd
import json

from utils.scrapper import Scrapper
from utils.classifier import Classsifier


def main() :
    # os.system("cls")
    s = Scrapper()
    s.start_scrapping()
    s.save()
    
    r = Classsifier()
    r.create_dataframe()
    
if __name__ == '__main__':
    main()








