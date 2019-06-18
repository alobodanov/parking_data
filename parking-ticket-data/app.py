# import necessary libraries
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    Markup
)
import json
import pandas as pd

import pymongo

app = Flask(__name__)

# Read data from CSV file
csv_tickets_1 = "parking-ticket-data/Resources/coords2.csv"
clean_df = pd.read_csv(csv_tickets_1)

# Mongodb connection set up
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.parking_db

# Drops collection if available to remove duplicates
# db.parking_tickets.drop()

# Creates a collection in the database and inserts data from csv
# for i in range(len(clean_df)):
#     clean_df1 = clean_df.iloc[i]
#
#     db.parking_tickets.insert(
#         {
#             "tag_number_masked": str(clean_df1['tag_number_masked']),
#             "date_of_infraction": str(clean_df1['date_of_infraction']),
#             "infraction_code": str(clean_df1['infraction_code']),
#             "infraction_description": clean_df1['infraction_description'],
#             "set_fine_amount": str(clean_df1['set_fine_amount']),
#             "time_of_infraction": float(clean_df1['time_of_infraction']),
#             "location2": clean_df1['location2'],
#             "coords": [
#                 clean_df1['lat'],
#                 clean_df1['lon']
#             ]
#         }
#     )
#     i = i + 1


def get_all_data():
    return list(db.parking_tickets.find({}))


clean_df_tmp = list(db.parking_tickets.find({}))
results = []
location_data = []


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
        location_data.append(parking_object)


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
    # create_json_structure(results)

    if request.method != 'GET':
        filter_data = json.loads(request.data)
        check = 0

        # filter_results = db.session.query(
        #     func.count(ParkingTickets.set_fine_amount),


        if filter_data["time_from"].replace(':', '').lstrip('0') == '':
            time_from_tmp = 0
        else:
            time_from_tmp = int(filter_data["time_from"].replace(':', '').lstrip('0'))

        if filter_data["time_to"].replace(':', '').lstrip('0') == '':
            time_to_tmp = 0
        else:
            time_to_tmp = int(filter_data["time_to"].replace(':', '').lstrip('0'))

        if filter_data["date"] or filter_data["time_from"] or filter_data["time_to"] or filter_data["address"] or filter_data["ticket_type"]:
            print('----------------->>>>>>>>>><<<<<<<<<<<-------------------')
            print(filter_data["date"])
            print(filter_data["time_from"])
            print(filter_data["time_to"])
            print(filter_data["address"])
            print(filter_data["ticket_type"])
            check = 1
            # filter_results = db.parking_tickets.find(
            #     {
            #         '$or': [


                        # {
                        #     'date_of_infraction': filter_data["date"]
                        # },
                        # {
                        #     'time_of_infraction': {
                        #         '$gte': time_from_tmp,
                        #         '$lte': time_to_tmp
                        #     }
                        # },
                        # {
                        #     "location2": {
                        #         "$regex": filter_data['address'], "$options": "i"
                        #     }
                        # },
                        # {
                        #     'infraction_description': filter_data["ticket_type"]
                        # }
            #         ]
            #     }
            # )
            filter_results = db.parking_tickets.find(
                {
                    'date_of_infraction': filter_data["date"],
                    'time_of_infraction': {
                                '$gte': time_from_tmp,
                                '$lte': time_to_tmp
                            },
                    "location2": {
                                "$regex": filter_data['address'], "$options": "i"
                            },
                    'infraction_description': filter_data["ticket_type"]
                }
            )
            print(list(filter_results))

        if check != 0:
            # print(filter_results)
            filter_results

                # (ParkingTickets.infraction_description).group_by(
                # ParkingTickets.location2).all()
        else:
            return json.dumps(data_formatter(get_all_data()))

        filtered_json = json_structure_for_filter(filter_results)
        return jsonify(data_formatter(filtered_json))


def data_formatter(format_data):
    address_data = []
    address_tmp_data = []

    for result in format_data:
        if result['location2'] in address_tmp_data:
            for address in address_data:
                if result['location2'] == address['address']:
                    tmp_obj = address['data']
                    tmp_obj.append({
                        # "total_fines": result['fine_count'],
                        "fine_amount": result['set_fine_amount'],
                        "infraction_description": result['infraction_description'],
                        "date_of_infraction": result['date_of_infraction']
                    })
                    address['data'] = tmp_obj
        else:
            address_data.append({
                "address": result['location2'],
                "coords": result['coords'],
                "data": [{
                    # "total_fines": result['fine_count'],
                    "fine_amount": result['set_fine_amount'],
                    "infraction_description": result['infraction_description'],
                    "date_of_infraction": result['date_of_infraction']
                }]})
            address_tmp_data.append(result['location2'])

    return address_data


if __name__ == "__main__":
    app.run()
