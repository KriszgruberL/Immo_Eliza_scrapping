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

from utils.property import Property

class Scrapper:
    def __init__(self) -> None:
        self.start_url = "https://www.immoweb.be/en/search/house-and-apartment"
        self.sale = "/for-sale"
        self.rent = "/for-rent"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": self.start_url,
        }

        self.params_sale = {
            "countries": "BE",
            "page": 1,
            "orderBy": "relevance",
        }
        
        self.params_rent = {
            "countries": "BE",
            "priceType": "MONTHLY_RENTAL_PRICE",
            "page": 1,
            "orderBy": "relevance",
        }

        self.house_data = []

    def start_scrapping(self) -> None:
        with ThreadPoolExecutor(max_workers=20) as pool:
            session = Session()
            self.get_url(pool, session, f"{self.start_url}{self.rent}", self.params_rent)
            self.get_url(pool, session, f"{self.start_url}{self.sale}", self.params_sale)
                         
    def get_url(self, pool: ThreadPoolExecutor, session: Session, link: str, params: Dict[str, str | int]) -> None:
        while params["page"] <= 333: 
            try:
                response = requests.get(link, headers=self.headers, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                house_urls = []

                for house in soup.select("div.card--result__body"):
                    house_url = urljoin(self.start_url, house.select_one("h2 a").get("href", ""))
                    house = Property(house_url)
                    house_urls.append(house)

                futures = [pool.submit(self.get_house_details, house, session) for house in house_urls]
                for future in futures:
                    future.result()
                    
                print(f"Processed page {params['page']}")
                params["page"] += 1
                
                if params["page"] % 10 == 0:
                    self.save()
                
            except requests.exceptions.HTTPError as e:
                print(f"Failed to fetch page {params['page']} from {link}: {e}")
                params["page"] += 1

    def get_house_details(self, house: Property, session: Session):
        try:
            print(f"Processing: {house.url}")
            response = session.get(house.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            script_tag = soup.find("script", string=re.compile("window.classified")).string
            json_data = re.search(r"window.classified\s*=\s*({.*});", script_tag).group(1)
            data = json.loads(json_data)

            house.update_details({
                "zip_code": data["property"]["location"]["postalCode"],
                "locality": data["property"]["location"]["locality"],
                "price": data["price"]["mainValue"],
                "type_transaction": data["transaction"]["type"],
                "subtype_transaction": data["transaction"]["subtype"],
                "type_of_property": data["property"]["type"],
                "subtype_of_property": data["property"]["subtype"],
                "surface_livable_space": data["property"]["netHabitableSurface"],
                "extras": {"open_fire": data["property"]["fireplaceExists"]},
            })

            for table in soup.find_all("table", class_="classified-table"):
                for row in table.find_all("tr"):
                    header = row.select_one("th")
                    value = row.select_one("td.classified-table__data")

                    if header and value:
                        header_txt = header.contents[0].strip()
                        value_txt = value.contents[0].strip()
                        value_txt = re.sub(r"^\s+|\s+$", "", value_txt) 
                        
                        if "Energy class" in header_txt:
                            house.details["energy_class"] = value_txt
                        elif "Heating type" in header_txt:
                            house.details["heating_type"] = value_txt
                        elif "Construction year" in header_txt:
                            house.details["construction_year"] = value_txt
                        elif "Number of frontages" in header_txt:
                            house.details["number_of_frontages"] = value_txt
                        elif "Living area" in header_txt:
                            house.details["surface_livable_space"] = value_txt
                        elif "Number of floors" in header_txt:
                            house.details["number_floors"] = value_txt
                        elif "Building condition" in header_txt:
                            house.details["building_condition"] = value_txt
                        elif "Surroundings type" in header_txt:
                            house.details["surroundings_type"] = value_txt
                        elif "Furnished" in header_txt:
                            house.details["furnished"] = True if value_txt == "Yes" else False 
                        elif "Living room surface" in header_txt:
                            house.details["rooms"]["living_room"] = value_txt
                        elif "Dining room" in header_txt:
                            house.details["rooms"]["dining_room"] = True if value_txt == "Yes" else False
                        elif "Kitchen type" in header_txt:
                            house.details["rooms"]["kitchen_type"]["installed"] = value_txt
                        elif "Kitchen surface" in header_txt:
                            house.details["rooms"]["kitchen_type"]["kitchen_surface"] = value_txt
                        elif "Bedrooms" in header_txt:
                            house.details["rooms"]["bedrooms"]["number"] = value_txt
                        elif re.match(r"Bedroom \d+ surface", header_txt):
                            bedroom_surface = value_txt
                            house.details["rooms"]["bedrooms"]["surface"].append(bedroom_surface)
                        elif "Bathrooms" in header_txt:
                            house.details["rooms"]["bathrooms"]["number"] = value_txt
                        elif "Toilets" in header_txt:
                            house.details["rooms"]["toilets"]["number"] = value_txt
                        elif "Laundry room" in header_txt:
                            house.details["rooms"]["laundry_room"] = True if value_txt == "Yes" else False 
                        elif "Office" in header_txt and "surface" not in header_txt:
                            house.details["rooms"]["office"]["presence"] = True if value_txt == "Yes" else False 
                        elif "Office surface" in header_txt:
                            house.details["rooms"]["office"]["surface"] = value_txt
                        elif "Basement surface" in header_txt:
                            house.details["rooms"]["basement"]["presence"] = True
                            house.details["rooms"]["basement"]["surface"] = value_txt
                        elif "Basement" in header_txt:
                            house.details["rooms"]["basement"]["presence"] = True
                        elif "Attic" in header_txt:
                            house.details["rooms"]["attic"] = True if value_txt == "Yes" else False 
                        elif "Surface of the plot" in header_txt:
                            house.details["surface_land"] = value_txt
                        elif "Garden surface" in header_txt:
                            house.details["exterior"]["garden"]["presence"] = True
                            house.details["exterior"]["garden"]["surface"] = value_txt
                        elif "Garden orientation" in header_txt:
                            house.details["exterior"]["garden"]["orientation"] = value_txt
                        elif "Garden" in header_txt:
                            house.details["exterior"]["garden"]["presence"] = True
                        elif "Terrace surface" in header_txt:
                            house.details["exterior"]["terrace"]["presence"] = True
                            house.details["exterior"]["terrace"]["surface"] = value_txt
                        elif "Terrace" in header_txt:
                            house.details["exterior"]["terrace"]["presence"] = True if value_txt == "Yes" else False 
                        elif "Terrace orientation" in header_txt:
                            house.details["exterior"]["terrace"]["orientation"] = value_txt
                        elif "Swimming pool" in header_txt:
                            house.details["exterior"]["swimming_pool"] = value_txt

            house.count_rooms()
            self.house_data.append(house.to_dict())
            
            with jsonlines.open("data/houses.jsonl", mode="a") as writer:
                writer.write(house.to_dict())

        except requests.exceptions.HTTPError as e:
            print(f"+--------------{house.url} cannot be found--------------+") 

    def save(self):
        with open("data/houses.json", "w") as file:
            json.dump(self.house_data, file)
