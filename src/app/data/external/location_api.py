from app.model.models import CoordinateResponse
import os

import requests
from requests import Response

from ...model.models import LocationResponse

locations_url = os.environ["LOCATIONS_URL"]

def get_locations() -> list[LocationResponse]:
    response = requests.get(locations_url)
    locations = []

    for result in response.json()["results"]:
        location = LocationResponse.model_validate_json(result)
        locations.append(location)

    return locations
