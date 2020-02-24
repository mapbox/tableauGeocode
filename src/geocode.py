from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import quote
import urllib.error as error
import pandas as pd
import ssl
import json
import os
from ratelimit import limits, sleep_and_retry

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# This is the rate limit period in seconds
# Mapbox rate limits on a per-minute basis, with geocoding set at 600 requests per minute
RATE_LIMIT = 600
LIMIT_DURATION = 60

errReturn = {
  "features": []
}

# Set up rate limiting for API calls
# If rate limit is exceeded, sleep the thread and wait until the LIMIT_DURATION has lapsed
# If you request an increased rate limit, update RATE_LIMIT above
@sleep_and_retry
@limits(calls=RATE_LIMIT, period=LIMIT_DURATION)
def req(url):
    try:
        with urlopen(url, context=ctx) as conn:
            return conn.read()
    except error.HTTPError as e:
        return json.dumps(errReturn).encode("utf-8")

def geocodeForward(input,token):
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/%s.json?pluginName=tableauGeocoder&access_token=%s&types=address&limit=1"
    access_token = token
    addr = list(input["Address"])
    urls = [url % (quote(list_item), access_token) for list_item in addr]
    # Once you exceed 1200 req/minute, then consider using more threads to achieve performance
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = (executor.map(req, urls))
        parsed_results = (json.loads(result.decode("utf-8")) for result in results)
        long,lat = zip(*list(result["features"][0]["geometry"]["coordinates"]
            if len(result["features"]) > 0
            else [None,None]
            for result in parsed_results))
        address = [
            result["features"][0].get("place_name", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        relevance = [
            result["features"][0].get("relevance", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        accuracy = [
            result["features"][0]["properties"].get("accuracy", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        d = {
            "InitialQuery": addr,
            "ReturnAddress": address,
            "Accuracy": accuracy,
            "Relevance": relevance,
            "Longitude": long,
            "Latitude": lat,
        }
        columns = list(d.keys())
        dataOut = pd.DataFrame(d, columns=columns)
        return dataOut

def geocodeReverse(input,token):
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/%s.json?pluginName=tableauGeocoder&access_token=%s&types=address&limit=1"
    access_token = token
    input['coords'] = input['Longitude'].map(str)+","+input['Latitude'].map(str)
    coordinates = list(input["coords"])
    urls = [url % (quote(str(list_item)), access_token) for list_item in coordinates]
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = (executor.map(req, urls))
        parsed_results = (json.loads(result.decode("utf-8")) for result in results)
        address = [
            result["features"][0].get("place_name", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        relevance = [
            result["features"][0].get("relevance", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        accuracy = [
            result["features"][0]["properties"].get("accuracy", None)
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        d = {
            "InitialQuery": coordinates,
            "ReturnAddress": address,
            "Accuracy": accuracy,
            "Relevance": relevance
        }
        columns = list(d.keys())
        dataOut = pd.DataFrame(d, columns=columns)
        return dataOut