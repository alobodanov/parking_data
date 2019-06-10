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

db.drop_all()
db.create_all()
# Load data into DB
csv_tickets_1 = "parking-ticket-data/Resources/parking_tickets_2018/parkingData.csv"
tickets_2015_df = pd.read_csv(csv_tickets_1)
locations = list(tickets_2015_df["location2"])
clean_locations = []

for location in locations:
    if re.search(r'\d+\w+', location):
        clean_locations.append(location)

clean_locations1 = clean_locations[:933495]
clean_locations2 = clean_locations[933495:]
clean_locations1 = list(dict.fromkeys(clean_locations1))
clean_locations2 = list(dict.fromkeys(clean_locations2))
clean_locations = clean_locations1 + clean_locations2
clean_locations = list(dict.fromkeys(clean_locations))
df = pd.DataFrame({'location2': clean_locations})
clean_df = pd.merge(tickets_2015_df, df, how="right", on='location2')

limit = 0
parking_tickets = {}

i = 0

for i in range(len(clean_df)):
    clean_df1 = clean_df.iloc[i]
    geolocator = Nominatim(user_agent="parking_ticket_data")
    location = geolocator.geocode(clean_df1['location2'] + ' Toronto')
    parking_tickets = {
        "tag_number_masked": str(clean_df['tag_number_masked']),
        "date_of_infraction": str(clean_df1['date_of_infraction']),
        # "infraction_code": clean_df1['infraction_code'],
        "infraction_description": clean_df1['infraction_description'],
        "set_fine_amount": clean_df1['set_fine_amount'],
        "time_of_infraction": str(clean_df1['time_of_infraction']),
        "location2": clean_df1['location2'],
        "lat": location.latitude,
        "long": location.longitude
    }

    ParkingTickets(**parking_tickets)
    db.session.add(ParkingTickets(**parking_tickets))
    db.session.commit()
    i = i + 1

#TODO coords array
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
    return render_template("index.html")


@app.route("/api/get/data")
def get_data():
    return jsonify(results)


if __name__ == "__main__":
    app.run()
