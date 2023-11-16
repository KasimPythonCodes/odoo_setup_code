from odoo import api, models, _
from odoo.exceptions import ValidationError
import re


class PartnerVanderCompany(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner Registration Record'
    _rec_name = 'name'

    @api.constrains('vat')
    def Check_Partner_Res(self):
        regx = r"^[A-Z]{2}[0-9A-Z]{10}$"
        for rec in self:
            if not rec.vat:
                raise ValidationError(_("GSTIN Can't be Null for Registered companies"))
            elif rec.vat:
                if rec.name in self.env['res.partner'].search([]):
                    raise ValidationError(_("Company name must be Unique"))
            elif rec.state_id.code != rec.vat[:2]:
                raise ValidationError(_("GSTIN or TIN number first two Doesn't Match"))
            elif not re.match(regx,rec.vat):
                raise ValidationError(_("GSTIN Doesn't Match"))
        query = """select name from res_partner"""
        self.env.cr.execute(query)
        pr = self.env.cr.fetchall()
        lst = list(pr)
        dset = set()
        for i in lst:
            if i in dset:
                raise ValidationError(_('Company name is Already Exists'))
            dset.add(i)
        return False


    @api.onchange('state_id')
    def Check_GSTIN_res(self):
        if self.state_id:
            self.vat = self.state_id.code
        return False

