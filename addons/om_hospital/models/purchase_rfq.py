from odoo import models, fields, api, _


from datetime import date


class PurchaseRFQ(models.Model):
    _name = 'purchase.rfq'
    _inherit = 'purchase.order'
    _description = 'Requests for Quotation'

    @api.model
    def create(self, vals):
        if vals.get('rfq_sequence', _('New')) == _('New'):
            vals['rfq_sequence'] = self.env['ir.sequence'].next_by_code('purchase.rfq.sequence') or '/'
        return super(PurchaseRFQ, self).create(vals)

    @api.multi
    def action_confirm_order(self):
        orderLine = self.env['purchase.order.line']
        for rfq in self:
            purchase_order = self.env['purchase.order'].create({'partner_id': rfq.partner_id.id})
            for line in self.quotation_line:
                order_line = orderLine.create({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'date_planned': line.date_planned,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'order_id': purchase_order.id,
                })

        form_view = self.env.ref('purchase.purchase_order_action_generic').read()[0]
        form_view['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        form_view['context'] = {
                                'default_partner_id': purchase_order.partner_id.id,
                                'default_order_line': [(4, order_line.id) for order_line in purchase_order.order_line],
                            }
        return form_view

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s' % (field.rfq_sequence)))
        return res

    @api.onchange('sel_quotation')
    def onchange_quotation_id(self):
        if self.sel_quotation:
            self.quotation_line = [(5, 0, 0)]
            self.quotation_line = [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                # 'order_id': line.rfq_id.id
            }) for line in self.sel_quotation.order_line]
            print('order_line:', self.order_line)

    rfq_sequence = fields.Char(string="RFQ Sequence")
    state = fields.Selection(selection_add=[('q_recd', 'RFQ Received'), ('awarded', 'Awarded'), ('un_awarded', 'Un Awarded')])
    quotation_line = fields.One2many('purchase.rfq.line', 'rfq_id',
                                     string='Quotation Lines',
                                     copy=True
                                     )
    sel_quotation = fields.Many2one('sale.order', 'Reference RFQ', copy=True)

class PurchaseRFQLine(models.Model):
    _inherit = 'purchase.order.line'
    _name = 'purchase.rfq.line'
    _description = 'Request for Quotation Line'

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ line id', index=True, required=True, ondelete='cascade', copy=True)
    order_id = fields.Many2one('purchase.order', compute='_compute_order_id')
    req_qty = fields.Integer('Requested Quantity')
    ord_qty = fields.Integer('Ordered Quantity')
    tot_qty = fields.Integer('Total Quantity', compute='_compute_total_qty')

    def _compute_total_qty(self):
        for line in self:
            line.tot_qty = line.req_qty + line.ord_qty

    @api.depends('rfq_id')
    def _compute_order_id(self):
        for line in self:
            if line.rfq_id and line.rfq_id.order_line.order_id:
                line.order_id = line.rfq_id.order_line.order_id
            else:
                line.order_id = False

    def _compute_qty_received(self):
        for line in self:
            line.qty_received_total = line.qty_received

    @api.onchange('order_id')
    def _onchange_order_id(self):
        if self.order_id:
            self.rfq_id = self.order_id.rfq_id