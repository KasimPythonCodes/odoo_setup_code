from odoo import models, fields, api, _

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.onchange('is_products')
    def _onchange_select_all_products(self):
        if self.is_products:
            self.purchase_out_lines = self.order_line.filtered(lambda line: line.product_id)

    # @api.model
    # def create(self, vals):
    #     if vals.get('job_order_seq', _('New')) == _('New'):
    #         vals['job_order_seq'] = self.env['ir.sequence'].next_by_code('hospital.job.order.sequence') or _('New')
    #     result = super(JobOrder, self).create(vals)
    #     return result

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s' % field.job_order_seq))
        return res

    job_order_seq = fields.Char(string='Job Order Id', required=True, copy=False,
                                readonly=True, index=True, default=lambda self: _('New'))
    order_type = fields.Selection([
        ('J', 'Job Order'),
        ('P', 'Purchase Order')
    ], default='J', string="Order Type")
    is_products = fields.Boolean(string="Some Item to be received")
    purchase_out_lines = fields.One2many('purchase.order.line', 'purchase_out_id', string="Purchase Out Lines")
    have_invoice = fields.Boolean(string="Have Invoice")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_number = fields.Text(string="Invoice Number")


@api.model
def create(self, vals):
    if vals.get('name', 'New') == 'New':
        if vals.get('job_order_seq') == True:
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.job.order.sequence') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
    return super(PurchaseOrder, self).create(vals)


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        if 'order_id' not in vals:
            vals['order_id'] = self._context.get('order_id')
        return super(PurchaseOrderLineInherit, self).create(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        return {'domain': {'product_id': [('type', 'in', ('product', 'service'))]}}

    purchase_out_id = fields.Many2one('purchase.order', string="Purchase Out")
    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')