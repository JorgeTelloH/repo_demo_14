# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    travel_allowance = fields.Monetary(string="Movilidad", help="Subsidio de transporte")
    da = fields.Monetary(string="Asignación Familiar", help="Asignación Familiar")
    meal_allowance = fields.Monetary(string="Subsidio de alimentación", help="Subsidio de alimentación")
    medical_allowance = fields.Monetary(string="Asignación médica", help="Asignación médica")
    produce_5ta_category = fields.Monetary(string='Renta 5ta Categoría')
    judicial_retention = fields.Monetary(string='Retención judicial')
    basket = fields.Monetary(string='Aguinaldo')

