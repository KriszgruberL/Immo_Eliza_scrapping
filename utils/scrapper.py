import aiohttp
import asyncio
from typing import Dict
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json

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

    async def start_scrapping(self) -> None:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            await self.get_url(session, f"{self.start_url}{self.rent}", self.params_rent)
            await self.get_url(session, f"{self.start_url}{self.sale}", self.params_sale)

    async def get_url(self, session: aiohttp.ClientSession, link: str, params: Dict[str, str | int]) -> None:
        while params["page"] <= 333:
            try:
                async with session.get(link, params=params) as response:
                    response.raise_for_status()
                    text = await response.text()
                    soup = BeautifulSoup(text, "html.parser")
                    house_urls = []

                    for house in soup.select("div.card--result__body"):
                        house_url = urljoin(self.start_url, house.select_one("h2 a").get("href", ""))
                        house_data = {"url": house_url}
                        house_urls.append((house_url, house_data))

                    tasks = [self.get_house_details(session, url, house_data) for url, house_data in house_urls]
                    await asyncio.gather(*tasks)

                print(f"Processed page {params['page']}")
                params["page"] += 1
                
            except aiohttp.ClientError as e:
                print(f"Failed to fetch page {params['page']} from {link}: {e}")
                params["page"] += 1

    async def get_house_details(self, session: aiohttp.ClientSession, url: str, house_data: Dict):
        try:
            print(f"Processing: {url}")
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")

                script_tag = soup.find("script", string=re.compile("window.classified")).string
                json_data = re.search(r"window.classified\s*=\s*({.*});", script_tag).group(1)
                data = json.loads(json_data)

                house_data.update({
                    "zip_code": data["property"]["location"]["postalCode"],
                    "locality": data["property"]["location"]["locality"],
                    "price": data["price"]["mainValue"],
                    "type_transaction": data["transaction"]["type"],
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
                            header_txt = header.contents[0].strip()
                            value_txt = value.contents[0].strip()

                            if "Energy class" in header_txt:
                                house_data["energy_class"] = value_txt
                            elif "Heating type" in header_txt:
                                house_data["heating_type"] = value_txt
                            elif "Construction year" in header_txt:
                                house_data["construction_year"] = value_txt
                            elif "Number of frontages" in header_txt:
                                house_data["number_of_frontages"] = value_txt
                            elif "Living area" in header_txt:
                                house_data["surface_livable_space"] = value_txt
                            elif "Number of floors" in header_txt:
                                house_data["number_floors"] = value_txt
                            elif "Building condition" in header_txt:
                                house_data["building_condition"] = value_txt
                            elif "Surroundings type" in header_txt:
                                house_data["surroundings_type"] = value_txt

                            elif "Furnished" in header_txt:
                                house_data["furnished"] = value_txt == "Yes"
                            elif "Living room surface" in header_txt:
                                house_data["rooms"]["living_room"] = value_txt
                            elif "Dining room" in header_txt:
                                house_data["rooms"]["dining_room"] = value_txt == "Yes"
                            elif "Kitchen type" in header_txt:
                                house_data["rooms"]["kitchen_type"]["installed"] = value_txt
                            elif "Kitchen surface" in header_txt:
                                house_data["rooms"]["kitchen_type"]["kitchen_surface"] = value_txt
                            elif "Bedrooms" in header_txt:
                                house_data["rooms"]["bedrooms"]["number"] = value_txt
                            elif re.match(r"Bedroom \d+ surface", header_txt):
                                house_data["rooms"]["bedrooms"]["surface"].append(value_txt)
                            elif "Bathrooms" in header_txt:
                                house_data["rooms"]["bathrooms"]["number"] = value_txt
                            elif "Toilets" in header_txt:
                                house_data["rooms"]["toilets"]["number"] = value_txt
                            elif "Laundry room" in header_txt:
                                house_data["rooms"]["laundry_room"] = value_txt == "Yes"
                            elif "Office" in header_txt and "surface" not in header_txt:
                                house_data["rooms"]["office"]["presence"] = value_txt == "Yes"
                            elif "Office surface" in header_txt:
                                house_data["rooms"]["office"]["surface"] = value_txt
                            elif "Basement surface" in header_txt:
                                house_data["rooms"]["basement"]["presence"] = True
                                house_data["rooms"]["basement"]["surface"] = value_txt
                            elif "Basement" in header_txt:
                                house_data["rooms"]["basement"]["presence"] = True
                            elif "Attic" in header_txt:
                                house_data["rooms"]["attic"] = value_txt == "Yes"

                            elif "Surface of the plot" in header_txt:
                                house_data["surface_land"] = value_txt
                            elif "Garden surface" in header_txt:
                                house_data["exterior"]["garden"]["presence"] = True
                                house_data["exterior"]["garden"]["surface"] = value_txt
                            elif "Garden orientation" in header_txt:
                                house_data["exterior"]["garden"]["orientation"] = value_txt
                            elif "Garden" in header_txt:
                                house_data["exterior"]["garden"]["presence"] = True
                            elif "Terrace surface" in header_txt:
                                house_data["exterior"]["terrace"]["presence"] = True
                                house_data["exterior"]["terrace"]["surface"] = value_txt
                            elif "Terrace" in header_txt:
                                house_data["exterior"]["terrace"]["presence"] = value_txt == "Yes"
                            elif "Terrace orientation" in header_txt:
                                house_data["exterior"]["terrace"]["orientation"] = value_txt
                            elif "Swimming pool" in header_txt:
                                house_data["exterior"]["swimming_pool"] = value_txt

                house_data["nb_of_rooms"] = self.count_rooms(house_data["rooms"])
                self.house_data.append(house_data)
                self.save()
                return house_data
        except aiohttp.ClientError as e:
            print(f"Failed to fetch details from {url}: {e}")

    def count_rooms(self, rooms):
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
            json.dump(self.house_data, file)

