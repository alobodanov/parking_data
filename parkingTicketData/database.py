import pymongo


class DB(object):
    URI = "mongodb://127.0.0.1:27017"

    @staticmethod
    def init():
        client = pymongo.MongoClient(DB.URI)
        DB.DATABASE = client['parking_db']
        DB.DATABASE.parking_tickets.drop()

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def insert_parking(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def find_all(collection):
        return DB.DATABASE[collection].find({})

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find(query)

    @staticmethod
    def filter(collection, searched_data):
        if searched_data["time_from"].replace(':', '').lstrip('0') == '':
            time_from_tmp = 0
        else:
            time_from_tmp = int(searched_data["time_from"].replace(':', '').lstrip('0'))

        if searched_data["time_to"].replace(':', '').lstrip('0') == '':
            time_to_tmp = 0
        else:
            time_to_tmp = int(searched_data["time_to"].replace(':', '').lstrip('0'))

        filter_statments = [
            {
                '$match': {
                    '$and': [

                    ]
                },
            },
            {
                '$group': {
                    '_id': {
                        'location2': '$location2',
                        'infraction_description': '$infraction_description'
                    },
                }
            },
            # {
            #     '$group': {
            #         '_id': '$_id.location2',
            #         'address': {'$addToSet': '$location2'},
            #         'coords': {'$addToSet': '$coords'},
            #         'total_fines': {'$sum': 1},
            #         'data': {
            #             '$mergeObjects': {
            #                 '$infraction_description',
            #                 '$date_of_infraction',
            #                 '$set_fine_amount',
            #                 # 'infraction_description': '$infraction_description',
            #                 # 'date_of_infraction': '$date_of_infraction',
            #                 # 'set_fine_amount': '$set_fine_amount',
            #                 # 'total_fines': {'$sum': 1},
            #             }
            #         }
            #     }
            # }
        ]

        if searched_data["date"]:
            filter_statments[0]['$match']['$and'].append(
                {"date_of_infraction": {"$regex": searched_data['date'], "$options": "i"}}
            )

        if searched_data["time_from"] and searched_data["time_to"]:
            filter_statments[0]['$match']['$and'].append({
                '$or': [
                    {
                        'time_of_infraction': {
                            '$gte': time_from_tmp,
                            '$lte': time_to_tmp
                        },
                    }
                ]
            })

        if searched_data["address"]:
            filter_statments[0]['$match']['$and'].append({
                "location2": {"$regex": searched_data['address'], "$options": "i"}
            })

        if searched_data["ticket_type"] and searched_data["ticket_type"] != "":
            filter_statments[0]['$match']['$and'].append(
                {'infraction_description': searched_data["ticket_type"]}
            )

        return DB.DATABASE[collection].aggregate(
            filter_statments,
        )
