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
import re
import pandas as pd
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
                location = geolocator.geocode(clean_df1['location2'] + ' Toronto')

                parking_tickets = ParkingTickets(
                    date_of_infraction=clean_df1['date_of_infraction'].decode('utf-8'),
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

    return render_template("index.html")


@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        return redirect("/", code=302)

    return render_template("form.html")


@app.route("/api/get/data")
def get_data():
    results = db.session.query(
        ParkingTickets.location2,
        ParkingTickets.lat,
        ParkingTickets.long,
        ParkingTickets.date_of_infraction,
        # ParkingTickets.infraction_code,
        ParkingTickets.infraction_description,
        ParkingTickets.set_fine_amount,
        # ParkingTickets.time_of_infraction
    ).all()

    return jsonify(results)


@app.route("/api/data")
def data():
    try:
        parking_data = []
        results = db.session.query(
            ParkingTickets.location2,
            ParkingTickets.lat,
            ParkingTickets.long,
            ParkingTickets.date_of_infraction,
            # ParkingTickets.infraction_code,
            ParkingTickets.infraction_description,
            ParkingTickets.set_fine_amount,
            # ParkingTickets.time_of_infraction
        ).all()

        print(results)

        for result in results:
            parking_object = {
                "address": result[0],
                "coords": [result[1], result[2]],
                "date_of_infraction": result[3],
                "infraction_code": result[4],
                "infraction_description": result[5],
                "set_fine_amount": result[6],
                "time_of_infraction": result[7]
            }
            parking_data.append(parking_object)

        return jsonify(parking_data)
    except TypeError as e:
        print(e)


if __name__ == "__main__":
    app.run()
