from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartners(models.Model):
    _inherit = 'res.partner'

    #OverRide Create Method Of a Model
    @api.model
    def create(self, vals_list):
        res = super(ResPartners, self).create(vals_list)
        print("yes working")
        # do the custom coding here
        return res



class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_name'

    @api.multi
    def test_cron_job(self):
        print("vaibhav")
        #code according to excute the cron

    patient_name = fields.Char(string='Name', required=True, track_visibility="always")
    patient_age = fields.Integer('Age', track_visibility="always")
    notes = fields.Text(string="notes")
    image = fields.Binary(string="Image", attachment=True)
    name = fields.Char(string="Test")
    patient_contact = fields.Char(string="Contact Number", required=True)
    name_seq = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('new'))
    patient_gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female')],
                                      required=True, track_visibility=True)
    age_group = fields.Selection(string="Age_Group", selection=[('major', 'major'), ('minor', 'minor')],
                                 compute='set_age_group')
    appointment_count = fields.Integer(string='Appointment', compute='get_appointment_count')
    active = fields.Boolean("Active", default=True)
    patient_email = fields.Char(string="Email")
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female'),
    ], string="Doctor Gender")
    patient_name_upper = fields.Char(compute='_patient_upper_name', inverse='_patient_inverse_upper_name')


    @api.depends('patient_name')
    def _patient_upper_name(self):
        for rec in self:
            rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False

    def _patient_inverse_upper_name(self):
        for rec in self:
            rec.patient_name = rec.patient_name_upper.lower() if rec.patient_name_upper else False

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('om_hospital', 'email_template_hospital_patient')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hospital.patient',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "om_hospital.mail_template_data_notification_email_hospital_patient",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.onchange('doctor_id')
    def set_doctor_gender(self):
        for rec in self:
            if rec.doctor_id:
                rec.doctor_gender = rec.doctor_id.gender

    @api.multi
    def open_patient_appointments(self):
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

    def get_appointment_count(self):
        count = self.env['hospital.appointment'].search_count([('patient_id', '=', self.id)])
        self.appointment_count = count

    @api.constrains('patient_age')
    def check_age(self):
        for rac in self:
            if rac.patient_age <= 5:
                raise ValidationError(_('The Must be Greater than 5'))


    @api.depends('patient_age')
    def set_age_group(self):
        for rac in self:
            if rac.patient_age:
                if rac.patient_age < 18:
                    rac.age_group = 'minor'
                else:
                    rac.age_group = 'major'
    @api.multi
    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.patient_name, rec.name_seq)))
        return res


    #     @api.depends('patient_name')
    #     def _compute_upper_name(self):
    #         for rec in self:
    #             rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False
    #
    # class HospitalManagementAPI(models.Model):
    #     _name = 'custom.module.api'
    #     _description = 'Custom Module API'
    #
    #     name = fields.Char(string='Name')
    #     description = fields.Text(string='Description')

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')
        result = super(HospitalPatient, self).create(vals)
        return result

    # @api.model
    # def update_custom_model_record(self, record_id, vals):
    #     record = self.env['hospital.patient'].browse(record_id)
    #     if record:
    #         return record.write(vals)
    #     return False
    #
    # @api.model
    # def delete_custom_model_record(self, record_id):
    #     record = self.env['hospital.patient'].browse(record_id)
    #     if record:
    #         return record.unlink()
    #     return False
