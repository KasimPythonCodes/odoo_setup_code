# import dp

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp

class SaleQuotation(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.quotation'
    _description = 'Sale Quotations'

    @api.model
    def create(self, vals):
        if vals.get('q_seq', _('New')) == _('New'):
            vals['q_seq'] = self.env['ir.sequence'].next_by_code('hospital.sale.quotation.sequence') or '/'
        return super(SaleQuotation, self).create(vals)

    @api.multi
    def action_confirm_quotation(self):
        orderLine = self.env['sale.order.line']
        for q in self:
            sale_order = self.env['sale.order'].create({'partner_id': q.partner_id.id})
            for line in self.sale_quotation_line:
                order_line = orderLine.create({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'tax_id': line.tax_id,
                    # 'q_id': sale_order.id,
                    'validity_date': q.validity_date,
                    'payment_term_id': q.payment_term_id,
                    'order_id': sale_order.id,
                    'price_subtotal': line.price_subtotal

                })
            if q.state == 'draft':
                q.state = 'sent'
        form_view = self.env.ref('sale.action_orders').read()[0]
        form_view['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        form_view['context'] = {
            'default_partner_id': sale_order.partner_id.id,
            'default_order_line': [(4, order_line.id) for order_line in sale_order.order_line],
        }
        return form_view

    q_seq = fields.Char("Quotation Sequence")
    sale_quotation_line = fields.One2many('sale.quotation.line', 'q_id', string='Sale Quotation Lines', copy=True)


class SaleQuotationLine(models.Model):
    _name = 'sale.quotation.line'
    _description = 'Sale Quotations Line'

    q_id = fields.Many2one('sale.quotation', string='Sale Quotation Id', index=True, required=True, ondelete='cascade', copy=True)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    invoice_lines = fields.Many2many('account.invoice.line', 'sale_order_line_invoice_rel', 'order_line_id',
                                     'invoice_line_id', string='Invoice Lines', copy=False)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0, track_visibility="onchange")

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce',
                                digits=dp.get_precision('Product Price'), readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True,
                                          store=True)
    price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl',
                                           readonly=True, store=True)

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict', required=True)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True,
                                       default=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0, track_visibility="onchange")
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    product_image = fields.Binary('Product Image', related="product_id.image", store=False)

    qty_delivered_updateable = fields.Boolean(compute='_compute_qty_delivered_updateable', string='Can Edit Delivered',
                                              readonly=True, default=True)
    qty_delivered = fields.Float(string='Delivered', copy=False, digits=dp.get_precision('Product Unit of Measure'),
                                 default=0.0)
    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    qty_invoiced = fields.Float(
        compute='_get_invoice_qty', string='Invoiced', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))

    salesman_id = fields.Many2one(related='q_id.user_id', store=True, string='Salesperson', readonly=True)
    currency_id = fields.Many2one(related='q_id.currency_id', store=True, string='Currency', readonly=True)
    company_id = fields.Many2one(related='q_id.company_id', string='Company', store=True, readonly=True)
    order_partner_id = fields.Many2one(related='q_id.partner_id', store=True, string='Customer')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
                                         " They are not copied when duplicating a sales order.")

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='q_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer",
        oldname="delay")
    amt_to_invoice = fields.Monetary(string='Amount To Invoice', compute='_compute_invoice_amount', compute_sudo=True,
                                     store=True)
    amt_invoiced = fields.Monetary(string='Amount Invoiced', compute='_compute_invoice_amount', compute_sudo=True,
                                   store=True)

    layout_category_id = fields.Many2one('sale.layout_category', string='Section')
    layout_category_sequence = fields.Integer(string='Layout Sequence')

    def _compute_qty_delivered_updateable(self):
        for line in self:
            line.qty_delivered_updateable -= line.qty_delivered_updateable

    # @api.depends('q_id')
    # def _compute_q_id(self):
    #     for line in self:
    #         line.q_id = line.q_id.q_id.id if line.q_id and line.q_id.order.id else False

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and \
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.q_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.q_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('product_id', 'q_id.state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel'] or (
                    line.state == 'sale' and (line.qty_invoiced > 0 or line.qty_delivered > 0)):
                line.product_updatable = False
            else:
                line.product_updatable = True

    @api.depends('product_id.invoice_policy', 'q_id.state')
    def _compute_qty_delivered_updateable(self):
        for line in self:
            line.qty_delivered_updateable = (line.q_id.state == 'sale') and (
                        line.product_id.service_type == 'manual') and (line.product_id.expense_policy == 'no')

    @api.depends('state',
                 'price_reduce_taxinc',
                 'qty_delivered',
                 'invoice_lines',
                 'invoice_lines.price_total',
                 'invoice_lines.invoice_id',
                 'invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.refund_invoice_ids',
                 'invoice_lines.invoice_id.refund_invoice_ids.state',
                 'invoice_lines.invoice_id.refund_invoice_ids.amount_total')
    def _compute_invoice_amount(self):
        refund_lines_product = self.env['account.invoice.line']
        for line in self:
            # Invoice lines referenced by this line
            invoice_lines = line.invoice_lines.filtered(
                lambda l: l.invoice_id.state in ('open', 'paid') and l.invoice_id.type == 'out_invoice')
            refund_lines = line.invoice_lines.filtered(
                lambda l: l.invoice_id.state in ('open', 'paid') and l.invoice_id.type == 'out_refund')
            # Refund invoices linked to invoice_lines
            refund_invoices = invoice_lines.mapped('invoice_id.refund_invoice_ids').filtered(
                lambda inv: inv.state in ('open', 'paid'))
            refund_invoice_lines = (
                        refund_invoices.mapped('invoice_line_ids') + refund_lines - refund_lines_product).filtered(
                lambda l: l.product_id == line.product_id)
            if refund_invoice_lines:
                refund_lines_product |= refund_invoice_lines
            # If the currency of the invoice differs from the sale order, we need to convert the values
            if line.invoice_lines and line.invoice_lines[0].currency_id \
                    and line.invoice_lines[0].currency_id != line.currency_id:
                invoiced_amount_total = sum([inv_line.currency_id.with_context(
                    {'date': inv_line.invoice_id.date}).compute(inv_line.price_total, line.currency_id)
                                             for inv_line in invoice_lines])
                refund_amount_total = sum([inv_line.currency_id.with_context(
                    {'date': inv_line.invoice_id.date}).compute(inv_line.price_total, line.currency_id)
                                           for inv_line in refund_invoice_lines])
            else:
                invoiced_amount_total = sum(invoice_lines.mapped('price_total'))
                refund_amount_total = sum(refund_invoice_lines.mapped('price_total'))
            # Total of remaining amount to invoice on the sale ordered (and draft invoice included) to support upsell (when
            # delivered quantity is higher than ordered one). Draft invoice are ignored on purpose, the 'to invoice' should
            # come only from the SO lines.
            total_sale_line = line.price_total
            if line.product_id.invoice_policy == 'delivery':
                total_sale_line = line.price_reduce_taxinc * line.qty_delivered

            line.amt_invoiced = invoiced_amount_total - refund_amount_total
            line.amt_to_invoice = (total_sale_line - invoiced_amount_total) if line.state in ['sale', 'done'] else 0.0

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'q_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.q_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'out_invoice':
                        qty_invoiced += invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced -= invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_invoiced = qty_invoiced

    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.depends('price_total', 'product_uom_qty')
    def _get_price_reduce_tax(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_subtotal', 'product_uom_qty')
    def _get_price_reduce_notax(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.q_id.fiscal_position_id or line.q_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.q_id.partner_shipping_id) if fpos else taxes

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        return {}

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('q_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            with self.env.do_in_onchange():
                line = self.new(values)
                line.product_id_change()
                for field in onchange_fields:
                    if field not in values:
                        res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model
    def create(self, values):
        values.update(self._prepare_add_missing_fields(values))
        line = super(SaleQuotationLine, self).create(values)
        if line.q_id.state == 'sale':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.q_id.message_post(body=msg)
            # create an analytic account if at least an expense product
            if line.product_id.expense_policy not in [False, 'no'] and not self.q_id.analytic_account_id:
                self.q_id._create_analytic_account()
        return line

    def _update_line_quantity(self, values):
        orders = self.mapped('q_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.q_id == order)
            msg = "<b>The ordered quantity has been updated.</b><ul>"
            for line in order_lines:
                msg += "<li> %s:" % (line.product_id.display_name,)
                msg += "<br/>" + _("Ordered Quantity") + ": %s -> %s <br/>" % (
                    line.product_uom_qty, float(values['product_uom_qty']),)
                if line.product_id.type in ('consu', 'product'):
                    msg += _("Delivered Quantity") + ": %s <br/>" % (line.qty_delivered,)
                msg += _("Invoiced Quantity") + ": %s <br/>" % (line.qty_invoiced,)
            msg += "</ul>"
            order.message_post(body=msg)

    @api.multi
    def write(self, values):
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                              precision_digits=precision) != 0)._update_line_quantity(
                values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('q_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(SaleQuotationLine, self).write(values)
        return result

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        product = self.product_id.with_context(force_company=self.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.q_id.fiscal_position_id or self.q_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.q_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.q_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).
            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        invoice_lines = self.env['account.invoice.line']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                invoice_lines |= self.env['account.invoice.line'].create(vals)
        return invoice_lines

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a procurement rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        return {}

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.q_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.q_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.q_id.partner_id.id, date=self.q_id.date_order,
                               uom=self.product_uom.id)
        final_price, rule_id = self.q_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.q_id.partner_id)
        base_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                              self.product_uom_qty,
                                                                                              self.product_uom,
                                                                                              self.q_id.pricelist_id.id)
        if currency_id != self.q_id.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(base_price,
                                                                                                            self.q_id.pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.q_id.partner_id.lang,
            partner=self.q_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.q_id.date_order,
            pricelist=self.q_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.q_id.pricelist_id and self.q_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.q_id.pricelist_id and self.q_id.partner_id:
            product = self.product_id.with_context(
                lang=self.q_id.partner_id.lang,
                partner=self.q_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.q_id.date_order,
                pricelist=self.q_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

    @api.multi
    def name_get(self):
        result = []
        for so_line in self:
            name = '%s - %s' % (so_line.q_id.name, so_line.name.split('\n')[0] or so_line.product_id.name)
            if so_line.order_partner_id.ref:
                name = '%s (%s)' % (name, so_line.order_partner_id.ref)
            result.append((so_line.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = expression.AND([
                args or [],
                ['|', ('q_id.name', operator, name), ('name', operator, name)]
            ])
        return super(SaleQuotationLine, self).name_search(name, args, operator, limit)

    @api.multi
    def unlink(self):
        if self.filtered(lambda x: x.state in ('sale', 'done')):
            raise UserError(
                _('You can not remove a sales order line.\nDiscard changes and try setting the quantity to 0.'))
        return super(SaleQuotationLine, self).unlink()

    @api.multi
    def _get_delivered_qty(self):
        '''
        Intended to be overridden in sale_stock and sale_mrp
        :return: the quantity delivered
        :rtype: float
        '''
        return 0.0

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(
                        product, qty, self.q_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id)

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_protected_fields(self):
        return [
            'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty',
            'tax_id', 'analytic_tag_ids'
        ]

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.q_id.partner_id and self.q_id.pricelist_id and
                self.q_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.q_id.partner_id.lang,
            partner=self.q_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.q_id.date_order,
            pricelist=self.q_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.q_id.partner_id.id, date=self.q_id.date_order,
                               uom=self.product_uom.id)

        price, rule_id = self.q_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.q_id.partner_id)
        new_list_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                                  self.product_uom_qty,
                                                                                                  self.product_uom,
                                                                                                  self.q_id.pricelist_id.id)

        if new_list_price != 0:
            if self.q_id.pricelist_id.currency_id.id != currency_id:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(
                    new_list_price, self.q_id.pricelist_id.currency_id)
            discount = (new_list_price - price) / new_list_price * 100
            if discount > 0:
                self.discount = discount

    ###########################
    # Analytic Methods
    ###########################

    @api.multi
    def _analytic_compute_delivered_quantity_domain(self):
        """ Return the domain of the analytic lines to use to recompute the delivered quantity
            on SO lines. This method is a hook: since analytic line are used for timesheet,
            expense, ...  each use case should provide its part of the domain.
        """
        return ['&', ('so_line', 'in', self.ids), ('amount', '<=', 0.0)]

    @api.multi
    def _analytic_compute_delivered_quantity(self):
        """ Compute and write the delivered quantity of current SO lines, based on their related
            analytic lines.
        """
        # The delivered quantity of Sales Lines in 'manual' mode should not be erased
        self = self.filtered(lambda sol: sol.product_id.service_type != 'manual')

        # avoid recomputation if no SO lines concerned
        if not self:
            return False

        # group anaytic lines by product uom and so line
        domain = self._analytic_compute_delivered_quantity_domain()
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'unit_amount', 'product_uom_id'], ['product_uom_id', 'so_line'], lazy=False
        )
        # Force recompute for the "unlink last line" case: if remove the last AAL link to the SO, the read_group
        # will give no value for the qty of the SOL, so we need to reset it to 0.0
        value_to_write = {}
        if self._context.get('sale_analytic_force_recompute'):
            value_to_write = dict.fromkeys([sol for sol in self], 0.0)
        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        for item in data:
            if not item['product_uom_id']:
                continue
            so_line = self.browse(item['so_line'][0])
            value_to_write.setdefault(so_line, 0.0)
            uom = self.env['product.uom'].browse(item['product_uom_id'][0])
            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(item['unit_amount'], so_line.product_uom, rounding_method='HALF-UP')
            else:
                qty = item['unit_amount']
            value_to_write[so_line] += qty

        # write the delivered quantity
        for so_line, qty in value_to_write.items():
            so_line.write({'qty_delivered': qty})

        return True

    def _is_delivery(self):
        self.ensure_one()
        return False