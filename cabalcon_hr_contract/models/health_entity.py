# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class HrEmployeeHealthEntity(models.Model):
    _name = 'hr.employee.health.entity'
    _description = 'Empresas Aseguradoras de Salud'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(code)', 'El Código de Empresa debe ser único!'),
    ]

    name = fields.Char('Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    active = fields.Boolean(string='Activo', default=True)
