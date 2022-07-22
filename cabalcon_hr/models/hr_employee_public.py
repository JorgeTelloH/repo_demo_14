# -*- coding: utf-8 -*-
from odoo import models, fields


class HREmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
        
    code = fields.Char(string='Código', readonly=True)
