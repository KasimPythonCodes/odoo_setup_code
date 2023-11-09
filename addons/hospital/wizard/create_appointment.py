from odoo import models, fields, _, api


class CreateAppointment(models.TransientModel):
    _name = 'create.appointment'
    _description = 'Create Appointment'

    patient_id = fields.Many2one('hospital.patient', string='Patient')
    appointment_date = fields.Date(string='Appointment Date')

    @api.multi
    def print_report(self):
        data = {
            'model': 'create.appointment',
            'form': self.read()[0]
        }
        return self.env.ref('hospital.report_appointment_ids').report_action(self, data=data)

    def create_appointment(self):
        vals = {
            'patient_id': self.patient_id.id,
            'appointment_date': self.appointment_date

        }
        self.patient_id.message_post(body="Appointment Created Successfully", subject="Appointment")
        self.env['hospital.appointment'].create(vals)
