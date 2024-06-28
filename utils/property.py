from typing import Dict


class Property:
    def __init__(self, url: str):
        self.url = url
        self.details = {
            "url": url,
            "zip_code": None,
            "locality": None,
            "price": None,
            "type_transaction": None,
            "subtype_transaction": None,
            "type_of_property": None,
            "subtype_of_property": None,
            "energy_class": None,
            "heating_type": None,
            "construction_year": None,
            "number_of_frontages": None,
            "surface_land": None,
            "surface_livable_space": None,
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
            "extras": {"open_fire": False},
            "exterior": {
                "terrace": {"presence": False, "surface": None, "orientation": None},
                "garden": {"presence": False, "surface": None, "orientation": None},
                "swimming_pool": False,
            }
        }

    def update_details(self, data: Dict):
        self.details.update(data)

    def count_rooms(self):
        count = 0
        for key, value in self.details["rooms"].items():
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
        self.details["nb_of_rooms"] = count

    def to_dict(self):
        return self.details