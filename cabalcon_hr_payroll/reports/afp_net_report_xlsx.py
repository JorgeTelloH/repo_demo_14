# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields
from odoo.exceptions import UserError, ValidationError


class ReconciliationReportXlsx(models.AbstractModel):
    _name = "report.cabalcon_hr_payroll.afp_net_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte AFP Net"

    def labor_relation_started(seft, ddate, _date):
        if _date.year == ddate.year and _date.month == ddate.month:
            return 'S'
        else:
            return 'N'

    def labor_relation_finished(self, ddate, _date):
        if ddate and _date.year == ddate.year and _date.month == ddate.month:
            return 'S'
        else:
            return 'N'

    # def get_salary(self, contract_id, date_from, date_to):
    #     payslip = self.env['hr.payslip'].search([
    #         ('contract_id', '=', contract_id),
    #         ('state', '=', 'done'),
    #         ('date_from', '>=', date_from),
    #         ('date_to', '<=', date_to),
    #     ], limit=1).net_wage
    #     return payslip

    def generate_xlsx_report(self, workbook, data, employees):

        employees = self.env['hr.employee'].browse(data['data_report'])
        date_from = data['date_from']
        date_to = data['date_to']
        _date = fields.Date.to_date(date_from)

        bold = workbook.add_format({"bold": True, 'valign': 'vcenter', 'text_wrap': True, "align": "center"})
        sheet = workbook.add_worksheet('Plantilla')

        show_header = data['show_header']
        headers = ['Número de secuencia', 'CUSPP', 'Tipo de documento de identidad', 'Número de documento de indentidad',
                   'Apellido paterno', 'Apellido materno', 'Nombres', 'Relación Laboral', 'Inicio de RL', 'Cese de RL',
                   'Excepcion de Aportar', 'Remuneración asegurable', 'Aporte voluntario del afiliado con fin previsional',
                   'Aporte voluntario del afiliado sin fin previsional', 'Aporte voluntario del empleador',
                   'Tipo de trabajo o Rubro', 'AFP (Conviene dejar en blanco)']

        row = 0
        if show_header:
            col = 0
            for header in headers:
                sheet.write(row, col, header, bold)
                col += 1
            row = 1

        sheet.set_column(0, 1, 8)
        sheet.set_column(0, 2, 8)
        sheet.set_column(0, 3, 15)
        sheet.set_column(0, 4, 10)
        sheet.set_column(0, 5, 10)
        sheet.set_column(0, 6, 8)
        sheet.set_column(0, 7, 8)
        sheet.set_column(0, 8, 8)
        sheet.set_column(0, 9, 8)
        sheet.set_column(0, 10, 10)
        sheet.set_column(0, 11, 10)
        sheet.set_column(0, 12, 12)
        sheet.set_column(0, 13, 12)
        sheet.set_column(0, 14, 12)
        sheet.set_column(0, 15, 12)
        sheet.set_column(0, 16, 15)

        item = 1
        for emp in employees:
            if emp.contract_id:
                sheet.write(row, 0, item)
                sheet.write(row, 1, emp.CUSPP or '')
                sheet.write(row, 2, int(emp.type_document) or 0)
                sheet.write(row, 3, emp.identification_id or '')
                sheet.write(row, 4, emp.lastname)
                sheet.write(row, 5, emp.lastname2 or '')
                sheet.write(row, 6, emp.firstname)
                sheet.write(row, 7, 'S' if emp.contract_id.state == 'open' else 'N')
                sheet.write(row, 8, self.labor_relation_started(emp.contract_id.date_start, _date))
                sheet.write(row, 9, self.labor_relation_finished(emp.contract_id.date_end, _date))
                sheet.write(row, 10, '')
                sheet.write(row, 11, '')
                sheet.write(row, 12, '')
                sheet.write(row, 13, '')
                sheet.write(row, 14, '')
                sheet.write(row, 15, '')
                sheet.write(row, 16, '')
                item += 1
                row += 1





