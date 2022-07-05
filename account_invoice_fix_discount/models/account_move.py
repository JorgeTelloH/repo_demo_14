# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_total = fields.Monetary(compute="_compute_discount_total", string="Dscto Total", currency_field="currency_id", store=True)
    price_total_no_discount = fields.Monetary(compute="_compute_discount_total", string="Total sin Dscto", currency_field="currency_id", store=True)


    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        vals = {}
        for line in self.invoice_line_ids.filtered("discount_fixed"):
            vals[line] = {"price_unit": line.price_unit}
            price_unit = line.price_unit - line.discount_fixed
            line.update({"price_unit": price_unit})
        res = super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
        for line in vals.keys():
            line.update(vals[line])
        return res

    #============= INI CALCULAR DSCTO TOTAL =============
    @api.depends("invoice_line_ids.discount_total", "invoice_line_ids.price_total_no_discount")
    def _compute_discount_total(self):
        invoices_discount = self.filtered(lambda a: a.is_invoice())

        # Factura con descuento
        for invoice in invoices_discount:
            discount_total = sum(invoice.invoice_line_ids.mapped("discount_total"))
            price_total_no_discount = sum( invoice.invoice_line_ids.mapped("price_total_no_discount"))
            invoice.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

        #Se excluyen los movimientos de cuenta que no sean facturas
        (self - invoices_discount).update(
            {
                "discount_total": 0.0,
                "price_total_no_discount": 0.0,
            }
        )
    #============= FIN CALCULAR DSCTO TOTAL =============

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Float( string="Monto Dscto", digits="Product Price", default=0.00, help="Aplicar monto de Dscto")
    discount_total = fields.Monetary(compute="_compute_discount_amount", string="Dscto Total", store=True)
    price_total_no_discount = fields.Monetary(compute="_compute_discount_amount", string="Total sin Dscto", store=True)

    @api.onchange("discount")
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains("discount", "discount_fixed")
    def _check_only_one_discount(self):
        for rec in self:
            for line in rec:
                if line.discount and line.discount_fixed:
                    raise ValidationError( _("Solo puedes Aplicar un Tipo de Descuento por línea.") )

    @api.onchange("quantity", "discount", "price_unit", "tax_ids", "discount_fixed")
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.model
    def _get_price_total_and_subtotal_model(
        self,
        price_unit,
        quantity,
        discount,
        currency,
        product,
        partner,
        taxes,
        move_type,
    ):
        if self.discount_fixed != 0:
            discount = self.discount_fixed #((self.discount_fixed) / price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )

    @api.model
    def _get_fields_onchange_balance_model(
        self,
        quantity,
        discount,
        amount_currency,
        move_type,
        currency,
        taxes,
        price_subtotal,
        force_computation=False,
    ):
        if self.discount_fixed != 0:
            discount = ((self.discount_fixed) / self.price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_fields_onchange_balance_model(
            quantity,
            discount,
            amount_currency,
            move_type,
            currency,
            taxes,
            price_subtotal,
            force_computation=force_computation,
        )

    @api.model_create_multi
    def create(self, vals_list):
        prev_discount = []
        for vals in vals_list:
            if vals.get("discount_fixed"):
                prev_discount.append(
                    {"discount_fixed": vals.get("discount_fixed"), "discount": 0.00}
                )
                fixed_discount = (
                    vals.get("discount_fixed") / vals.get("price_unit")
                ) * 100
                vals.update({"discount": fixed_discount, "discount_fixed": 0.00})
            elif vals.get("discount"):
                prev_discount.append({"discount": vals.get("discount")})
        res = super(AccountMoveLine, self).create(vals_list)
        i = 0
        for rec in res:
            if rec.discount and prev_discount:
                rec.write(prev_discount[i])
                i += 1
        return res

    #============= INI CALCULAR DSCTO TOTAL =============
    @api.depends("discount", "discount_fixed", "price_total")
    def _compute_discount_amount(self):
        invoice_lines_discount = self.filtered( lambda a: (a.discount or a.discount_fixed) and not a.exclude_from_invoice_tab)

        # Lineas de Factura con descuento
        for line in invoice_lines_discount:
            taxes = line.tax_ids.compute_all(
                line.price_unit,
                line.move_id.currency_id,
                line.quantity,
                product=line.product_id,
                partner=line.partner_id,
            )
            price_total_no_discount = taxes['total_excluded']  #taxes["total_included"]
            discount_total = price_total_no_discount - line.price_total
            line.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

        #Líneas sin descuento y las que no son líneas de factura están excluidos
        (self - invoice_lines_discount).update(
            {
                "discount_total": 0.0,
                "price_total_no_discount": 0.0,
            }
        )

    #============= FIN CALCULAR DSCTO TOTAL =============