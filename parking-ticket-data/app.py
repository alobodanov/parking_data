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
import sqlalchemy
from sqlalchemy import func

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
        # "lat": 0,
        # "long": 0,
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
    return render_template("index.html", seldesc=Markup(list(clean_df['infraction_description'].unique())))


@app.route("/api/get/data")
def get_data():
    return jsonify(results)


@app.route("/api/filter", methods=['POST', 'GET'])
def filter_search():
    if request.method != 'POST':
        return render_template('index.html')

    filter_data = request.form
    print(filter_data['ticket_type'])
    #print(filter_data['time'])
    print(filter_data['address'])
    #print(filter_data['date'])
    print("------------------")
    filtered_final = []
    print(filter_data['ticket_type'])
    print(filter_data['address'])
    # all 4 filters
    if (filter_data['ticket_type'] and filter_data['address'] and filter_data['time'] and filter_data['date']):
        filter_results = db.session.query(\
        func.sum(ParkingTickets.set_fine_amount),\
        func.avg(ParkingTickets.set_fine_amount),\
        ParkingTickets.location2).filter(ParkingTickets.location2==filter_data['address'])\
        .filter(ParkingTickets.date_of_infraction==filter_data['date'])\
        .filter(ParkingTickets.infraction_description==filter_data['ticket_type'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: ticket_type, address, time
    elif (filter_data['ticket_type'] and filter_data['address'] and filter_data['time']):
        filter_results = db.session.query(\
        func.sum(ParkingTickets.set_fine_amount),\
        func.avg(ParkingTickets.set_fine_amount),\
        ParkingTickets.location2).filter(ParkingTickets.location2==filter_data['address'])\
        .filter(ParkingTickets.infraction_description==filter_data['ticket_type'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: ticket_type, address, date
    elif (filter_data['ticket_type'] and filter_data['address'] and filter_data['time']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.location2==filter_data['address'])\
        .filter(ParkingTickets.infraction_description==filter_data['ticket_type'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['date'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: time, address, date
    elif (filter_data['date'] and filter_data['address'] and filter_data['time']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.location2==filter_data['address'])\
        .filter(ParkingTickets.infraction_description==filter_data['date'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: time, address
    elif (filter_data['address'] and filter_data['time']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['address'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: time, date
    elif (filter_data['date'] and filter_data['time']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['date'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: address, date
    elif (filter_data['address'] and filter_data['date']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['date'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['address'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: time, ticket_type
    elif (filter_data['time'] and filter_data['ticket_type']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['ticket_type'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: ticket_type, date
    elif (filter_data['ticket_type'] and filter_data['date']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['date'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['ticket_type'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: ticket_type, address
    elif (filter_data['address'] and filter_data['ticket_type']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['address'])\
        .filter(ParkingTickets.time_of_infraction==filter_data['ticket_type'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: address
    elif (filter_data['address']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['address'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: ticket_type
    elif (filter_data['ticket_type']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['ticket_type'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: time
    elif (filter_data['time']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['time'])\
        .group_by(ParkingTickets.location2).all()
    #filter by: date
    elif (filter_data['date']):
        filter_results = db.session.query(
        func.sum(ParkingTickets.set_fine_amount),
        func.avg(ParkingTickets.set_fine_amount),
        ParkingTickets.location2).filter(ParkingTickets.infraction_description==filter_data['date'])\
        .group_by(ParkingTickets.location2).all()
    else:
        return render_template('index.html', data_filtered=Markup(parking_data))

    for result in filter_results:
        filtered_object = {
            "total_fines":result[0],
            "average_fine":result[1],
            "address":result[2]
            }
        filtered_final.append(filtered_object)

    return render_template('index.html', data_filtered=Markup(filtered_final))


if __name__ == "__main__":
    app.run()
