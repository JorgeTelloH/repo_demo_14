# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    essalud_tax = fields.Float(string='Essalud tasa')
    sctr_tax = fields.Float(string='SCTR tasa')
    uit_tax = fields.Float(string='UIT tasa')
    eps_tax = fields.Float(string='EPS %')

    essalud_rmv = fields.Float(string='Essalud RMV')
    sctr_rmv = fields.Float(string='SCTR RMV')
    uit_rmv = fields.Float(string='UIT RMV')

    rubro = fields.Char(string='Rubro')
    # campo necesario para el modelo de liquidacion CTS
    general_manager = fields.Char(string='Gerente General')
    product_id = fields.Many2one('product.product', string='Producto Recibo por Honorarios',
                                 domain="[('type', '=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', id)]")
    insurance_premium_cap = fields.Float(string='Tope de prima de seguros')
    eps_credit_amount = fields.Monetary(string='Importe credito EPS')

    company_type = fields.Selection(string='Tipo de compañia',
                                     selection=[('PRIVS', 'Sector privado'),
                                                ('PUBS', 'Sector publico'),
                                                ('OE', 'Otras entidades')
                                                ],
                                     help="Tipo de compañias")