# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResAfp(models.Model):
    _name = 'res.afp'
    _description = 'Administradoras de Fondos de Pensiones'

    _sql_constraints = [ ('code', 'unique (code)', 'El código de la AFP debe ser único!') ]

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)
    seat = fields.Float(string='Fondo')
    commission_flow = fields.Float(string='Comisión Flujo')
    commission_mixed = fields.Float(string='Comisión Mixta')
    commission_mixed_year = fields.Float(string='Comisión Mixta Anual')
    insurance = fields.Float(string='Seguro')
    rma = fields.Float(string='Remuneración maxima asegurable')
