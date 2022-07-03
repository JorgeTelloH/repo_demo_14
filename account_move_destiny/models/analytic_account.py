# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    target_debit_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe')
    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')