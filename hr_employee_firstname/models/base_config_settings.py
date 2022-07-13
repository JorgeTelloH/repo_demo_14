# -*- encoding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    employee_names_order = fields.Selection(
        string="Employee Names Order", 
        selection="_employee_names_order_selection",
        help="Order to compose employee fullname", config_parameter="employee_names_order", 
        default=lambda a: a._employee_names_order_default(),
        required=True,
    )

    def _employee_names_order_selection(self):
        return [
            ("last_first", "Lastname Firstname"),
            ("last_first_comma", "Lastname, Firstname"),
            ("first_last", "Firstname Lastname"),
        ]

    def _employee_names_order_default(self):
        return self.env["hr.employee"]._names_order_default()
