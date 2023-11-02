from odoo import models, fields


class HotelManagement(models.Model):
    _name = "hotel.management"
    _description = "Hotel Record"

    hotel_name = fields.Char(string="Name")
    customer_name = fields.Char(string="Name")
    customer_age = fields.Integer("age")
