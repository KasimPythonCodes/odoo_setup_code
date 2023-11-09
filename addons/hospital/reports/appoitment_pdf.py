from odoo import api, models, _


class AppointmentReport(models.AbstractModel):
    _name = 'report.hospital.appointment_report'
    _description = 'Appointment Report'

    @api.multi
    def print_report(self):
        print("LLLLLLLLLLLLLLLLLLLLLLLLL")
        return self.env.ref('hospital.report_appointment_ids').report_action(self)

    # @api.model
    # def get_report_values(self, docids, data=None):
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': 'hospital.patient',
    #         'docs': self.env['hospital.patient'].browse(docids),
    #         # Other data you want to pass to the report template
    #     }

    # @api.model
    # def get_report_values(self, docids, data=None):
    #     print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    #     if data['form']['patient_id']:
    #         appointments = self.env['hospital.appointment'].search([('patient_id', '=', data['form']['patient_id'][0])])
    #     else:
    #         appointments = self.env['hospital.appointment'].search([])
    #     print(appointments, "AAAAAAAAAAAAAAAAAAAAAA")
    #     return {
    #
    #         'doc_model': 'hospital.patient',
    #         'appointments': appointments,
    #         # Other data you want to pass to the report template
    #     }
