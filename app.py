from flask import Flask, jsonify
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    session.close()
    
    print(results)
    
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():

    session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    results = session.query(Station.station).all()

    session.close()
    
    print(results)

    stations = list(np.ravel(results))
    print(stations)
    
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)

    print(results)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run(debug=True)
