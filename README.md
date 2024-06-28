# Immo_Eliza

<p align="center">
  <img src="./assets/logo.webp" width="350"  />
</p>

## Overview

This project is a real estate web scraper that collects data on properties for sale and rent from Immoweb. It extracts details about each property, including price, location, type, and various features, and saves this data into JSON and CSV formats for further analysis.

## Collaborator
Thank you Antoine Servais for your contribution to this project:

- [antoineservais1307](https://github.com/antoineservais1307)

## Project Structure

- **main.py**: The entry point of the application. It initializes the scraper, saves the scraped data, and then converts the JSON data to a CSV file.
- **utils/**
  - **scrapper.py**: Contains the `Scrapper` class, which is responsible for sending requests to the website, parsing HTML content, and extracting property details.
  - **property.py**: Defines the `Property` class, which models the details of a real estate property and provides methods to update and convert these details.
  - **classifier.py**: Contains the `Classifier` class, which handles converting JSON data to a CSV format for easier analysis.
- **data/**
  - **houses.json**: A JSON file containing property data collected by the scraper.
  - **houses.csv**: A CSV file containing the property data for easy analysis.
- **requirements.txt**: Contains the required packages and their versions for the project.

## Setup

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

## Usage

1. **Run the scraper**:
    ```sh
    python main.py
    ```

    This will start the scraping process, save the data into `houses.json`, and convert the data to `houses.csv`.

2. **Data files**:
    - `houses.json`: Contains the full dataset in JSON format.
    - `houses.csv`: Contains the dataset in CSV format for easy analysis.

## Details

### main.py

This file initializes the `Scrapper` and starts the scraping process. It then saves the scraped data to `houses.json` and uses the `Classifier` class to convert the JSON data to a CSV file.

### scrapper.py

Defines the `Scrapper` class which handles:
- Initializing HTTP session parameters and headers.
- Sending requests to the target website.
- Parsing HTML content using BeautifulSoup.
- Extracting property details and saving them every 10 pages in `houses.json`.

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

## Libraries documentation

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [jsonlines](https://jsonlines.readthedocs.io/en/latest/)
- [Pandas](https://pandas.pydata.org/)

