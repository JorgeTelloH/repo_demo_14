# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

MONTHS = [('01', 'Enero'),
          ('02', 'Febrero'),
          ('03', 'Marzo'),
          ('04', 'Abril'),
          ('05', 'Mayo'),
          ('06', 'Junio'),
          ('07', 'Julio'),
          ('08', 'Agosto'),
          ('09', 'Septiembre'),
          ('10', 'Octubre'),
          ('11', 'Noviembre'),
          ('12', 'Diciembre')]


class MatrixWizard(models.TransientModel):
    _name = 'matrix.wizard'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year - 2, datetime.now().year + 1)]

    def get_df(self):
        cd = 0
        if self.month and self.year:
            resource_calendar = self.env.user.company_id.resource_calendar_id
            cd = len(resource_calendar.global_leave_ids.filtered(lambda a: a.work_entry_type_id.code == 'LEAVE120' and a.date_from.year == self.year))
        return cd

    month = fields.Selection(string='Mes', selection=MONTHS, required=True)
    year = fields.Selection(string='Año', selection=_get_years, required=True, default=str(datetime.now().year))
    df = fields.Integer(string='Días Feriado')
    dd = fields.Integer(string='Días de Descanso')

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    def action_print(self):

        date_from = fields.Date.today().replace(day=1, month=int(self.month), year=int(self.year))
        date_to = date_from + relativedelta(months=+1, day=1, days=-1)

        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        contracts = self.env['hr.contract'].search([('contract_type_id', '=', contract_type),
                                                    ('state', 'in', ('open', 'close')),
                                                    ('company_id', '=', self.company_id.id), '|',
                                                    ('date_end', '=', False), '&',
                                                    ('date_end', '>', date_from), ('date_end', '<', date_to)])
        if not contracts:
            raise ValidationError('No se encontraron empleados para este reporte')

        data = {'data_report': contracts.ids, 'date_from': date_from, 'date_to': date_to,
                'company_id': self.company_id.id, 'year': self.year, 'month': self.month,
                'df': self.df, 'dd': self.dd}

        return self.env.ref('cabalcon_hr_payroll.action_matrix_report_xlsx').report_action(self, data=data)
