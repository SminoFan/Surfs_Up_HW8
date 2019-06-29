import numpy as np
import pandas as pd

import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year including date and precipitation"""
    maxdate = session.query(func.max(Measurement.date)).first()[0]
    last_year = (pd.to_datetime(maxdate)- dt.timedelta(365)).date().strftime('%Y-%m-%d')
    sel = [Measurement.date, Measurement.prcp]
    results = session.query(*sel).filter(Measurement.date.between(last_year, maxdate)).order_by('date')

    # Create a list of dicts with `date` and `prcp` as the keys and values

    rainfall = []
    for date, prcp in results:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        rainfall.append(rain_dict)
   
    session.close()

    return jsonify(rainfall)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    session.close()
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year including date and tobs"""

    maxdate = session.query(func.max(Measurement.date)).first()[0]
    last_year = (pd.to_datetime(maxdate)- dt.timedelta(365)).date().strftime('%Y-%m-%d')
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date.between(last_year, maxdate)).order_by('date')

    # Create a list of dicts with `date` and `tobs` as the keys and values

    temperature = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["prcp"] = tobs
        temperature.append(temp_dict)
   
    session.close()

    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def trip_start(start):    
    """Return a JSON list of the minimum, average, and temperatures for a given start range."""

    maxdate = session.query(func.max(Measurement.date)).first()[0]
    end_date = pd.to_datetime(maxdate).date().strftime('%Y-%m-%d')
    
    start_date = pd.to_datetime(start).date().strftime('%Y-%m-%d')
    
    trip_data =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date.between(start_date, end_date )).all()
    trip = list(np.ravel(trip_data))
    
    session.close()
    return jsonify(trip)
    
    

@app.route("/api/v1.0/<start>/<end>")
def trip_start_end(start,end):
    """Return a JSON list of the minimum, average, and temperatures for a given start range."""

    end_date = pd.to_datetime(end).date().strftime('%Y-%m-%d')
    start_date = pd.to_datetime(start).date().strftime('%Y-%m-%d')
    
    trip_data =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date.between(start_date, end_date )).all()
    trip = list(np.ravel(trip_data))
    
    session.close()
    return jsonify(trip)

if __name__ == "__main__":
    app.run(debug=True)