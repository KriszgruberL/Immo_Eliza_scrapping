import pandas as pd
import json

class Classsifier:
    """
    A class used to represent a Classifier that handles data operations.

    Methods
    -------
    create_dataframe():
        Reads a JSON file, normalizes it into a pandas DataFrame, and saves it as a CSV file.
    """
    
    def create_dataframe(self):
        """
        Reads a JSON file containing house data, normalizes the JSON structure into a flat 
        pandas DataFrame, and saves the DataFrame as a CSV file.

        The method reads from 'data/houses.json' and writes to 'data/houses.csv'.
        """
        with open('data/houses.json', 'r') as file:  
            data = json.loads(file.read())
            df = pd.json_normalize(data, sep='_')
            
            # Replace NaN values (resulting from JSON null values) with 'NULL'
            df = df.where(pd.notnull(df), 'NULL')
            
            df.to_csv("data/houses.csv",index=False)
        