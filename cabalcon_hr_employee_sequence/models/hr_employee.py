# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Employee(models.Model):
    _inherit = "hr.employee"
    _sql_constraints = [('employee_code_unique', 'unique(company_id, code)', 'El código del Empleado debe ser único')]

    code = fields.Char(string='Código de Empleado', copy=False)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('hr.employee.code') or '/'
        res = super(Employee, self).create(vals)
        return res
