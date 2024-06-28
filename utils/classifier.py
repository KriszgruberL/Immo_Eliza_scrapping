import pandas as pd
import json
import jsonlines


class Classsifier:
    def create_dataframe(self):
        with open('data/houses.json', 'r') as file:  #just a little script to convert the "houses.json" to a .csv file easier to read
            data = json.loads(file.read())
            df = pd.json_normalize(data, sep='_')
            df.to_csv("data/houses.csv",index=False)
        # data = []
        # with jsonlines.open('data/houses.jsonl', 'r') as reader:
        #     for obj in reader:
        #         data.append(obj)
        #     df = pd.jsonnormalize(data, sep='')
        #     df.to_csv("data/houses.csv", index=False)