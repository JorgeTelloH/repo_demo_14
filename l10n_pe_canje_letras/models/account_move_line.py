# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    letra_id = fields.Many2one('canje.letras.lineas', string='Letra', readonly=True)

    # def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
    #     res = super(AccountMoveLine, self).reconcile(writeoff_acc_id,writeoff_journal_id)
    #     for line in self:
    #         if line.letra_id:
    #             line.letra_id._compute_residual()
    #     return res
