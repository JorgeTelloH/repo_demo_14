# -*- coding: utf-8 -*-
from odoo import models, fields, api

from datetime import datetime

class HrTypeDriverLicense(models.Model):
    _name = 'hr.type.driver.license'
    _description = 'Tipos de Licencia de Conducir'

    name = fields.Char(string='Tipo de Licencia', required=True)
    active = fields.Boolean(string='Activo', default=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    driver = fields.Boolean(string='Es Conductor?', help='Activar solo si el Empleado es conductor')
    type_employee = fields.Selection([("planilla", "Planilla"), ("tercero", "Tercero")], string='Tipo Empleado (No Usar)', default='planilla')
    partner_id = fields.Many2one('res.partner', string='Proveedor (No Usar)', index=True)
    driver_license = fields.Char(string='Nro Brevete')
    license_type = fields.Char(string='Tipo Licencia (No Usar)')
    license_type_id = fields.Many2one('hr.type.driver.license', string="Tipo de Brevete")
    license_expiration = fields.Date(string='Caducidad de Brevete', help='Fecha de Caducidad de Brevete')
    days_to_expire = fields.Integer(compute='_compute_days_to_expire', string='Caducidad de Brevete')
    #SOAT
    soat_nbr = fields.Char(string='Nro SOAT')
    soat_start_date = fields.Date(string='Fecha Desde')
    soat_finish_date = fields.Date(string='Fecha Hasta', help='Fecha de Caducidad de SOAT')
    soat_days_to_expire = fields.Integer(compute='_compute_soat_days_to_expire', string='Caducidad de SOAT')


    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        for rec in self:
            now = fields.Date().today()
            date_expire = rec.license_expiration or fields.Date().today()
            delta = date_expire - now
            if delta.days >= -1:
                if rec.license_expiration:
                    rec.days_to_expire = delta.days + 1
                else:
                    rec.days_to_expire = 0
            else:
                rec.days_to_expire = 0

    @api.depends('soat_finish_date')
    def _compute_soat_days_to_expire(self):
        for rec in self:
            now = fields.Date().today()
            soat_date_expire = rec.soat_finish_date or fields.Date().today()
            delta = soat_date_expire - now
            if delta.days >= -1:
                rec.soat_days_to_expire = delta.days + 1
            else:
                rec.soat_days_to_expire = 0
