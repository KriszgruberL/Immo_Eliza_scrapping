from typing import Dict

class Property:
    """
    A class to represent a Property and manage its details.

    Attributes
    ----------
    url : str : The URL associated with the property.
    details : dict : A dictionary to store various details about the property, including address, price, 
        type, energy class, rooms, and exterior features.

    Methods
    -------
    update_details(data: Dict):
        Updates the property details with the given data.
        
    count_rooms():
        Counts the total number of rooms in the property and updates the details dictionary.
        
    to_dict():
        Returns the property details as a dictionary.
    """
    def __init__(self, url: str):
        """
        Constructs all the necessary attributes for the Property object.

        Parameters
        ----------
        url : str : The URL associated with the property.
        """
        
        self.url = url
        
        # Initialize the details dictionary with default values
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