
from flask import Flask, render_template, jsonify, request
import markdowne

from allp import root_bp
from chp import chp_bp
from rec import rec_bp
from iap import iap_bp
from cep import cep_bp
from pip import pip_bp
from lastmeasure import lastmeasure_bp
from storemeasure import storemeasure_bp
from storemeasure import token_bp
from flask_json import FlaskJSON
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
FlaskJSON(app)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(root_bp, url_prefix='/allp')
app.register_blueprint(chp_bp, url_prefix='/chp')
app.register_blueprint(rec_bp, url_prefix='/rec')
app.register_blueprint(iap_bp, url_prefix='/iap')
app.register_blueprint(cep_bp, url_prefix='/cep')
app.register_blueprint(pip_bp, url_prefix='/pip')
app.register_blueprint(lastmeasure_bp, url_prefix='/lastmeasure')
app.register_blueprint(storemeasure_bp, url_prefix='/storemeasure')
app.register_blueprint(token_bp, url_prefix='/token')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dsanmartins:innova2023@dsanmartins.mysql.pythonanywhere-services.com/dsanmartins$default'
db = SQLAlchemy(app)


# Measurement model
class Measurement(db.Model):

    __tablename__ = 'measurement'  # Specify the table name
    measure_id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(255))
    time = db.Column(db.Integer)
    measure = db.Column(db.Float)

    def __repr__(self):
        return f"<Measurement(sensor_name='{self.station_id}', unixtime='{self.time}', flow_measure='{self.measure}')>"


@app.route('/about')
def info_web():
    with open('mysite/index.md', 'r') as f:
        text = f.read()
        html = markdown.markdown(text, extensions=['tables'])
        return html

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def get_data():
    # Get the sensor name and Unix time filter from the request
    sensor_name = request.args.get('sensor_name')
    start_unixtime = request.args.get('start_unixtime')
    end_unixtime = request.args.get('end_unixtime')
    measure_threshold = request.args.get('measure_threshold', type=float)


    # Build the query to fetch the data
    query = db.session.query(Measurement.time, Measurement.measure).filter(
        Measurement.station_id == sensor_name,
        Measurement.time >= start_unixtime,
        Measurement.time <= end_unixtime
    )

     # Apply measure threshold filtering if a value is provided
    if measure_threshold is not None:
        query = query.filter(Measurement.measure >= measure_threshold)

    data = [(row[0], row[1]) for row in query.all()]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

