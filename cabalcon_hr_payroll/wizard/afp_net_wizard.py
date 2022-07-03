# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AfpNetWizard(models.TransientModel):
    _name = 'afp.net.wizard'

    date_from = fields.Date(string='Fecha de inicio', required=True, default=fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Fecha fin', required=True)
    show_header = fields.Boolean(string='Mostrar encabezado de columnas', default=True)

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            self.date_to = self.date_from + relativedelta(months=+1, day=1, days=-1)

    def action_print(self):
        if self.date_to < self.date_from:
            raise ValidationError('La fecha fin no puede ser menor que la fecha inicio')

        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        employees = self.env['hr.employee'].search([('contract_id.contract_type_id', '=', contract_type)])
        if not employees:
            raise ValidationError('No se encontraron empleados para este reporte')

        data = {'data_report': employees.ids, 'show_header': self.show_header, 'date_from': self.date_from,
                'date_to': self.date_to}

        return self.env.ref('cabalcon_hr_payroll.action_afp_net_report_xlsx').report_action(self, data=data)
