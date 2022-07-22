# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    alert_contract = fields.Integer(string='Alerta Vencimiento de contrato (días)', default=30)
    notification_contract_expiration_ids = fields.Many2many('hr.employee', string='Notificar contratos próximos a expirar')
    notification_vac_expiration_ids = fields.Many2many('hr.employee', 'rel_notification_vac_expiration', string='Notificar vacaciones por disfrutar')

    is_af = fields.Boolean(string='Tiene Asignación Familiar?', default=True)
    percent_af = fields.Float(string='Porcentaje de Asignación Familiar', default=10)

    number_absences = fields.Integer(string='Ausencias injustificadas permitidas', default=10)
    vacation_days_allowed = fields.Integer(string='Días permitidos de vacaciones', default=30)

    days_medical_certificate = fields.Integer(string='Días de Descanso médico', default=20, 
        help='Días de descanso médico cubierto por la Compañía')

    porcet_gratification = fields.Float(string='Porcentaje de gratificación', default=100)
