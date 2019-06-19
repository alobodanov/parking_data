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
from sqlalchemy import func, between

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
csv_tickets_1 = "parking-ticket-data/Resources/coord600.csv"
clean_df = pd.read_csv(csv_tickets_1)
locations = list(clean_df["location2"])
parking_tickets = {}

parking_data = []
i = 0

for i in range(len(clean_df)):
    clean_df1 = clean_df.iloc[i]

    parking_tickets = {
        "tag_number_masked": str(clean_df['tag_number_masked']),
        "date_of_infraction": str(clean_df1['date_of_infraction']),
        "infraction_code": str(clean_df1['infraction_code']),
        "infraction_description": clean_df1['infraction_description'],
        "set_fine_amount": clean_df1['set_fine_amount'],
        "time_of_infraction": float(clean_df1['time_of_infraction']),
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


def create_json_structure(results_data):
    for result in results_data:
        parking_object = {
            "address": result[0],
            "coords": [result[1], result[2]],
            "date_of_infraction": result[3],
            # "infraction_code": result[4],
            "infraction_description": result[4],
            "set_fine_amount": result[5],
            "time_of_infraction": result[6],
            "fine_count": ""
        }
        parking_data.append(parking_object)


def json_structure_for_filter(filtered_data):
    filtered_json = []

    for result_json in filtered_data:
        filtered_object = {
            "address": result_json[2],
            "coords": [result_json[3], result_json[4]],
            "date_of_infraction": result_json[6],
            # "infraction_code": result[4],
            "infraction_description": result_json[5],
            "set_fine_amount": result_json[1],
            "fine_count": result_json[0]
            # "time_of_infraction": result_json[6]
        }
        filtered_json.append(filtered_object)

    return filtered_json


@app.route("/api/data")
def data():
    return json.dumps(parking_data)


@app.route("/")
def home():
    return render_template("index.html", seldesc=Markup(list(clean_df['infraction_description'].unique())))


@app.route("/api/get/data")
def get_data():
    return jsonify(results)


@app.route("/api/architecture")
def architecture():
    return render_template("architecture-diagram.html")


@app.route("/api/filter", methods=['GET', 'POST'])
def filter_search():
    create_json_structure(results)

    if request.method != 'GET':
        filter_data = json.loads(request.data)
        check = 0

        filter_results = db.session.query(
            func.count(ParkingTickets.set_fine_amount),
            ParkingTickets.set_fine_amount,
            ParkingTickets.location2,
            ParkingTickets.lat,
            ParkingTickets.long,
            ParkingTickets.infraction_description,
            ParkingTickets.date_of_infraction,
            ParkingTickets.time_of_infraction
        )

        if filter_data["time_from"].replace(':', '').lstrip('0') == '':
            time_from_tmp = 0
        else:
            time_from_tmp = int(filter_data["time_from"].replace(':', '').lstrip('0'))

        if filter_data["time_to"].replace(':', '').lstrip('0') == '':
            time_to_tmp = 0
        else:
            time_to_tmp = int(filter_data["time_to"].replace(':', '').lstrip('0'))

        if filter_data["date"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.date_of_infraction == filter_data["date"])

        if filter_data["time_from"] and filter_data["time_to"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.time_of_infraction >= time_from_tmp)\
                .filter(ParkingTickets.time_of_infraction <= time_to_tmp)

        if filter_data["address"]:
            check = 1
            filter_results = filter_results.filter(ParkingTickets.location2.like("%" + filter_data["address"].upper() + "%"))

        if filter_data["ticket_type"] and filter_data["ticket_type"] != "":
            check = 1
            filter_results = filter_results.filter(ParkingTickets.infraction_description == filter_data["ticket_type"])

        if check != 0:
            filter_results = filter_results.group_by(ParkingTickets.infraction_description).group_by(
                ParkingTickets.location2).all()
        else:
            return json.dumps(data_formatter(parking_data))

        filtered_json = json_structure_for_filter(filter_results)
        return jsonify(data_formatter(filtered_json))


def data_formatter(format_data):
    address_data = []
    address_tmp_data = []

    for result in format_data:
        if result['address'] in address_tmp_data:
            for address in address_data:
                if result['address'] == address['address']:
                    tmp_obj = address['data']
                    tmp_obj.append({
                        "total_fines": result['fine_count'],
                        "fine_amount": result['set_fine_amount'],
                        "infraction_description": result['infraction_description'],
                        "date_of_infraction": result['date_of_infraction']
                    })
                    address['data'] = tmp_obj
        else:
            address_data.append({
                "address": result['address'],
                "coords": result['coords'],
                "data": [{
                    "total_fines": result['fine_count'],
                    "fine_amount": result['set_fine_amount'],
                    "infraction_description": result['infraction_description'],
                    "date_of_infraction": result['date_of_infraction']
                }]})
            address_tmp_data.append(result['address'])

    return address_data


if __name__ == "__main__":
    app.run()
