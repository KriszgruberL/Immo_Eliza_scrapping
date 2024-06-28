import os

from utils.scrapper import Scrapper
from utils.classifier import Classsifier


def main() :
    """
    The main function to execute the web scraping and data processing pipeline.
    
    This function performs the following steps:
    1. Initializes the Scrapper class and starts the web scraping process.
    2. Saves the scraped data.
    3. Initializes the Classifier class and creates a DataFrame from the saved data.
    """
    # Clear the console screen (commented out)
    # os.system("cls")
    
    # Initialize the Scrapper and start scraping
    s = Scrapper()
    s.start_scrapping()
    s.save()
    
    # Initialize the Classifier and create a DataFrame from the scraped data
    r = Classsifier()
    r.create_dataframe()
    
if __name__ == '__main__':
    main()








