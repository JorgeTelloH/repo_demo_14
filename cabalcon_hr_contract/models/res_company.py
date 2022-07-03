# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    alert_contract = fields.Integer(string='Alerta de vencimiento de contrato (días)', default=30)
    notification_contract_expiration_ids = fields.Many2many('hr.employee', string='Notificar contratos próximos a expirar')
