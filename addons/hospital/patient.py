from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    patient_name = fields.Char(string="Patient Name")

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Patient Record'
    _rec_name = 'patient_name'
    sequence = fields.Char(string='Patient Id', required=True, copy=False, readonly=True, index=True,default=lambda self: _('New'))
    gender = fields.Selection([('male', 'Male'),('female', 'Female')])
    age_group = fields.Selection([('major','Major'),('minor','Minor')],string='Age Group',compute='set_age_group')
    patient_name = fields.Char(string="name")
    patient_age = fields.Integer('age',track_visibility='always')
    notes = fields.Text(string='Notes')
    patient_email = fields.Char(string="Email")
    appointment_count =fields.Integer(string='Appointment',compute='get_appointment_count')
    image = fields.Binary(string='image',attechment=True)
    patient_gender = fields.Selection([('Male', 'Male'),
                                       ('Female', 'Female')])


    @api.multi
    def print_report(self):
        return self.env.ref('hospital.report_hospital_patient_card').report_action(self)



    def action_confirm(self):
        for rec in self:
            rec.state ='confirm'


    def action_done(self):
        for rec in self:
            rec.state ='done'


    @api.depends('patient_age')
    def set_age_group(self):
        for rec in self:
            if rec.patient_age:
                if rec.patient_age < 10:
                    rec.age_group = 'minor'
                else:
                    rec.age_group = 'major'

    @api.constrains('patient_age')
    def Check_age(self):
        for rec in self:
            if rec.patient_age <= 10:
                raise ValidationError(_(f"Your age greater than 10"))

    @api.multi
    def open_patient_appointment(self):
        return {
            'name': _('Appointments'),
            'domain': [('patient_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def hospital_appointment_wizard(self):
        return {
            'name': 'Hospital Patient Record',
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.patient.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_name': 'Select Patient',
            },
        }

    def action_quotation_send(self):
        template_id = self.env.ref('hospital.email_template_hospital_patient').id
        template=self.env['mail.template'].browse(template_id)
        template.send_mail(self.id ,force_send=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New') == _('New')):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')
        res = super(HospitalPatient, self).create(vals)
        return res

    def get_appointment_count(self):
        count=self.env['hospital.appointment'].search_count([('patient_id','=',self.id)])
        self.appointment_count = count

    # state = fields.Selection([
    #         ('draft', 'draft'),
    #         ('confirm', 'confirm'),
    #         ('done', 'done'),
    #         ('cancel', 'cancelled'),
    #     ] , string='status',readonly=True,default='Draft')