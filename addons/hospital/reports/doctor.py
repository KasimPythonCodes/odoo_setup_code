from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    description = 'Doctor Report'
    _rec_name = 'doctor_name'

    doctor_name = fields.Char(string="Doctor Name", required=True)
    doctor_department = fields.Char(string="Doctor Department")
    doctor_gender = fields.Selection([
        ('male', 'male'),
        ('female', 'female'),
    ] ,string="Gender")
    # patient_id = fields.Many2one('hospital.patient', string='')
