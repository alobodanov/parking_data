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
    def find_all(collection):
        return DB.DATABASE[collection].find({})

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find(query)

    @staticmethod
    def filter(collection, searched_data):
        print('----------------->>>>>>>>>>Filter from DB file<<<<<<<<<<<-------------------')
        print(searched_data["date"])
        print(searched_data["time_from"])
        print(searched_data["time_to"])
        print(searched_data["address"])
        print(searched_data["ticket_type"])

        if searched_data["time_from"].replace(':', '').lstrip('0') == '':
            time_from_tmp = 0
        else:
            time_from_tmp = int(searched_data["time_from"].replace(':', '').lstrip('0'))

        if searched_data["time_to"].replace(':', '').lstrip('0') == '':
            time_to_tmp = 0
        else:
            time_to_tmp = int(searched_data["time_to"].replace(':', '').lstrip('0'))

        return DB.DATABASE[collection].aggregate([
            {
                '$match': {
                    '$and': [
                        {
                            '$or': [
                                {'date_of_infraction': searched_data["date"]},
                            ]
                        },
                        {
                            '$or': [
                                {'infraction_description': searched_data["ticket_type"]}
                            ]
                        },
                        {
                            '$or': [
                                {"location2": {"$regex": searched_data['address'], "$options": "i"}}
                            ]
                        },
                        {
                            '$or': [
                                {
                                    'time_of_infraction': {
                                        '$gte': time_from_tmp,
                                        '$lte': time_to_tmp
                                    },
                                }
                            ]
                        }
                    ]
                }
            },
            # {
            #     '$count': "set_fine_amount"
            # }
            # {
            #     '$group': {
            #         '_id': '$infraction_description',
            #         'fine_count': {'$sum': '$set_fine_amount'}
            #     }
            # }
        ])
