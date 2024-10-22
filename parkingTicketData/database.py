import pymongo
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

DATABASE_CONFIG = {
    'MONGO_HOST': 'ds241097.mlab.com',
    'MONGO_PORT': 41097,
    'MONGO_DBNAME': 'heroku_flgb1cjr',
    'MONGO_USERNAME': 'devUser',
    'MONGO_PASSWORD': 'z3HzHYmk83g7Lc',
    'MONGO_AUTH_SOURCE': 'admin'
}


class DB(object):
    DATABASE = None

    @staticmethod
    def init():
        client = pymongo.MongoClient(DATABASE_CONFIG['MONGO_HOST'], DATABASE_CONFIG['MONGO_PORT'])
        DB.DATABASE = client[DATABASE_CONFIG['MONGO_DBNAME']]
        DB.DATABASE.authenticate(DATABASE_CONFIG['MONGO_USERNAME'], DATABASE_CONFIG['MONGO_PASSWORD'])
        DB.DATABASE.parking_tickets.drop()

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def find_all(collection):
        return DB.DATABASE[collection].find({})

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find(query)

    @staticmethod
    def filter(collection, searched_data):
        filter_statments = [
            {
                '$and': [

                ]
            },
        ]

        if searched_data["date"]:
            filter_statments[0]['$and'].append(
                {"date_of_infraction": {"$regex": searched_data['date'], "$options": "i"}}
            )

        if searched_data["time_from"] and searched_data["time_to"]:
            filter_statments[0]['$and'].append({
                '$or': [
                    {
                        'time_of_infraction': {
                            '$gte': 0 if searched_data["time_from"].replace(':', '').lstrip('0') == ''
                                        else int(searched_data["time_from"].replace(':', '').lstrip('0')),
                            '$lte': 0 if searched_data["time_to"].replace(':', '').lstrip('0') == ''
                                        else int(searched_data["time_to"].replace(':', '').lstrip('0'))
                        },
                    }
                ]
            })

        if searched_data["address"]:
            filter_statments[0]['$and'].append({
                "location2": {"$regex": searched_data['address'], "$options": "i"}
            })

        if searched_data["ticket_type"] and searched_data["ticket_type"] != "":
            filter_statments[0]['$and'].append(
                {'infraction_description': searched_data["ticket_type"]}
            )

        results=DB.DATABASE[collection].find(
            filter_statments[0],
        ).sort([
            ("location2", pymongo.ASCENDING),
            ("infraction_description", pymongo.DESCENDING)
        ])

        final_result = []
        address_list = []
        description_list = []
        # i = 0
        
        for i in range(results.count()):
            if results[i]['location2'] in address_list:
                for address in final_result:
                    if address["address"] == results[i]['location2']:                   
                        for data in address['data']:
                            if results[i]['infraction_description'] \
                                    in description_list \
                                    and results[i]['infraction_description' ]== data["infraction_description"]:

                                data["total_fines"] = data["total_fines"]+1   
                            elif results[i]['infraction_description'] in description_list:
                                continue
                            else:
                                address['data'].append({
                                    "fine_amount": results[i]['set_fine_amount'],
                                    "infraction_description": results[i]['infraction_description'],
                                    "total_fines":1
                                })
                                description_list.append(results[i]['infraction_description'])
                                break
                       
            else:
                final_result.append({
                    "address": results[i]["location2"],
                    "coords": results[i]["coords"],
                    "data": [{
                        "fine_amount": results[i]['set_fine_amount'],
                        "infraction_description": results[i]['infraction_description'],
                        "total_fines":1
                    }]
                })

                address_list.append(results[i]["location2"])
                description_list = []
                description_list.append(results[i]['infraction_description'])

        return final_result
