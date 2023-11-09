from odoo import api, fields, models
from num2words import num2words


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    total_quantity = fields.Float(compute='_compute_total_quantity', string='Total Quantity')
    total_amount_in_words = fields.Char(string='Total Amount in Words', compute="_convert_total_amount_to_words")
    taxed_amount_in_words = fields.Char(string='Taxed Amount in Words', compute="_convert_taxed_amount_to_words")
    invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines')

    @api.depends('invoice_line_ids.quantity')
    def _compute_total_quantity(self):
        for invoice in self:
            invoice.total_quantity = int(sum(invoice.invoice_line_ids.mapped('quantity')))

    @api.depends('amount_total')
    def _convert_total_amount_to_words(self):
        words = num2words(self.amount_total, lang='en_IN')
        self.total_amount_in_words = words

    @api.depends('amount_tax')
    def _convert_taxed_amount_to_words(self):
        words = num2words(self.amount_tax, lang='en_IN')
        self.taxed_amount_in_words = words


class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    tax_amount_each = fields.Float(string='Tax Amount', compute='_compute_tax_amount_each')

    @api.depends('price_unit', 'invoice_line_tax_ids.amount')
    def _compute_tax_amount_each(self):
        for line in self:
            for tax in line.invoice_line_tax_ids:
                tax_amount = (line.price_unit * tax.amount) / 100
                line.tax_amount_each = tax_amount