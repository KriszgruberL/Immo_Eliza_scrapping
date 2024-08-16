# Immo_Eliza




<p align="center">
    <br>
    <a href="https://github.com/KriszgruberL" target="_blank"> <img alt="Made with Frogs" src="./assets/made-with-🐸.svg" style="border-radius:0.5rem"></a>
    <a href="https://github.com/antoineservais1307"><img alt="In collaboration with antoineservais1307" src="./assets/in-collaboration-with-antoineservais1307.svg" style="border-radius:0.5rem; margin-left : 0.5rem"></a>
    <br>
    <br><br>
    <a><img src="./assets/logo-modified.png" width="350"  /></a>
    <h2 align="center">Using:
    <br>
    <br>
    <a href="https://www.python.org/downloads/release/python-3120/"><img alt="Python 3.12" src="https://img.shields.io/badge/Python%203.12-python?style=for-the-badge&logo=python&logoColor=F8E71C&labelColor=427EC4&color=2680D1" style="border-radius:0.5rem"></a>
    <a href="https://www.crummy.com/software/BeautifulSoup/"><img alt="Beautiful soup" src="https://img.shields.io/badge/Beautiful_Soup-Beautiful_Soup?style=for-the-badge&color=2FB3B6" style="border-radius:0.5rem"></a>
    <a href="https://pandas.pydata.org/docs/"><img alt="Pandas" src="https://img.shields.io/badge/Pandas-Pandas?style=for-the-badge&logo=pandas&color=61B3DD" style="border-radius:0.5rem"></a>
    <br>
</p>

## BeCode red line project - Immo_Eliza 1/4

1. [Scrapping](https://github.com/KriszgruberL/Immo_Eliza)
2. [Data Analysis](https://github.com/KriszgruberL/Immo_Eliza_Data_Analysis)
3. [Preprocessing and Machine Learning](https://github.com/KriszgruberL/Immo_eliza_ML)
4. [API and Deployment](https://github.com/KriszgruberL/Immo_Eliza_front)

## 📚 Overview

This project is a real estate web scraper that collects data on properties for sale and rent from Immoweb. It extracts details about each property, including price, location, type, and various features, and saves this data into JSON and CSV formats for further analysis.

## 🕺 Collaborator
Thank you Antoine Servais for your contribution to this project:

- [antoineservais1307](https://github.com/antoineservais1307)

## 🚧 Project Structure

<div style="display: flex; align-items :center">

<div style="flex: 0.5; padding-right: 1%;">

    .
    ├── .venv/
    ├── .vscode/
    │   ├── settings.json
    ├── assets/
    │   └── logo.webp
    ├── data/
    │   ├── __init__.py
    │   ├── Data_house.xlsx
    │   ├── houses.csv
    │   └── houses.json
    ├── utils/
    │   ├── __pycache__/
    │   │   ├── ...
    │   ├── __init__.py
    │   ├── classifier.py 
    │   ├── property.py 
    │   └── scrapper.py
    ├── .gitignore
    ├── Instructions.md
    ├── main.py
    ├── README.md
    └── requirements.txt
 
</div>

<div style="flex: 0.75;">
<br>

- **main.py**: The entry point of the application. It initializes the scraper, saves the scraped data, and then converts the JSON data to a CSV file.
- **utils/**
  - **scrapper.py**: Contains the `Scrapper` class, which is responsible for sending requests to the website, parsing HTML content, and extracting property details. It utilizes `ThreadPoolExecutor` for concurrent processing of multiple pages and property details, significantly speeding up the scraping process.
  - **property.py**: Defines the `Property` class, which models the details of a real estate property and provides methods to update and convert these details.
  - **classifier.py**: Contains the `Classifier` class, which handles converting JSON data to a CSV format for easier analysis.
- **data/**
  - **houses.json**: A JSON file containing property data collected by the scraper.
  - **houses.csv**: A CSV file containing the property data for easy analysis.
- **requirements.txt**: Contains the required packages and their versions for the project.

</div>

</div>


## ⚒️ Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/KriszgruberL/Immo_Eliza.git
    cd Immo_Eliza
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  
    # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

## ⚙️ Usage

1. **Run the scraper**:
    ```sh
    python main.py
    ```

    This will start the scraping process, save the data into `houses.json`, and convert the data to `houses.csv`.<br>
    <b>⚠️ Running time is about 20-25 minutes </b>

2. **Data files**:
    - `houses.json`: Contains the full dataset in JSON format.
    - `houses.csv`: Contains the dataset in CSV format for easy analysis.

## 🔎 Details

### main.py

This file initializes the `Scrapper` and starts the scraping process. It then saves the scraped data to `houses.json` and uses the `Classifier` class to convert the JSON data to a CSV file.

### scrapper.py

    Defines the `Scrapper` class which handles:
    - Initializing HTTP session parameters and headers.
    - Sending requests to the target website.
    - Parsing HTML content using BeautifulSoup.
    - Extracting property details and saving them every 10 pages in `houses.json`.
    - Utilizing `ThreadPoolExecutor` for concurrent processing of multiple pages and property details.

### property.py

    Defines the `Property` class which models the details of each property:
    - Contains methods to update property details.
    - Provides a method to count the number of rooms.
    - Converts the property details to a dictionary format.

### classifier.py

    Defines the `Classifier` class which handles:
    - Reading the JSON data from `houses.json`.
    - Normalizing the data into a pandas DataFrame.
    - Saving the normalized data as a CSV file.

## 📃 Libraries documentation

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [Pandas](https://pandas.pydata.org/)

