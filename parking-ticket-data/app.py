# import necessary libraries
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    Markup
)
import json
import re
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db.sqlite"
db = SQLAlchemy(app)

from .models import ParkingTickets

# @app.before_first_request
# def setup():
# db.drop_all()
# db.create_all()

db.drop_all()
db.create_all()
# Load data into DB
csv_tickets_1 = "parking-ticket-data/Resources/coords2.csv"
clean_df = pd.read_csv(csv_tickets_1)
locations = list(clean_df["location2"])
parking_tickets = {}

i = 0

for i in range(len(clean_df)):
    clean_df1 = clean_df.iloc[i]

    parking_tickets = {
        "tag_number_masked": str(clean_df['tag_number_masked']),
        "date_of_infraction": str(clean_df1['date_of_infraction']),
        # "infraction_code": clean_df1['infraction_code'],
        "infraction_description": clean_df1['infraction_description'],
        "set_fine_amount": clean_df1['set_fine_amount'],
        "time_of_infraction": str(clean_df1['time_of_infraction']),
        "location2": clean_df1['location2'],
        "lat": clean_df1['lat'],
        "long": clean_df1['lon']
    }

    ParkingTickets(**parking_tickets)
    db.session.add(ParkingTickets(**parking_tickets))
    db.session.commit()
    i = i + 1

# TODO coords array
results = db.session.query(
    ParkingTickets.location2,
    ParkingTickets.lat,
    ParkingTickets.long,
    ParkingTickets.date_of_infraction,
    # ParkingTickets.infraction_code,
    ParkingTickets.infraction_description,
    ParkingTickets.set_fine_amount,
    ParkingTickets.time_of_infraction
).all()

data_all = json.dumps(results)
parking_data = []

for result in results:
    parking_object = {
        "address": result[0],
        "coords": [result[1], result[2]],
        "date_of_infraction": result[3],
        # "infraction_code": result[4],
        "infraction_description": result[4],
        "set_fine_amount": result[5],
        "time_of_infraction": result[6]
    }
    parking_data.append(parking_object)


@app.route("/api/data")
def data():
    return json.dumps(parking_data)


# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html", seldesc=Markup(list(clean_df['infraction_description'].unique())))


@app.route("/api/get/data")
def get_data():
    return jsonify(results)


@app.route("/api/filter", methods=['GET', 'POST'])
def filter_search():
    if request.method != 'GET':
        filter_data = json.loads(request.data)
        check = 0

        filter_results = db.session.query(func.count(ParkingTickets.set_fine_amount), func.avg(ParkingTickets.set_fine_amount),ParkingTickets.location2, ParkingTickets.lat, ParkingTickets.long)
        if filter_data["date"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.date_of_infraction == filter_data["date"])
        if filter_data["time"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.time_of_infraction == filter_data["time"])
        if filter_data["address"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.location2 == filter_data["address"])
        if filter_data["ticket_type"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.infraction_description == filter_data["ticket_type"])
        if check != 0:
            filter_results = filter_results.group_by(ParkingTickets.location2).all()
        else:
            return json.dumps(parking_data)

        filtered_final = []

        for result in filter_results:
            filtered_object = {
                "total_fines": result[0],
                "average_fine": result[1],
                "address": result[2],
                "coords": [result[3],result[4]]
            }
            filtered_final.append(filtered_object)

        return jsonify(filtered_final)


if __name__ == "__main__":
    app.run()
