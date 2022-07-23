# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    essalud_tax = fields.Float(string='EsSalud Tasa')
    sctr_tax = fields.Float(string='SCTR Tasa')
    uit_tax = fields.Float(string='UIT tasa')
    eps_tax = fields.Float(string='EPS %')

    essalud_rmv = fields.Float(string='Essalud RMV')
    sctr_rmv = fields.Float(string='SCTR RMV')
    uit_rmv = fields.Float(string='UIT RMV')

    rubro = fields.Char(string='Rubro de la Compañia')
    # campo necesario para el modelo de liquidacion CTS
    general_manager_id = fields.Many2one('res.partner', string='Gerente General', help="Gerente General de la Compañia")
    product_id = fields.Many2one('product.product', string='Producto Recibo por Honorarios',
                                 domain="[('type', '=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', id)]")
    insurance_premium_cap = fields.Float(string='Tope de prima de Seguros')
    eps_credit_amount = fields.Monetary(string='Importe crédito EPS')
    ofic_norm_prev = fields.Float(string='Oficina de normalización previsional')

    sigla = fields.Char(string='Sigla')
    #Adelantos
    account_type = fields.Selection(string='Tipo de Cuenta Cargo',
                                    selection=[('C', 'Corriente'),
                                               ('M', 'Maestra')],
                                    default='C')
    account = fields.Char(string='Cuenta Cargo')
