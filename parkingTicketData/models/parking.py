import datetime

from parkingTicketData.database import DB


class Parking(object):

    def __init__(
            self,
            tag_number_masked,
            date_of_infraction,
            infraction_code,
            infraction_description,
            set_fine_amount,
            time_of_infraction,
            location2,
            coords
    ):
        self.tag_number_masked = tag_number_masked
        self.date_of_infraction = date_of_infraction
        self.infraction_code = infraction_code
        self.infraction_description = infraction_description
        self.set_fine_amount = set_fine_amount
        self.time_of_infraction = time_of_infraction
        self.location2 = location2
        self.coords = coords
        self.created_at = datetime.datetime.utcnow()

    def insert(self):
        DB.insert(collection='parking_tickets', data=self.json())

    def json(self):
        return {
            'tag_number_masked': self.tag_number_masked,
            'date_of_infraction': self.date_of_infraction,
            'infraction_code': self.infraction_code,
            'infraction_description': self.infraction_description,
            'set_fine_amount': self.set_fine_amount,
            'time_of_infraction': self.time_of_infraction,
            'location2': self.location2,
            'coords': self.coords,
            'created_at': self.created_at
        }
