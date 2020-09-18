import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"For the options below, please use date format YYYY-MM-DD<br/>"
        f"/api/v1.0/<'start'><br/>"
        f"/api/v1.0/<'start'>/<'end'>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precip.append(precip_dict)    
    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(func.strftime(Measurement.date) > "2016-08-22").\
    filter(Measurement.station == 'USC00519281').all()
    session.close()

    ly_tobs = list(np.ravel(results))
    return jsonify(ly_tobs)

@app.route("/api/v1.0/<start>")
def startonly(start):
    session = Session(engine)
    input_date = dt.datetime.strptime(start, '%Y-%m-%d')
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= input_date).all()
    session.close()
    startlist = list(np.ravel(start_data))
    return jsonify(startlist)

@app.route("/api/v1.0/<start>/<end>")
def beginandend(start,end): 
    session = Session(engine)   
    input_start= dt.datetime.strptime(start, '%Y-%m-%d')
    input_end= dt.datetime.strptime(end,'%Y-%m-%d')
    spaninfo = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= input_start).filter(Measurement.date <= input_end).all()
    durationinfo = list(np.ravel(spaninfo))
    return jsonify(durationinfo)

if __name__ == "__main__":
    app.run(debug=True)
