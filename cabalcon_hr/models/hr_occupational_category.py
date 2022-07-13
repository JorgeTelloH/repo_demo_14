# -*- encoding: utf-8 -*-
from odoo import fields, models, api


class OccupationalCategory(models.Model):
    _name = 'hr.occupational.category'
    _description = 'Categoría Ocupacional del trabajador'
    _sql_constraints = [
        ('code', 'unique (code)', 'El código de la categoría ocupacional debe ser único!')
    ]

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    private_sector = fields.Boolean(string='Sector Privado',required=True)
    public_sector = fields.Boolean(string='Sector Publico',required=True)
    other_entities = fields.Boolean(string='Otras Entidades',required=True)
    active = fields.Boolean(string='Activo',  default=True)