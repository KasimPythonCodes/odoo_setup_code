from odoo import models, fields, api, _

class HospitalPatientWizard(models.Model):
    _name = 'hospital.patient.wizard'
    _description = 'Patient Record Wizard'

    patient_id = fields.Many2one('hospital.patient', string="Patient")
    appointment_date = fields.Date(string="Appointment Date")

    def create_appointment(self):
        vals = {
            'patient_id': self.patient_id.id,
            'appointment_date': self.appointment_date,
            'notes': 'Created From The Wizard/Code'
        }
        self.patient_id.message_post(body="Appointment Created Successfully", subject="Appointment")
        self.env['hospital.appointment'].create(vals)