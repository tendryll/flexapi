import os

import requests

from ...model.models import LocationResponse

locations_url = os.environ["LOCATIONS_URL"]


def get_locations() -> list[LocationResponse]:
    response = requests.get(locations_url)
    locations = []

    for result in response.json():
        location = LocationResponse.model_validate(result)
        locations.append(location)

    return locations
