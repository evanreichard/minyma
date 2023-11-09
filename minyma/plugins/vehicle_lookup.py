import json
import requests
from bs4 import BeautifulSoup
from minyma.plugin import MinymaPlugin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0)"
    " Gecko/20100101 Firefox/105.0",
}

class VehicleLookupPlugin(MinymaPlugin):
    """Search Vehicle Information"""

    def __init__(self, config):
        self.config = config
        self.name = "vehicle_state_plate"
        self.functions = [self.lookup_vehicle_by_state_plate]

    def __query_api(self, url, json=None, headers=None):
        # Perform Request
        if json is not None:
            resp = requests.post(url, json=json, headers=headers)
        else:
            resp = requests.get(url, headers=headers)

        # Parse Text
        text = resp.text.strip()

        # Parse JSON
        try:
            json = resp.json()
            return json, text, None
        except requests.JSONDecodeError:
            error = None
            if resp.status_code != 200:
                error = "Invalid HTTP Response: %s" % resp.status_code
            else:
                error = "Invalid JSON"
            return None, text, error


    def lookup_vehicle_by_state_plate(self, state_abbreviation: str, licence_plate: str):
        CARVANA_URL = (
            "https://apim.carvana.io/trades/api/v5/vehicleconfiguration/plateLookup/%s/%s"
            % (state_abbreviation, licence_plate)
        )

        # Query API
        json_resp, text_resp, error = self.__query_api(CARVANA_URL, headers=HEADERS)

        # Invalid JSON
        if json_resp is None:
            return json.dumps({
                "error": error,
                "response": text_resp,
            })

        try:
            # Check Result
            status_resp = json_resp.get("status", "Unknown")
            if status_resp != "Succeeded":
                if status_resp == "MissingResource":
                    error = "No Results"
                else:
                    error = "API Error: %s" % status_resp
                return {"error": error, "response": text_resp}

            # Parse Result
            vehicle_info = json_resp.get("content")
            vin = vehicle_info.get("vin")
            year = vehicle_info.get("vehicles")[0].get("year")
            make = vehicle_info.get("vehicles")[0].get("make")
            model = vehicle_info.get("vehicles")[0].get("model")
            trim = vehicle_info.get("vehicles")[0].get("trim")

        except Exception as e:
            return json.dumps({
                "error": "Unknown Error: %s" % e,
                "response": text_resp,
            })

        return json.dumps({
            "result": {
                "vin": vin,
                "year": year,
                "make": make,
                "model": model,
                "trim": trim,
            },
        })
