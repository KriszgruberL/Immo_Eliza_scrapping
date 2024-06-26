import os
import jsonlines
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin


class Scrapper:

    def __init__(self) -> None:
        """
        Function that sets up the base of the scrapping
        """
        self.start_url = "https://www.immoweb.be/en/search/house/for-sale"

        # Work around for the restriction where immoweb don't allow request that aren't coming from a browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": self.start_url,
        }

        self.params = {
            "countries": "BE",
            "priceType": "SALE_PRICE",
            "page": 1,
            "orderBy": "relevance",
        }

        self.house_data = []
        self.id = 1

    def get_url_sale(self):
        while self.params["page"] <= 2:  # Limiting to 2 pages for testing
            response = requests.get(
                self.start_url, headers=self.headers, params=self.params
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Extracting information from each house listing
            for house in soup.select("div.card--result__body"):
                text = (house.select_one("p.card__information--locality").get_text().strip())
                zip_code, locality = text.split(" ", 1) if " " in text else (text, "")

                price_match = re.search(r"\((\d+)\s*€\)", house.select_one("h2 a").get("aria-label", ""))
                price = price_match.group(1) if price_match else None

                house_url = urljoin(
                    self.start_url, house.select_one("h2 a").get("href", "")
                )
                house_data = {
                    "id": self.id,
                    "url": house_url,
                    "zip_code": zip_code,
                    "locality": locality.upper(),
                    "price": price,
                }

                house_details = self.get_house_details(house_url)
                house_data.update(house_details)
                self.id += 1

                self.house_data.append(house_data)
                self.params["page"] += 1

            time.sleep(0.5)  # Adding a delay to be polite to the server

    def get_house_details(self, url):
        #Just a little print to see the progress
        print(f"Processing : {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        #Fetching some data in the json object hidding in the page 
        script_tag = soup.find("script", string=re.compile("window.classified")).string
        # Use a regular expression to extract the JSON data within the JavaScript assignment
        # The regex looks for "window.classified =" followed by the JSON data enclosed in curly braces
        json_data = re.search(r"window.classified\s*=\s*({.*});", script_tag).group(1)
        data = json.loads(json_data)

        #Structure of house data, not necessary but improve clarity
        house_data = {
            "type_of_property": data["property"]["type"],
            "subtype_of_property": data["property"]["subtype"],
            "construction_year": None,
            "surface": None,
            "number_floors": None,
            "building_condition": None,
            "rooms": {
                "living_room": None,
                "dining_room": None,
                "kitchen_type": {"installed": None, "kitchen_surface": None},
                "bedrooms": {"number": None, "surface": []},
                "bathrooms": {"number": None},
                "toilets": {"number": None},
                "laundry_room": None,
                "office": {"presence": None, "surface": None},
                "basement": {"presence": None, "surface": None},
                "attic": None,
            },
        }

        for table in soup.find_all("table", class_="classified-table"):
            for row in table.find_all("tr"):

                header = row.select_one("th")
                value = row.select_one("td.classified-table__data")

                if header and value:
                    # Extract the text content, stripping any leading and trailing whitespace
                    header_txt = header.contents[0].strip()
                    value_txt = value.contents[0].strip()

                    # Scrapping general infos
                    if "Construction year" in header_txt:
                        house_data["construction_year"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Living area" in header_txt:
                        house_data["surface"] = re.sub(r"^\s+|\s+$", "", value_txt)
                    elif "Number of floors" in header_txt:
                        house_data["number_floors"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Building condition" in header_txt:
                        house_data["building_condition"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )

                    # Scraping for the rooms
                    elif "Living room surface" in header_txt:
                        house_data["rooms"]["living_room"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Dining room" in header_txt:
                        house_data["rooms"]["dining_room"] = (
                            True
                            if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes"
                            else False
                        )
                    elif "Kitchen type" in header_txt:
                        house_data["rooms"]["kitchen_type"]["installed"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Kitchen surface" in header_txt:
                        house_data["rooms"]["kitchen_type"]["kitchen_surface"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Bedrooms" in header_txt:
                        house_data["rooms"]["bedrooms"]["number"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif re.match(r"Bedroom \d+ surface", header_txt):
                        bedroom_surface = re.sub(r"^\s+|\s+$", "", value_txt)
                        house_data["rooms"]["bedrooms"]["surface"].append(
                            bedroom_surface
                        )
                    elif "Bathrooms" in header_txt:
                        house_data["rooms"]["bathrooms"]["number"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Toilets" in header_txt:
                        house_data["rooms"]["toilets"]["number"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Laundry room" in header_txt:
                        house_data["rooms"]["laundry_room"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Office" in header_txt and "surface" not in header_txt:
                        house_data["rooms"]["office"]["presence"] = (
                            True
                            if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes"
                            else False
                        )
                    elif "Office surface" in header_txt:
                        house_data["rooms"]["office"]["surface"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Basement surface" in header_txt:
                        house_data["rooms"]["basement"]["presence"] = True
                        house_data["rooms"]["basement"]["surface"] = re.sub(
                            r"^\s+|\s+$", "", value_txt
                        )
                    elif "Attic" in header_txt:
                        house_data["rooms"]["attic"] = (
                            True
                            if re.sub(r"^\s+|\s+$", "", value_txt) == "Yes"
                            else False
                        )

                    house_data["nb_of_rooms"] = self.count_rooms(house_data["rooms"])

                else:
                    print("Skipping non-standard row")
        self.save()
        
        

        return house_data

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
        # with open("houses.json", "w") as file:
        #     json.dump(self.house_data, file, indent=4)
        with jsonlines.open("houses.json", mode="w") as file:
            file.write(self.house_data)


