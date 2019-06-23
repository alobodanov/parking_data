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
        final_results = []
        address_data = []
        address_tmp_data = [results[0]["location2"]]
        description_tmp_data =[results[0]["infraction_description"]]
        data=[]
        small_object={
                        "fine_amount": results[0]['set_fine_amount'],
                        "infraction_description": results[0]['infraction_description'],
                        #"date_of_infraction": results[0]['date_of_infraction'],
                        "total_fines":1
                        }
        big_object={
                    "address":results[0]["location2"],
                    "coords":results[0]["coords"],
                    "data":data
                }

        if results.count()>1:
            
            for result in results:
                
                if result['location2'] in address_tmp_data:
                    
                    if result["infraction_description"] in description_tmp_data:
                        
                        small_object["total_fines"]+=1
                    else:
                        
                        data.append(small_object)
                        small_object={
                            "fine_amount": result['set_fine_amount'],
                            "infraction_description": result['infraction_description'],
                            
                            "total_fines":1
                            }
                else:
                   
                    data.append(small_object)
                    big_object["data"] = data
                    final_results.append(big_object)
                    data=[]
                    big_object={
                        "address":result["location2"],
                        "coords":result["coords"],
                        "data":data
                    }
                    small_object={
                            "fine_amount": result['set_fine_amount'],
                            "infraction_description": result['infraction_description'],
                            
                            "total_fines":1
                            }
                    address_tmp_data.append(result["location2"])
                    description_tmp_data.append(result["infraction_description"])
        else:
            
            data.append(small_object)
            big_object["data"] = data
            final_results.append(big_object)
        
        if not final_results:
            data.append(small_object)
            big_object["data"] = data
            final_results.append(big_object)
        
        print(final_results)

        return final_results
