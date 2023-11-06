from odoo import models, fields, _, api
from odoo.exceptions import ValidationError




# class CustommoduleXLS(models.AbstractModel):
#     _name = 'report.aaa.custom_module_report_xls'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, line):
#         c = 0
#         for lines in line:
#             c += 1
#             format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
#             format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
#             sheet = workbook.add_worksheet('Patient Card %s' % (c))
#             sheet.set_column(3, 3, 50)
#             sheet.set_column(2, 2, 30)
#             sheet.write(2, 2, 'Name', format1)
#             sheet.write(2, 3, lines.name, format2)
#             sheet.write(3, 2, 'Age', format1)
#             sheet.write(3, 3, lines.custom_age, format2)

class TestDoctor(models.Model):
    _name = "test.doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Doctor Record'
    _rec_name = 'doctor_name'


    @api.constrains('doctor_age')
    def Check_age(self):
        if self.doctor_age <= 10:
            raise ValidationError(_(f"Your age greater than 10"))


    doctor_name = fields.Char(string="name", required=True)
    doctor_age = fields.Integer('age')
    doctor_image = fields.Binary(string='image')
    doctor_department = fields.Char(string='Department')
    doctor_gender = fields.Selection([('Male','Male'),('Female','Female')])
    sequence = fields.Char(string='Doctor Id', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    PatientAppointment_id= fields.One2many('patient.appointment','patient_appoint_id' ,string='Patient Appointment model')

    appointment_doctor_id=fields.One2many('doctor.appointment','appointment_id' ,string='Appointment model')


    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New') == _('New')):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('test.doctor.sequence') or _('New')
        res = super(TestDoctor, self).create(vals)
        return res


class DoctorAppointment(models.Model):
    _name = "doctor.appointment"
    _description = 'Doctor Appointment Record'
    _rec_name = 'patient_name_appoint'

    patient_appointmentid_id = fields.Many2one('patient.appointment' ,string='Patient')
    patient_name_appoint = fields.Char(string='name')
    appointment_id = fields.Many2one('test.doctor' , string='Doctor Appointed for Patient')



class PatientAppointment(models.Model):
    _name = "patient.appointment"
    _description = 'Doctor Appointment Record'
    _rec_name = 'patient_name'

    @api.multi
    def name_get(self):
        rec = []
        for field in self:
            rec.append((field.id, '%s %s' % (field.patient_name, field.patient_sequence)))
        return rec
    patient_name = fields.Char(string="name", required=True)
    patient_age = fields.Integer('age')
    patient_image = fields.Binary(string='image')
    patient_gender = fields.Selection([('Male','Male'),('Female','Female')])
    patient_sequence = fields.Char(string='Patient Id', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))
    patient_appoint_id = fields.Many2one('test.doctor' , string='Doctor')
    doctor_gender = fields.Selection([('Male','Male'),('Female','Female')])

    @api.model
    def create(self, vals):
        if vals.get('patient_sequence', _('New') == _('New')):
            vals['patient_sequence'] = self.env['ir.sequence'].next_by_code('patient.appointment.sequence') or _('New')
        res = super(PatientAppointment, self).create(vals)
        return res

    @api.onchange('patient_appoint_id')
    def Select_gander(self):
        if self.patient_appoint_id:
            self.doctor_gender =self.patient_appoint_id.doctor_gender