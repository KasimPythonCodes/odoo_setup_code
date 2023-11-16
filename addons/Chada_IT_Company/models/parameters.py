from odoo import fields, api, _, models
from odoo.exceptions import ValidationError


class UserParameter(models.Model):
    _name = 'user.parameter'
    _description = 'Parameter Record'
    _rec_name = 'parameter_name'

    @api.constrains('parameter_name')
    def Check_Null_Value(self):
        # query="""select parameter_name from user_parameter""".format(f"{self.parameter_name}")
        query="""select parameter_name from user_parameter"""
        self.env.cr.execute(query)
        pr=self.env.cr.fetchall()
        lst=list(pr)
        dset=set()
        for i in lst:
            if i in dset:
                raise ValidationError(_('Parameter name is Already Exists'))
            dset.add(i)
        return False

        # print(self.parameter_name!=i,"HHHHHHH")
        # if self.env['user.parameter'].search([('id', '=', [self.ids])]):
        #     raise ValidationError(_('Parameter name is Already Exists'))
        # elif self.env['user.parameter'].search([('parameter_name', 'not in', [self.parameter_name])]):
        #         # raise ValidationError(_('Parameter name is Already Exists'))
        #         pass
    # for lst in lst:
        #     if self.parameter_name not in lst or self.parameter_name  in lst:
        #         raise ValidationError(_('Parameter name is Already Exists'))
        #     return False

    parameter_name = fields.Selection([
        ('technical parameter', 'Technical parameter'),
        ('other parameter', 'Other Parameter'),
        ('requirement area ', 'Requirement Area '),
    ],
        string='Parameter', required=True)
    parameter_value = fields.Integer(string='Value')

    @api.multi
    def Messages_Warning(self):
        return {
            'warning': {
                'title': 'Warning!',
                'message': 'The warning text'}
        }

