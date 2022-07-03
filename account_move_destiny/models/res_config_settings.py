# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    automatic_destiny = fields.Boolean(string='Destinos Automáticos', related='company_id.automatic_destiny', readonly=False,)