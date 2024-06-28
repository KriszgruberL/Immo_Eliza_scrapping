import pandas as pd
import json
import jsonlines


class Classsifier:
    def create_dataframe(self):
        with open('data/houses.json', 'r') as file:  
            data = json.loads(file.read())
            df = pd.json_normalize(data, sep='_')
            df.to_csv("data/houses.csv",index=False)
        