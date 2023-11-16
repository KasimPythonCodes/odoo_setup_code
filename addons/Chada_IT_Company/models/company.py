from odoo import models,api,_
from odoo.exceptions import ValidationError
import re
class RegistrationCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Company Registration Record'
    _rec_name = 'name'


    @api.constrains('company_registry')
    def Check_Company_Res(self):
        regx = r"^[A-Z]{2}[0-9A-Z]{10}$"
        for rec in self:
            if rec.company_registry:
                if not rec.vat:
                    raise ValidationError(_("GSTIN Can't be Null for Registered companies"))
            elif rec.name in self.env['res.company'].search([]):
                raise ValidationError(_("Company name must be Unique"))
            elif rec.state_id.code != rec.vat[:2]:
                raise ValidationError(_("GSTIN first two number Doesn't Match"))
            elif not re.fullmatch(regx ,rec.vat):
                raise ValidationError(_("GSTIN number wrong formate"))



                # self.vat = rec.state_id.code
                # raise ValidationError(_("First Two Charactor is Invalid "))




    @api.onchange('state_id')
    def Check_GSTIN(self):
            if self.state_id:
                self.vat = self.state_id.code
            return False





