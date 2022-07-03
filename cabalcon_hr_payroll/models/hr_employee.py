# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Campos que se utilizan en la liquidacion
    liquidation_date_init = fields.Date(string='Fecha de Inicio de Computo')
    average_gratification = fields.Float(string='Promedio Gratificación')
    overtime_average = fields.Float(string='Horas Extras (Promedio)')
    cut_vacations = fields.Float(string='Vacaciones turnca')
    cut_vacations_m2 = fields.Float(string='Periodo 2, Vacaciones turnca (meses)')
    cut_vacations_d2 = fields.Float(string='Periodo 2, Vacaciones turnca (días)')
    afp = fields.Float(string='AFP')
    gratification_description = fields.Char(string='Gratificación')
    cut_gratification = fields.Integer(string='Gratificación (meses)')
    bonus = fields.Float(string='Bonificacion Extraordinaria - 9%')
    cts_period = fields.Integer(string='CTS')
    vacations_trunc = fields.Float(string='Vacaciones trunca')
    gratification = fields.Float(string='Gratificación')

    def compute_difference_in_months(self, date_init, date_end):
        months = 0
        if date_init and date_end:
            months = relativedelta(date_end, date_init).months
        return months

    def get_amount_to_text(self, value):
        currency = self.company_id.currency_id
        return currency.amount_to_text(value)

    def print_liquidation(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Liquidación por tiempo de servicios',
            'res_model': 'hr.liquidation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id,
                        'liquidation_date': self.liquidation_date_init,
                        'average_gratification': self.average_gratification,
                        'cut_vacations': self.cut_vacations,
                        'cut_vacations_m2': self.cut_vacations_m2,
                        'cut_vacations_d2': self.cut_vacations_d2,
                        'afp': self.afp,
                        'gratification_description': self.gratification_description,
                        'cut_gratification': self.cut_gratification,
                        'bonus': self.bonus,
                        'cts_period': self.cts_period},
            'views': [[False, 'form']]
        }

    def print_liquidation_cts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'liquidación de depósitos semestrales de CTS',
            'res_model': 'hr.liquidation.cts.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, },
            'views': [[False, 'form']]
        }
