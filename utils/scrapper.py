from concurrent.futures import ThreadPoolExecutor
from typing import Dict
import jsonlines
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin
from requests import Session

class Scrapper:

    def __init__(self) -> None:
        """
        Initializes the Scrapper class with base URLs, headers, and parameters for scraping.
        """
        self.start_url = "https://www.immoweb.be/en/search/house-and-apartment"
        self.sale = "/for-sale"
        self.rent = "/for-rent"

        # Work around for the restriction where immoweb don't allow request that aren't coming from a browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": self.start_url,
        }

        # Parameters for fetching sale listings
        self.params_sale = {
            "countries": "BE",
            "page": 1,
            "orderBy": "relevance",
        }
        
        # Parameters for fetching rental listings
        self.params_rent = {
            "countries": "BE",
            "priceType": "MONTHLY_RENTAL_PRICE",
            "page": 1,
            "orderBy": "relevance",
        }
        

        self.house_data = []
        
        
    def start_scrapping(self) -> None : 
        """
        Initiates the web scraping process for both rental and sale properties.
        
        This method calls the `get_url` method twice:
        1. To scrape rental properties using the URL for rentals and rental-specific parameters.
        2. To scrape sale properties using the URL for sales and sale-specific parameters.
        """
        self.get_url(f"{self.start_url}{self.rent}", self.params_rent)
        self.get_url(f"{self.start_url}{self.sale}", self.params_sale)
        
        
    def get_url(self, link: str, params: Dict[str, str | int]) -> None:
        """
        Fetches house listings from the specified URL with given parameters.

        This method performs HTTP GET requests to the provided URL, parses the HTML content,
        and extracts relevant house listing information. It handles multiple pages of results
        by incrementing the page number parameter and re-fetching until the limit is reached.

        Args:
            link (str): The URL to fetch the house listings from.
            params (Dict[str, int | str]): Parameters to include in the HTTP GET request.

        Returns:
            None
        """
        session = Session()
        with ThreadPoolExecutor() as pool : 
            while params["page"] <= 333:  # Limiting to 2 pages for testing
                response = requests.get(link, headers=self.headers, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                house_urls = []

                # Extracting information from each house listing
                for house in soup.select("div.card--result__body"):
                    text = (house.select_one("p.card__information--locality").get_text().strip())
                    zip_code, locality = text.split(" ", 1) if " " in text else (text, "")

                    price_match = re.search(r"\((\d+)\s*€\)", house.select_one("h2 a").get("aria-label", ""))
                    price = price_match.group(1) if price_match else None

                    house_url = urljoin(self.start_url, house.select_one("h2 a").get("href", ""))
                    
                    house_data = {
                        "url": house_url,
                        "zip_code": zip_code,
                        "locality": locality.upper(),
                        "price": price,
                    }
                    house_urls.append((house_url, house_data))

                # Use ThreadPoolExecutor to fetch house details concurrently
                futures = [pool.submit(self.get_house_details, url, house_data, session) for url, house_data in house_urls]
                for future in futures:
                    future.result()
                    
                print(f"Processed page {params['page']}")
                params["page"] += 1
                time.sleep(0.2)



    def get_house_details(self, url : str ,house_data : Dict, session : Session):
        """
        Fetches detailed information for a house listing from the provided URL.

        This method sends an HTTP GET request to the provided URL, parses the HTML content
        to extract house details, and structures the data into a dictionary. It also handles
        the extraction of additional details from a JSON object embedded in the page.

        Args:
            url (str): The URL of the house listing to fetch details from.
            session (Session): The requests session to use for making the HTTP request.

        Returns:
            dict: A dictionary containing detailed information about the house listing.
        """
        # Just a little print to see the progress
        try : 
            print(f"Processing : {url}")
            response = session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Fetching some data in the json object hidding in the page
            script_tag = soup.find("script", string=re.compile("window.classified")).string
            # Use a regular expression to extract the JSON data within the JavaScript assignment
            # The regex looks for "window.classified =" followed by the JSON data enclosed in curly braces
            json_data = re.search(r"window.classified\s*=\s*({.*});", script_tag).group(1)
            data = json.loads(json_data)

            # Structure of house data, not necessary but improve clarity
            house_data.update({
                "type_transaction" : data["transaction"]["type"],
                "subtype_transaction": data["transaction"]["subtype"],
                "type_of_property": data["property"]["type"],
                "subtype_of_property": data["property"]["subtype"],
                "energy_class": None,
                "heating_type": None,
                "construction_year": None,
                "number_of_frontages": None,
                "surface_land": None,
                "surface_livable_space": data["property"]["netHabitableSurface"],
                "number_floors": None,
                "building_condition": None,
                "surroundings_type": None,
                "furnished": False,
                "rooms": {
                    "living_room": None,
                    "dining_room": None,
                    "kitchen_type": {"installed": False, "kitchen_surface": None},
                    "bedrooms": {"number": None, "surface": []},
                    "bathrooms": {"number": None},
                    "toilets": {"number": None},
                    "laundry_room": False,
                    "office": {"presence": False, "surface": None},
                    "basement": {"presence": False, "surface": None},
                    "attic": False,
                },
                "extras": {"open_fire": data["property"]["fireplaceExists"]},
                "exterior": {
                    "terrace": {"presence": False, "surface": None, "orientation": None},
                    "garden": {"presence": False, "surface": None, "orientation": None},
                    "swimming_pool": False,
                }
            })

            for table in soup.find_all("table", class_="classified-table"):
                for row in table.find_all("tr"):

                    header = row.select_one("th")
                    value = row.select_one("td.classified-table__data")

                    if header and value:
                        # Extract the text content, stripping any leading and trailing whitespace
                        header_txt = header.contents[0].strip()
                        value_txt = value.contents[0].strip()

                        # Scrapping general infos
                        if header and value:
                            # Extract the text content, stripping any leading and trailing whitespace
                            header_txt = header.contents[0].strip()
                            value_txt = value.contents[0].strip()
                            
                            # Scrapping general infos
                            if "Energy class" in header_txt:
                                house_data["energy_class"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Heating type" in header_txt:
                                house_data["heating_type"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Construction year" in header_txt:
                                house_data["construction_year"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Number of frontages" in header_txt:
                                house_data["number_of_frontages"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Living area" in header_txt:
                                house_data["surface_livable_space"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Number of floors" in header_txt:
                                house_data["number_floors"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Building condition" in header_txt:
                                house_data["building_condition"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Surroundings type" in header_txt:
                                house_data["surroundings_type"] = re.sub(r"^\s+|\s+$", "", value_txt)

                            # Scraping for the rooms
                            elif "Furnished" in header_txt:
                                house_data["furnished"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False 
                            elif "Living room surface" in header_txt:
                                house_data["rooms"]["living_room"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Dining room" in header_txt:
                                house_data["rooms"]["dining_room"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False
                            elif "Kitchen type" in header_txt:
                                house_data["rooms"]["kitchen_type"]["installed"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Kitchen surface" in header_txt:
                                house_data["rooms"]["kitchen_type"]["kitchen_surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Bedrooms" in header_txt:
                                house_data["rooms"]["bedrooms"]["number"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif re.match(r"Bedroom \d+ surface", header_txt):
                                bedroom_surface = re.sub(r"^\s+|\s+$", "", value_txt)
                                house_data["rooms"]["bedrooms"]["surface"].append(bedroom_surface)
                            elif "Bathrooms" in header_txt:
                                house_data["rooms"]["bathrooms"]["number"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Toilets" in header_txt:
                                house_data["rooms"]["toilets"]["number"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Laundry room" in header_txt:
                                house_data["rooms"]["laundry_room"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False 
                            elif "Office" in header_txt and "surface" not in header_txt:
                                house_data["rooms"]["office"]["presence"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False 
                            elif "Office surface" in header_txt:
                                house_data["rooms"]["office"]["surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Basement surface" in header_txt:
                                house_data["rooms"]["basement"]["presence"] = True
                                house_data["rooms"]["basement"]["surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Basement" in header_txt:
                                house_data["rooms"]["basement"]["presence"] = True
                            elif "Attic" in header_txt:
                                house_data["rooms"]["attic"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False 

                            # Exterior datas
                            elif "Surface of the plot" in header_txt:
                                house_data["surface_land"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Garden surface" in header_txt:
                                house_data["exterior"]["garden"]["presence"] = True
                                house_data["exterior"]["garden"]["surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Garden orientation" in header_txt:
                                house_data["exterior"]["garden"]["orientation"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Garden" in header_txt:
                                house_data["exterior"]["garden"]["presence"] = True
                            elif "Terrace surface" in header_txt:
                                house_data["exterior"]["terrace"]["presence"] = True
                                house_data["exterior"]["terrace"]["surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Terrace" in header_txt:
                                house_data["exterior"]["terrace"]["presence"] = True if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes" else False 
                            elif "Terrace orientation" in header_txt:
                                house_data["exterior"]["terrace"]["orientation"] = re.sub(r"^\s+|\s+$", "", value_txt)
                            elif "Swimming pool" in header_txt:
                                house_data["exterior"]["swimming_pool"] = re.sub(r"^\s+|\s+$", "", value_txt)

                        house_data["nb_of_rooms"] = self.count_rooms(house_data["rooms"])

                    # else:
                    #     print("Skipping non-standard row")
            self.house_data.append(house_data)
            self.save()

            return house_data
        except requests.exceptions.HTTPError as e:
            print(f"+--------------{url} cannot be found--------------+") 
            


    def count_rooms(self, rooms):
            """A utilitarian function to count the number of rooms of a house scrapped

            Args:
                rooms (Dict): The rooms to count

            Returns:
                int: The total of rooms
            """
            count = 0
            for key, value in rooms.items():
                if isinstance(value, dict):
                    if "presence" in value and value["presence"]:
                        count += 1
                    elif "number" in value and value["number"]:
                        count += int(value["number"])
                    else:
                        count += 1  # Count the room itself even if nested
                elif isinstance(value, list):
                    count += len(value)
                elif value:
                    count += 1
            return count

    def save(self):
        with open("data/houses.json", "w") as file:
            json.dump(self.house_data, file )
        # with jsonlines.open("houses.json", mode="w") as file:
        #     file.write(self.house_data)
