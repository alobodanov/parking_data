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
from parkingTicketData.database import DB
from parkingTicketData.models.parking import Parking

app = Flask(__name__)

# Read data from CSV file
csv_tickets_1 = "parkingTicketData/Resources/coords2.csv"
clean_df = pd.read_csv(csv_tickets_1)

DB.init()

# Creates a collection in the database and inserts data from csv
for i in range(len(clean_df)):
    clean_df1 = clean_df.iloc[i]

    new_data = Parking(
        tag_number_masked=str(clean_df1['tag_number_masked']),
        date_of_infraction=str(clean_df1['date_of_infraction']),
        infraction_code=str(clean_df1['infraction_code']),
        infraction_description=clean_df1['infraction_description'],
        set_fine_amount=str(clean_df1['set_fine_amount']),
        time_of_infraction=float(clean_df1['time_of_infraction']),
        location2=clean_df1['location2'],
        coords=[
            clean_df1['lat'],
            clean_df1['lon']
        ]
    )

    new_data.insert()
    i = i + 1


def get_all_data():
    return list(DB.find_all('parking_tickets'))


clean_df_tmp = get_all_data()
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


@app.route("/", methods=['GET'])
def home():
    return render_template("index.html", seldesc=Markup(list(clean_df['infraction_description'].unique())))


@app.route("/api/get/data", methods=['GET'])
def get_data():
    return jsonify(results)


@app.route("/api/architecture", methods=['GET'])
def architecture():
    return render_template("architecture-diagram.html")


@app.route("/api/filter", methods=['GET', 'POST'])
def filter_search():
    if request.method != 'GET':
        filter_data = json.loads(request.data)
        check = 1

        if filter_data["date"] or \
                filter_data["time_from"] or \
                filter_data["time_to"] or \
                filter_data["address"] or \
                filter_data["ticket_type"]:

            check = 0
            filter_results = DB.filter('parking_tickets', filter_data)

        if check == 1:
            return json.dumps(data_formatter(get_all_data()))

        print(list(filter_results))

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


@app.errorhandler(404)
def page_not_found(e):
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }

    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run()
