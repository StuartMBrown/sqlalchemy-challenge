# Import all dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify
import datetime as dt
#################################################
# Database Setup
#################################################
hawaii=create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model, and its tables.
reflect=automap_base()
reflect.prepare(autoload_with=hawaii)
# Save the references to each table.
Measurement=reflect.classes.measurement
Station=reflect.classes.station
# Begin our session (link) from Python to the database
surf=Session(hawaii)
#################################################
# Set up Flask
#################################################
flasky=Flask(__name__)
#################################################
# Route Flask
#################################################
@flasky.route("/")
def home(): """List all available routes"""
    return("""<h1>Available Routes:</h1>
    <ul> <li>Precipitation in last 12 months: <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>
    <li>List of stations: <a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>
    <li>Temperatures in last 12 months: <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>
    <li>Temperature stats from the start date yyyy-mm-dd: <a href='/api/v1.0/start'>/api/v1.0/{start}</a></li>
    <li>Temperature stats from the start date to the end date in yyyy-mm-dd format: <a href='/api/v1.0/start/end'>/api/v1.0/{start}/{end}</a></li> </ul>""")
#Precipitation
@flasky.route("/api/v1.0/precipitation")
def precip():
    enddate = surf.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    enddate = dt.datetime.strptime(enddate, '%Y-%m-%d')
    ua = dt.date(enddate.year -1, enddate.month, enddate.day)
    results1 = surf.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= ua).all()
    surf.close()
    response = []
    # Convert results into a list
    results = list(np.ravel(results1))
    for r in range(0, len(results1), 2):
        # Create a new dictionary.
        dicti = {}
        dicti["date"] = results1[r]
        dicti["prcp"] = results1[r+1]
        response.append(dicti)
    return jsonify(response)
#Stations
@flasky.route('/api/v1.0/stations')    
def stations():
    stations = []
    result2 = surf.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    for row in result2:
        row_as_dict = row._mapping 
        station = dict(row_as_dict)
        stations.append(station)
    return jsonify(stations)
#Tobs
@flasky.route("/api/v1.0/tobs")
def tobs():
    enddate = surf.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    enddate = dt.datetime.strptime(enddate, '%Y-%m-%d')
    ua = dt.date(enddate.year -1, enddate.month, enddate.day)
    results3 = surf.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= ua).all()
    surf.close()
    alltobs = []
    for row in results3:
        row_as_dict = row._mapping 
        tob = dict(row_as_dict)
        alltobs.append(tob)
    return jsonify(alltobs)
#Starting
@flasky.route('/api/v1.0/<start>')
def tempstart(start):
    result4 = surf.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    surf.close()
    d1 = (("tmin", "tavg", "tmax"), list(np.ravel(result4)))
    startresp = dict(zip(*d1))
    return jsonify(startresp)
#Starting and stopping
@flasky.route('/api/v1.0/<start>/<stop>')
def temp_start_stop(start,stop):
    result5 = surf.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    surf.close()
    d2 = (("tmin", "tavg", "tmax"), list(np.ravel(result5)))
    response = dict(zip(*d2))
    return jsonify(response)