from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import quote
import urllib.error as error
import pandas as pd
import ssl
import json
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def req(url):
    try:
        with urlopen(url, context=ctx) as conn:
            return conn.read()
    except error.HTTPError as e:
        print(url)

def geocodeForward(input,token):
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/%s.json?access_token=%s&types=address&limit=1"
    access_token = token
    addr = list(input["Address"])
    urls = [url % (quote(list_item), access_token) for list_item in addr]
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(req, urls))
        parsed_results = [json.loads(result.decode("utf-8")) for result in results]
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
        long = [
            result["features"][0]["geometry"]["coordinates"][0]
            if len(result["features"]) > 0
            else None
            for result in parsed_results
        ]
        lat = [
            result["features"][0]["geometry"]["coordinates"][1]
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
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/%s.json?access_token=%s&types=address&limit=1"
    access_token = token
    input['coords'] = input['Longitude'].map(str)+","+input['Latitude'].map(str)
    coordinates = list(input["coords"])
    urls = [url % (quote(list_item), access_token) for list_item in coordinates]
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(req, urls))
        parsed_results = [json.loads(result.decode("utf-8")) for result in results]
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