# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    canje_id = fields.Many2one('canje.letras', string='Canje Letra', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    letra_id = fields.Many2one('canje.letras.lineas', string='Lineas de Letra', readonly=True)


    def write(self, vals):
        if self and "full_reconcile_id" in vals:
            if vals.get("full_reconcile_id"):
                if self.letra_id:
                    for letra in self.letra_id:
                        letra.write({'state':'paid'})
            else:
                if self.letra_id:
                    for letra in self.letra_id:
                        letra.write({'state': 'paid'})
        return super().write(vals)

    # def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
    #     res = super(AccountMoveLine, self).reconcile(writeoff_acc_id,writeoff_journal_id)
    #     for line in self:
    #         if line.letra_id:
    #             line.letra_id._compute_residual()
    #     return res
