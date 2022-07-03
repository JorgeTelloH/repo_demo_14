# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    time_work = fields.Char('Tiempo de Servicio', compute="_compute_time_work")
    departure_reason = fields.Many2one('hr.employee.departure.reason', 'Departure reason')

    @api.depends('first_contract_date', 'departure_date')
    def _compute_time_work(self):
        for record in self:
            if record.first_contract_date and record.departure_date:
                years = relativedelta(record.departure_date,  record.first_contract_date).years
                months = relativedelta(record.departure_date,  record.first_contract_date).months
                days = relativedelta(record.departure_date,  record.first_contract_date).days
                record.time_work = "{} Año(s) {} Mes(es) {} Día(s)".format(years, months, days)
            else:
                record.time_work = ""

    def get_date_to_report(self, date):
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
                  "Noviembre", "Diciembre")
        _date = ''
        if date:
            month = months[date.month - 1]
            _date = "{} de {} del {}".format(date.day, month, date.year)

        return _date

    def _get_first_contracts(self):
        self.ensure_one()
        return self.sudo().with_context(active_test=False).contract_ids.filtered(lambda c: c.state != 'cancel')

    def print_work_certificates(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Certificado de trabajo',
            'res_model': 'hr.work.certificate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'opinion': self.opinion},
            'views': [[False, 'form']]
        }

    def print_withdrawal_letter_cts(self):
        return self.env.ref('cabalcon_hr_contract.action_withdrawal_letter').report_action(self)

class DepartureReason(models.Model):
    _name = "hr.employee.departure.reason"
    _description = 'Motivos de salida de la entidad'

    code = fields.Char(string='Código', required="True")
    name = fields.Char(string='Nombre corto', required=True)
    desc = fields.Char(string='Descripción', required="True")


    active = fields.Boolean(string='Active',  default=True)

    def unlink(self):
        for reason in self:
            contracts = self.env['hr.employee'].search([('departure_reason', '=', reason.id)])
            if len(contracts) > 0:
                raise ValidationError('No puedes eliminar este motivo de salidad porque está siendo usado')
        return super(DepartureReason, self).unlink()

class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Many2one('hr.employee.departure.reason', 'Departure reason', required=True)