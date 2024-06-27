import os
import pandas as pd

from utils.scrapper import Scrapper


def main() :
    os.system("cls")
    s = Scrapper()
    s.start_scrapping()

if __name__ == '__main__':
    main()
