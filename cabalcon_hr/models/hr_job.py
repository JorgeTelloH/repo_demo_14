# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Job(models.Model):
    _inherit = "hr.job"

    occupational_category_id = fields.Many2one('hr.occupational.category', string='Categoría ocupacional')

