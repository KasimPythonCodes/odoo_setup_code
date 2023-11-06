from odoo import models ,fields ,_,api


# /home/kasim/Downloads/odoo-11.0/addons/doctor/doctor.py

class CreateAppointment(models.TransientModel):
    _name = 'create.appointment'
    _description = 'Create Appointment'

    patient_id = fields.Many2one('patient.appointment' , string='Patient')
    appointment_date = fields.Date(string='Appointment Date')

    def create_appointment(self):
        vals={
            'patient_id': self.patient_id.id,
            'appointment_date': self.appointment_date

         }
        self.env['patient.appointment'].create(vals)
