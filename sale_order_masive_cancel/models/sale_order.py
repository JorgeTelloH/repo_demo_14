# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_masive_cancel(self):
        self.action_cancel()
        return

    def action_send_masive_draft(self):
        self.action_draft()
        return

