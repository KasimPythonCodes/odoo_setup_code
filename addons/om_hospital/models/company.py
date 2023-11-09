import re
from odoo import models, fields, api, exceptions


class CompanyRegis(models.Model):
    _inherit = 'res.company'

    # @api.constrains('vat')
    # def _validate_gst_number(self):
    #     for record in self:
    #         vat = record.vat
    #         if vat:
    #             vat = vat.replace(' ', '')
    #             if not re.match(r'^[0-9]{2}[A-Z]{5}$', vat):
    #                 raise exceptions.ValidationError('Invalid GST number: %s' % vat)

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.vat = self.state_id.l10n_in_tin
        else:
            self.vat = False

    @api.constrains('company_registry', 'vat')
    def _set_company_regis(self):
        for record in self:
            if record.vat:
                # Validate GST number using a regular expression
                gst_regex = r'^[0-9]{2}[A-Z]{5}$'
                if not re.match(gst_regex, record.vat):
                    raise exceptions.ValidationError("Invalid GST number format.")
            if record.company_registry:
                # if record.name != record.company_registry:
                #     raise exceptions.ValidationError(
                #         "Name and Company Registry must be the same when the Company Registry is filled.")
                if not record.vat or not record.vat.strip():
                    raise exceptions.ValidationError("GST field is mandatory when the Company Registry is filled.")

    validated_fields = fields.Char(compute='_set_company_regis')


class VendorRegis(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat')
    def _validate_vendor_gst_number(self):
        for record in self:
            vat = record.vat
            if vat:
                vat = vat.replace(' ', '')
                if not re.match(r'^[0-9]{2}[A-Z]{5}$', vat):
                    raise exceptions.ValidationError('Invalid GST number: %s' % vat)


class SaleOrderLineRegis(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.company_id.vat', 'product_id.taxes_id')
    def _purchase_compute_name(self):
        for line in self:
            if line.order_id.company_id.vat:
                line.tax_id = line.product_id.taxes_id
            else:
                line.tax_id = False