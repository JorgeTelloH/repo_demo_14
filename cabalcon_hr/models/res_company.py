# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    essalud_tax = fields.Float(string='EsSalud tasa')
    sctr_tax = fields.Float(string='SCTR tasa')
    uit_tax = fields.Float(string='UIT tasa')
    eps_tax = fields.Float(string='EPS %')

    essalud_rmv = fields.Float(string='Essalud RMV')
    sctr_rmv = fields.Float(string='SCTR RMV')
    uit_rmv = fields.Float(string='UIT RMV')

    rubro = fields.Char(string='Rubro')
    # campo necesario para el modelo de liquidacion CTS
    # general_manager = fields.Char(string='Gerente General')
    general_manager_id = fields.Many2one('res.partner', string='Gerente General', help="Gerente General de la Compañia")
    product_id = fields.Many2one('product.product', string='Producto Recibo por Honorarios',
                                 domain="[('type', '=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', id)]")
    insurance_premium_cap = fields.Float(string='Tope de prima de seguros')
    eps_credit_amount = fields.Monetary(string='Importe crédito EPS')
    ofic_norm_prev = fields.Float(string='Oficina de normalización previsional')

    sector = fields.Selection(string='Sector',
                              selection=[('PRIVS', 'Sector Privado'),
                                         ('PUBS', 'Sector Publico'),
                                         ('OE', 'Otras Entidades')],
                              help="Sector")

    company_type = fields.Selection(string='Tipo de compañia',
                                    selection=[('01', 'Empresa'),
                                               ('02', 'MIPYMES')],
                                    help="Tipo de Compañia",
                                    default='01')
    sigla = fields.Char(string='Sigla')
    account_type = fields.Selection(string='Tipo de cuenta de cargo',
                                    selection=[('C', 'Corriente'),
                                               ('M', 'Maestra')],
                                    default='C')
    account = fields.Char(string='Cuenta de cargo')
