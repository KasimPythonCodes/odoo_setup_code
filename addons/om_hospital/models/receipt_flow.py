from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    have_invoice = fields.Boolean(string='Have Invoice')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_no = fields.Integer(string='Invoice Number')

    def _action_done(self):
        if not self.have_invoice:
            for move in self.move_lines.filtered(lambda m: m.state in ['draft', 'waiting', 'confirmed']):
                move.quantity_done = 0.0
            res = super(StockPickingInherit, self)._action_done()
            return res
        else:
            return super(StockPickingInherit, self)._action_done()

    def button_validate(self):
        if not self.have_invoice:
            self.ensure_one()
            for move in self.move_lines.filtered(lambda m: m.state in ['draft', 'waiting', 'confirmed']):
                move._action_cancel()
            self.action_done()
        else:
            res = super(StockPickingInherit, self).button_validate()
            return res

    # @api.model
    # def create(self, vals_list):
    #     res = super(StockPickingInherit, self).create(vals_list)
    #     # print("yes working")
    #     # do the custom coding here
    #     return res

    # @api.depends('have_invoice')
    # def button_validate(self):
    #     for picking in self:
    #         if picking.have_invoice:
    #             for move in picking.move_lines:
    #                 move.update({
    #                     'name': 'Stock Move',
    #                     'location_id': move.partner_id.property_stock_supplier.id,
    #                     'location_dest_id': move.location_dest_id.id,
    #                     'product_id': move.product_id.id,
    #                     'product_uom_qty': move.product_uom_qty
    #                 })
    #     return super(ReceiptFlow, self).button_validate()