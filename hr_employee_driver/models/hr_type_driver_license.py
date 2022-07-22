# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrTypeDriverLicense(models.Model):
    _name = 'hr.type.driver.license'
    _description = 'Tipos de Licencia de Conducir'

    name = fields.Char(string='Tipo de Licencia', required=True)
    active = fields.Boolean(string='Activo', default=True)
