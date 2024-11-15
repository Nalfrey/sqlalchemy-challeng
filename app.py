# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Create engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Map the classes
#Base.classes.keys()
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
def homepage():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stats from the start date (MMDDYYYY): /api/v1.0/<start><br/>"
        f"Temperature stats from the start to end dates (MMDDYYYY): /api/v1.0/<start>/<end><br/>"
    )

#Precipitation Route 

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    twelve_months_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    """Return the precipitation data for the last year"""
    # Get the most recent date and the date one year ago,  # Perform a query to retrieve the data and precipitation scores for the last year
    mrd_list = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).\
        filter(Measurement.date >= twelve_months_prior).all()
    prcp_list = []
    
     # Convert the query results to a dictionary with date as the key and prcp as the value
    for date, prcp in mrd_list:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)
    session.close()
    return jsonify(prcp_list)
   

#Stations Route

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Perform a query to retrieve the stations data
    stations_data = session.query(Station.station).order_by(Station.station).all()

    session.close()

 # Convert the query results
    stations_list = list(np.ravel(stations_data))

    return jsonify(stations_list)

#TOBS Route

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) of the most active station for the previous year"""
    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()

    session.close()

    # Convert the query results 
    tobs_list = []
    for prcp, date,tobs in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

#Dynamic Route 
#Start route + start/end route grouped together to follow DRY
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def Start_dates(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for a start date"""
    # Query all tobs
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of start_date_tobs
    starting_tobs = []
    starting_tobs_dict = {}
    for min, avg, max in results:

        starting_tobs_dict["min_temp"] = min
        starting_tobs_dict["avg_temp"] = avg
        starting_tobs_dict["max_temp"] = max
        starting_tobs.append(starting_tobs_dict) 
    return jsonify(starting_tobs)

@app.route("/api/v1.0/<start>/<end>")
def Start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for start and end dates"""
    # Query all tobs

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        
    session.close()
  
    # Create a dictionary from the row data and append to a list of start_end_date_tobs
    ending_tobs = []
    ending_tobs_dict = {}
    for min, avg, max in results:
        ending_tobs_dict["min_temp"] = min
        ending_tobs_dict["avg_temp"] = avg
        ending_tobs_dict["max_temp"] = max
        ending_tobs.append(ending_tobs_dict) 
    
    return jsonify(ending_tobs)

if __name__ == "__main__":
    app.run(debug=True)