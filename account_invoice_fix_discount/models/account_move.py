# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    discount_line_total = fields.Monetary(compute="_compute_discount_total", string="Dscto Total Linea", currency_field="currency_id", store=True)

    #============= INI CALCULAR DSCTO LINEA TOTAL =============
    @api.depends("invoice_line_ids.discount_line_total")
    def _compute_discount_total(self):
        invoices_discount = self.filtered(lambda a: a.is_invoice())
        # Factura con descuento
        for invoice in invoices_discount:
            total_line_discount = sum(invoice.invoice_line_ids.mapped("discount_line_total"))
            invoice.update(
                {
                    "discount_line_total": total_line_discount,
                }
            )
        #Se excluyen los movimientos de cuenta que no sean facturas
        (self - invoices_discount).update(
            {
                "discount_line_total": 0.0,
            }
        )
    #============= FIN CALCULAR DSCTO LINEA TOTAL =============

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Float( string="Monto Dscto", digits="Discount", default=0.0, help="Aplicar monto de Dscto sobre el Precio")
    discount_line_total = fields.Monetary(compute="_compute_discount_amount", string="Dscto Total Linea", store=True)

    #============= INI CALCULAR DSCTO TOTAL LINEA =============
    @api.depends("discount", "price_total")
    def _compute_discount_amount(self):
        invoice_lines_discount = self.filtered( lambda a: (a.discount) and not a.exclude_from_invoice_tab)

        # Lineas de Factura con descuento
        for line in invoice_lines_discount:
            taxes = line.tax_ids.compute_all(
                line.price_unit,
                line.move_id.currency_id,
                line.quantity,
                product=line.product_id,
                partner=line.partner_id,
            )
            total_line_discount = taxes['total_excluded'] - line.price_subtotal #taxes["total_included"]
            line.update(
                {
                    "discount_line_total": total_line_discount,
                }
            )
        #Líneas sin descuento y las que no son líneas de factura están excluidos
        (self - invoice_lines_discount).update(
            {
                "discount_line_total": 0.0,
            }
        )
    #============= FIN CALCULAR DSCTO TOTAL LINEA =============
