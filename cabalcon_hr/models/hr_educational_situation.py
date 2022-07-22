# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HrEducacionalSituation(models.Model):
    _name = 'hr.educational.situation'
    _description = 'Situación Educacional'

    _sql_constraints = [
        ('code', 'unique (code)', 'El código de la situación educacional debe ser único!')]

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)
    desc = fields.Char(string='Descripción', required=True)
    active = fields.Boolean(string='Activo',  default=True)
