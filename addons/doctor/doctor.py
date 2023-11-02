from odoo import models,fields,_,api

class TestDoctor(models.Model):
    _name = "test.doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Doctor Record'
    _rec_name = 'doctor_name'

    doctor_name = fields.Char(string="name", required=True)
    doctor_age = fields.Integer('age')
    doctor_image = fields.Binary(string='image')
    doctor_department = fields.Char(string='Department')
    doctor_gender = fields.Char(selection=['Male','Female'])
    sequence=fields.Char(string='Doctor Id' ,required=True , copy=False,readonly=True ,index=True ,default=lambda self:_('New'))

    @api.model
    def create(self, vals):
        if vals.get('sequence' ,_('New')==_('New')):
            vals['sequence']=self.env['ir.sequence'].next_by_code('test.doctor.sequence') or _('New')
        res = super(TestDoctor , self).create(vals)
        return res

