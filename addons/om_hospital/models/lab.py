from odoo import models, fields


# Creating New Model/ Database Table
class HospitalLab(models.Model):
    _name = 'hospital.lab'
    _description = 'Hospital Laboratory'

    name = fields.Char(string="Name", required=True)
    user_id = fields.Many2one('hospital.doctor', string='Responsible')