from flask import Flask, request, jsonify
import mysql.connector
from functools import wraps
from flask import Blueprint
import jwt
storemeasure_bp = Blueprint('storemeasure', __name__)
token_bp = Blueprint('token', __name__)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to your preferred secret key
app.config['MYSQL_HOST'] = 'dsanmartins.mysql.pythonanywhere-services.com'  # MySQL host
app.config['MYSQL_USER'] = 'dsanmartins'  # MySQL username
app.config['MYSQL_PASSWORD'] = 'innova2023'  # MySQL password
app.config['MYSQL_DATABASE'] = 'dsanmartins$default'  # MySQL database name

# Decorator function for token-based authentication
def token_required(f):
    print(f)
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or 'Bearer ' not in token:
            return jsonify({'message': 'Token is missing or invalid!'}), 401

        try:
            token = token.split()[1]  # Extract token from "Bearer <token>"
            print(token)
            print(app.config['SECRET_KEY'])
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms = ['HS256'])
            print(data)
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated

# Route for generating a new token
@token_bp.route('/', methods=['POST'])
def generate_token():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        # Add your authentication logic here
        # For demonstration purposes, we'll use a simple username and password check
        if username == 'admin' and password == 'password':
            token_payload = {'username': username, 'password':password}
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token})

        return jsonify({'message': 'Invalid credentials!'}), 401

    except Exception as e:
        return jsonify({'message': 'Error generating token!', 'error': str(e)}), 500


# Route for receiving and storing JSON values
@storemeasure_bp.route('/', methods=['POST'])
@token_required
def store_data():
    try:
        data = request.get_json()

        station_id = data['station_id']
        time = int(data['time'])
        measure = float(data['measure'])

        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        cursor = conn.cursor()
        cursor.execute('INSERT INTO measurement (station_id, time, measure) VALUES (%s, %s, %s)', (station_id, time, measure))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Data stored successfully!'})

    except Exception as e:
        return jsonify({'message': 'Error storing data!', 'error': str(e)}), 500
