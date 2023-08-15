import json
from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)
config = json.load(open("config.json"))["config"]
db_server = config["DB_SERVER"]
db_port = config["DB_PORT"]
db_user = config["DB_USER"]
db_pass = config["DB_PASS"]
db_name = config["DB_NAME"]
db_params = {
    "dbname": db_name,
    "user": db_user,
    "password": db_pass,
    "host": db_server
}

def getData(q):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        query = q
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))
        cursor.close()
        connection.close()
        return jsonify(data)
    except psycopg2.Error as e:
        return jsonify({"error": str(e)})

@app.route('/api/forecast', methods=['GET'])
def get_data_by_dt():
    try:
        dt = request.args.get('dt')
        if dt is None:
            try:
                query = "SELECT * FROM daily;"
                data = getData(query)
                return data
            except psycopg2.Error as e:
                return jsonify({"error": str(e)})
        else:
            try:
                query = "SELECT * FROM daily WHERE left(dt_txt,10) = '{0}';".format(dt[:10])
                data = getData(query)
                return data
            except Exception as e:
                return jsonify({"message": "Registro não encontrado"})
    except psycopg2.Error as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)