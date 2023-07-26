import mysql.connector
from flask_json import as_json, json_response
from flask import Flask, Blueprint

lastmeasure_bp = Blueprint('lastmeasure', __name__)

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'dsanmartins.mysql.pythonanywhere-services.com'  # MySQL host
app.config['MYSQL_USER'] = 'dsanmartins'  # MySQL username
app.config['MYSQL_PASSWORD'] = 'innova2023'  # MySQL password
app.config['MYSQL_DATABASE'] = 'dsanmartins$default'  # MySQL database name

@lastmeasure_bp.route('/<string:id>')
@as_json
def lastmeasure(id):

    try:
        conn = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DATABASE']
            )

        cursor = conn.cursor()
        cursor.execute("SELECT ifnull(max(time),0) as lastmeasure FROM measurement where station_id = %s", (id,))
        query = query = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return json_response(data = query, headers_={'Content-Type' : 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*'})

    except mysql.connector.Error as error:
        return json_response(data={'message': f"Error retrieving data from MySQL: {error}"}, status_=500)

