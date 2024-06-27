import json
import os
import pandas as pd
import json

from utils.scrapper import Scrapper


def main() :
    os.system("cls")
    s = Scrapper()
    s.start_scrapping()
    with open('data/houses.json', 'r') as file:  #just a little script to convert the "houses.json" to a .csv file easier to read
            data = json.load(file)
            df = pd.json_normalize(data, sep='_')
            df.to_csv("data/houses.csv",index=False)

if __name__ == '__main__':
    main()
