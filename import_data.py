import pandas as pd
import psycopg2
import json
import requests
from datetime import datetime

config = json.load(open("config.json"))["config"]

def getForecast():
    api_url_base = config["API_URL_BASE"]
    api_url_key = config["API_KEY"]
    api_url = api_url_base+api_url_key
    response = requests.get(api_url)
    forecast = response.json()
    df = pd.json_normalize(forecast["list"], max_level=None)
    df_e = df.explode("weather")
    df_e["weather.description"]=df_e["weather"].apply(lambda x: x["description"])
    df_f = df_e.drop(columns=["weather"])
    for i in df_f.columns:
        df_f = df_f.rename(columns={i:i.replace(".","_")})
    return df_f
def write_db(table,df):
    table="daily"
    db_server = config["DB_SERVER"]
    db_port = config["DB_PORT"]
    db_user = config["DB_USER"]
    db_pass = config["DB_PASS"]
    db_name = config["DB_NAME"]
    etl_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df["etl_date"] = etl_date
    valx = ",".join(["%s"]*len(df.columns))
    insert_sql = f"""INSERT INTO {table} ({','.join(df.columns)}) VALUES ({valx})"""
    try:
        conn = psycopg2.connect(
                        dbname=db_name,
                        user=db_user,
                        password=db_pass,
                        host=db_server,
                        port=db_port
                    )
        cursor = conn.cursor()
        cursor.executemany(insert_sql, df.values)
        print("executed..")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        raise e
    
#get forecast
df = getForecast()
#insert db
write_db("daily",df)