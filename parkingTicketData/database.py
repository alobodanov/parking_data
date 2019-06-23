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
                '$and':[]
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
                            '$gte': time_from_tmp,
                            '$lte': time_to_tmp
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
        ).sort([("location2", pymongo.ASCENDING), ("infraction_description", pymongo.DESCENDING)])

        final_result = []
        address_list=[]
        description_list=[] 
        i=0
        
        for i in range(results.count()):
            if results[i]['location2'] in address_list:
                for address in final_result:
                    if address["address"] == results[i]['location2']:                   
                        for data in address['data']:
                            if results[i]['infraction_description'] in description_list and results[i]['infraction_description']==data["infraction_description"]:
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
                    "address":results[i]["location2"],
                    "coords":results[i]["coords"],
                    "data":[{
                        "fine_amount": results[i]['set_fine_amount'],
                        "infraction_description": results[i]['infraction_description'],
                        "total_fines":1
                        }]
                })
                address_list.append(results[i]["location2"])
                description_list=[]
                description_list.append(results[i]['infraction_description'])

        return final_result
