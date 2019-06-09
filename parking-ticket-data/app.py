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
import numpy as np
from geopy.geocoders import Nominatim
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db.sqlite"
db = SQLAlchemy(app)

from .models import ParkingTickets


@app.before_first_request
def setup():
    db.drop_all()
    db.create_all()

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data/load")
def load_data():
    print('test')
    try:
        csv_tickets_1 = "parking-ticket-data/Resources/parking_tickets_2018/parkingData.csv"
        tickets_2015_df = pd.read_csv(csv_tickets_1)
        locations = list(tickets_2015_df["location2"])
        clean_locations = []

        for location in locations:
            try:
                if re.search(r'\d+\w+', location):
                    clean_locations.append(location)
            except:
                continue

        clean_locations1 = clean_locations[:933495]
        clean_locations2 = clean_locations[933495:]
        clean_locations1 = list(dict.fromkeys(clean_locations1))
        clean_locations2 = list(dict.fromkeys(clean_locations2))
        clean_locations = clean_locations1 + clean_locations2
        clean_locations = list(dict.fromkeys(clean_locations))
        df = pd.DataFrame({'location2': clean_locations})
        clean_df = pd.merge(tickets_2015_df, df, how="right", on='location2')
        limit = 5
        i = 0

        while i <= limit:
            try:
                i = i + 1
                clean_df1 = clean_df.iloc[i]
                geolocator = Nominatim(user_agent="parking_ticket_data")
                location = geolocator.geocode(clean_df1['location2'])

                parking_tickets = ParkingTickets(
                    date_of_infraction=clean_df1['date_of_infraction'],
                    infraction_code=clean_df1['infraction_code'],
                    infraction_description=clean_df1['infraction_description'],
                    set_fine_amount=clean_df1['set_fine_amount'],
                    time_of_infraction=clean_df1['set_fine_amount'],
                    location2=clean_df1['location2'],
                    lat=location.latitude,
                    long=location.longitude
                )

                db.session.add(parking_tickets)
                db.session.commit()
            except TypeError as e:
                print(e)
                continue
    except TypeError as e:
        print(e)

    return render_template("form.html")


@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        return redirect("/", code=302)

    return render_template("form.html")


@app.route("/api/data")
def data():
    try:
        parking_data = []
        results = db.session.query(ParkingTickets.location2, ParkingTickets.lat, ParkingTickets.long).all()

        for result in results:
            parking_object = {
                "lat": result[1],
                "lon": result[2],
                "address": result[0],
                "hoverinfo": "text",
                "marker": {
                    "size": 50,
                    "line": {
                        "color": "rgb(8,8,8)",
                        "width": 1
                    },
                }
            }
            parking_data.append(parking_object)

        return jsonify(parking_data)

        # return render_template("index.html", allParkingData=jsonify(parking_data))
    except TypeError as e:
        print(e)


if __name__ == "__main__":
    app.run()
