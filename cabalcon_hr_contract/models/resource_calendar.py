from odoo import fields, models, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    vacation_record = fields.Integer(string='Record vacacional', default=260)