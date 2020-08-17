# imports dependancy 
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import os
# sets base folder to current folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# creates engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# starts app
app = Flask(__name__)



@app.route("/")
# creates home page with a list of other pages 
def home():
    return ("Home Page<br/>"
    "Possible routes<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/mm-dd-yr<br/>"
    "/api/v1.0/mm-dd-yr/mm-dd-yr<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # finds the date for the last 12 months 
    dates = session.query(Measurement.date).all()
    last_date= str(dates[-1])
    last_date = last_date[2:-3]
    year_one = str(int(last_date[0:4]) - 1) + last_date[4:]
    # creates a dict for storing data
    prcp_dict = {}
    # pulls data and prcp information from the last 12 months 
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
             filter(Measurement.date >= year_one)
    # stores date in dictionary 
    for row in prcp_query:
        prcp_dict[row[0]] = row[1]
    session.close()
    # returns a jsonify dict 
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    stats = session.query(Station.name)
    stat_list = []
    # finds a list of station names 
    for stat in stats:
        stat_list.append(stat)
    session.close()
    # returns a jsonify list
    return jsonify(stat_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # finds the dates for the previos year 
    dates = session.query(Measurement.date).all()
    last_date= str(dates[-1])
    last_date = last_date[2:-3]
    year_one = str(int(last_date[0:4]) - 1) + last_date[4:]
    year_two = str(int(year_one[0:4]) - 1) + year_one[4:]
    temp_dict = {}
    # finds the temp measuremnts for the most active station for the previos year
    stat_list = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.prcp))
    highst_stat = stat_list[-1][0]
    temp_query = session.query(Measurement.date, Measurement.tobs).\
                      filter(Measurement.date <= year_one).\
                      filter(Measurement.date >= year_two).\
                      filter(Measurement.station == stat_list[-1][0])
    for row in temp_query:
        temp_dict[row[0]] = row[1]

    session.close()
    # returns a jsonify dict
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_dict = {}
    # calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    start_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date >= start)
    for row in start_query:
        start_dict["TMIN"] = row[0]
        start_dict["TAVG"] = row[1]
        start_dict["TMAX"] = row[2]

    session.close()
    # returns a jsonify dict
    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def st_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    st_end_dict = {}
    st_end_query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date <= end).\
             filter(Measurement.date >= start)
    # calculate `TMIN`, `TAVG`, and `TMAX` for all dates between the given start and end date
    for row in st_end_query:
        st_end_dict["TMIN"] = row[0]
        st_end_dict["TAVG"] = row[1]
        st_end_dict["TMAX"] = row[2]

    session.close()
    # returns a jsonify dict
    return jsonify(st_end_dict)
if __name__ == "__main__":
    app.run(debug=True)
