import pandas as pd
import pyodbc
import json
import requests

config = json.load(open("config.json"))["config"]

def getForecast():
    api_url_base = config["API_URL_BASE"]
    api_url_key = config["API_KEY"]
    api_url = api_url_base+api_url_key
    db_server = config["DB_SERVER"]
    db_port = config["DB_PORT"]
    db_user = config["DB_USER"]
    db_pass = config["DB_PASS"]
    response = requests.get(api_url)
    return response.json()

forecast = getForecast()
df = pd.json_normalize(forecast["list"], max_level=None)
df