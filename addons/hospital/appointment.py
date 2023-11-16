from odoo import models, fields, api, _


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    _rec_name = 'patient_id'

    def _get_default_note(self):
        return

    # name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
    #                    index=True, default=lambda self: _('new'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_age = fields.Integer(string='Age', related='patient_id.patient_age')
    notes = fields.Text(string="Registration Note",)
    doctor_notes = fields.Text(string="Doctor Note",)
    pharmacy_notes = fields.Text(string="Pharmacy Note",)
    appointment_lines = fields.One2many('hospital.appointment.lines', 'appointment_id', string='Appointment Lines')
    appointment_date = fields.Date(string="Date",)
    appointment_total_amount = fields.Integer(string="Total Amount",)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, default='draft')
    appointment_seq = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('new'))

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.model
    def create(self, vals):
        if vals.get('appointment_seq', _('New')) == _('New'):
            vals['appointment_seq'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')
        result = super(HospitalAppointment, self).create(vals)
        return result

class HospitalAppointmentLines(models.Model):
        _name = 'hospital.appointment.lines'
        _description = 'Appointment Lines'

        product_id = fields.Many2one('hospital.appointment', string='product')
        product_qty = fields.Integer(string="Quantity")
        appointment_id = fields.Many2one('hospital.appointment', string='Appointment ID')

        # display_type = fields.Selection([
        #     ('line_section', "Section"),
        #     ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


















# from odoo import models , fields ,api,_
# class HospitalAppointment(models.Model):
#     _name = "hospital.appointment"
#     _description = 'Appointment'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'id desc'
#
#     def set_default_notes(self):
#         return "please subscribe my youtube channel"
#
#     @api.model
#     def create(self, vals):
#         if vals.get('name', _('New') == _('New')):
#             vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
#         res = super(HospitalAppointment, self).create(vals)
#         return res
#
#     name = fields.Char(string="Appointment Id",
#                        required=True, copy=False, readonly=True, index=True,
#                        default=lambda self: _('New'))
#     patient_id = fields.Many2one('hospital.patient' , string='Patient',readonly=True)
#     patient_age = fields.Integer('age',related='patient_id.patient_age')
#     notes = fields.Text(string='Registration Note' ,default=set_default_notes)
#     appointment_date = fields.Date(string='Date',required=True)
#     appointment_lines= fields.One2many('hospital.appointment.lines','appointment_id' ,string='Appointment lines')
#     # state = fields.Selection([
#     #         ('draft', 'draft'),
#     #         ('confirm', 'confirm'),
#     #         ('done', 'done'),
#     #         ('cancel', 'cancelled'),
#     #     ] , string='status',readonly=True,default='Draft')
#
#
# class HospitalAppointmentlines(models.Model):
#     _name = "hospital.appointment.lines"
#     _description = 'Appointment Lines'
#
#     product_id = fields.Many2one('product.product' , string='Medicine')
#     product_qty = fields.Integer(string='Quality')
#     appointment_id = fields.Many2one('hospital.appointment' , string='Appointment ID')
