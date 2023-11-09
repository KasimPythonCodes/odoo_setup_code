from odoo import api, models, fields


class QuotationAmendment(models.Model):
    _name = 'quotation.amendment'
    _description = 'Quotation Amendments'

    amend_id = fields.Many2one('sale.quotation', string='Quotation', required=True, ondelete='cascade')
    amend_no = fields.Integer(string='Amendment Number', default=0)

    @api.model
    def create(self, vals):
        if vals.get('amend_no', 'New') == 'New':
            vals['amend_no'] = self._get_next_amendment_number()
        return super(QuotationAmendment, self).create(vals)

    def _get_next_amendment_number(self):
        amendment = self.search([], order='amend_no desc', limit=1)
        print('goo....', amendment)
        if amendment:
            print('inside', amendment.amend_no)
            return amendment.amend_no + 1
        return 1


class QuotationLineAmendment(models.Model):
    _name = 'quotation.line.amendment'
    _description = 'Quotation Line Amendment'

    line_id = fields.Many2one('sale.quotation.line', string='Quotation Line', required=True, ondelete='cascade')
    amendment_no = fields.Integer(string='Amendment Number', compute='_compute_amendment_no', store=True)

    @api.depends('line_id')
    def _compute_amendment_no(self):

        for amendment in self:
            print('quotation line', amendment.line_id.amendment_ids)
            amendment.amendment_no = len(amendment.line_id.amendment_ids)


class SaleQuotationLine(models.Model):
    _inherit = 'sale.quotation.line'

    amendment_ids = fields.One2many('quotation.line.amendment', 'line_id', string='Amendments')


class SaleQuotation(models.Model):
    _inherit = 'sale.quotation'

    amendment_ids = fields.One2many('quotation.amendment', 'amend_id', string='Amendments')
    amendment_number = fields.Integer(string='Amendment Number', store=True, compute='_compute_amendment_number')
    amendment_done = fields.Boolean(string='Amendment Done', default=False, store=False)

    @api.depends('amendment_ids')
    def _compute_amendment_number(self):
        for quotation in self:
            quotation.amendment_number = quotation.amendment_number + 1

    def get_quotation_enable_state(self):
        settings = self.env['res.config.settings'].sudo().create({})
        values = settings.get_values()
        quotation_amendment_state = values.get('quotation_amendment', False)
        return quotation_amendment_state

    @api.multi
    def write(self, vals):
        res = super(SaleQuotation, self).write(vals)
        # if vals.keys():
        if any(field_name.startswith('sale_quotation_line') for field_name in vals.keys()):
            # is_quotation_amendment_enabled = self.get_quotation_enable_state()
            # if is_quotation_amendment_enabled:
            for quotation in self:
                if quotation.state == 'sent' and not quotation.amendment_done:
                    quotation.amendment_number += 1
                    quotation.amendment_done = True
        return res

    @api.multi
    def action_save(self):
        res = super(SaleQuotation, self).action_save()
        if self.amendment_done:
            self.amendment_done = False
        return res