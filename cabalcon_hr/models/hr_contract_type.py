# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Tipo de Contrato'

    name = fields.Char(string="Tipo de Contrato", required=True)
    active = fields.Boolean(string='Activo', default=True)
