# -*- coding:utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _sql_constraints = [
        (
        'payroll_struct_uniq', 'unique(struct_id, date_from, date_to, contract_id, credit_note)', 'Un trabajador no pueda tener más de una nómina en un periodo y estructura salarial'
        ),
    ]

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        # res = []
        # # structure_ids = contracts.get_all_structures()
        # structure_ids = contracts.structure_type_id.struct_ids
        # rule_ids = self.env['hr.payroll.structure'].browse(structure_ids.ids).rule_ids
        # sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        # inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')
        #
        # for contract in contracts:
        #     for input in inputs:
        #         input_data = {
        #             'name': input.name,
        #             'code': input.code,
        #             'contract_id': contract.id,
        #         }
        #         res += [input_data]
        return self.input_line_ids

    def revert_leave_allocation(self):
        for payslip in self:
            holidays = self.env['hr.leave.allocation'].search([('payslip_id', '=', payslip.id)])
            holidays.action_refuse()
            holidays.action_draft()
            holidays.unlink()

    def revert_invoice(self):
        for payslip in self:
            invoice = self.env['account.move'].search([('payslip_id', '=', payslip.id)])
            invoice.button_draft()
            invoice.unlink()

    def create_leave_allocation(self):
        allocation = self.env['hr.leave.allocation']
        hs = self.env.ref('cabalcon_hr_holidays.holiday_status_vac').id
        name = "Asignación de vacaciones para %s del %s-%s" % (self.employee_id.name, self.date_from.month,self.date_from.year)
        values = {'employee_id': self.employee_id.id,
                  'holiday_type': 'employee',
                  'holiday_status_id': hs,
                  'name': name,
                  'number_of_days': 2.05,
                  'state': 'validate',
                  'payslip_id': self.id}
        allocation.create(values)

    def create_in_invoice(self):
        invoice = self.env['account.move']
        partner = self.env['res.partner'].search([('employee_id', '=', self.employee_id.id)])

        line_ids = [(0, 0, {
            'product_id':  self.company_id.product_id.id,
            'quantity': 1,
            'price_unit': self.net_wage,

        })]
        values = {'partner_id': partner.id,
                  'invoice_date': self.date_to,
                  'move_type': 'in_invoice',
                  'invoice_line_ids': line_ids,
                  'payslip_id': self.id
                  }
        invoice.sudo().create(values)

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        # Esto era para generar lo 2.05 dias que acumula de vacaciones
        # contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent')
        # tdays = self._get_worked_days_line_number_of_days('WORK100')
        # if self.employee_id.contract_id.contract_type_id == contract_type and tdays > 0:
        #     self.create_leave_allocation()

        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_formal_independent')
        if self.employee_id.contract_id.contract_type_id == contract_type and self.net_wage > 0:
            if not self.company_id.product_id:
                raise ValidationError('Debe configurar el producto Recibo por Honorarios')
            self.create_in_invoice()

        return res

    def refund_sheet(self):
        for payslip in self:
            payslip.revert_leave_allocation()
            payslip.revert_invoice()

        return super(HrPayslip, self).refund_sheet()

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'compute_employment_essalud': compute_employment_essalud,
            'compute_gratification': compute_gratification,
        })
        return res


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    is_employer_contributions = fields.Boolean(related='salary_rule_id.is_employer_contributions', readonly=True)


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    payslip_id = fields.Many2one('hr.payslip', string='payslip')


class AccountMove(models.Model):
    _inherit = "account.move"

    payslip_id = fields.Many2one('hr.payslip', string='payslip')


def compute_employment_essalud(payslip, categories):
    value = 0
    if payslip:
        if payslip.contract_id.eps:
            essalud_tax = payslip.company_id.eps_tax
        else:
            essalud_tax = payslip.company_id.essalud_tax

        essalud_rmv = payslip.company_id.essalud_rmv

        net_wage = categories.BASIC + categories.ALW

        if net_wage > essalud_rmv:
            value = essalud_rmv * essalud_tax / 100
        else:
            value = net_wage * essalud_tax / 100

    return value


def compute_gratification(payslip, categories):
    value = 0
    if payslip:
        ok = False
        if payslip.date_from.month == 7:
            date_init_str = '%s-01-01' % (payslip.date_from.year)
            date_init = fields.Date.to_date(date_init_str)
            if payslip.contract_id.date_start > date_init:
                date_init = payslip.contract_id.date_start
            date_end_str = '%s-06-30' % (payslip.date_from.year)
            date_end = fields.Date.to_date(date_end_str)
            ok = True

        if payslip.date_from.month == 12:
            date_init_str = '%s-07-01' % (payslip.date_from.year)
            date_init = fields.Date.to_date(date_init_str)
            if payslip.contract_id.date_start > date_init:
                date_init = payslip.contract_id.date_start
            date_end_str = '%s-12-31' % (payslip.date_from.year)
            date_end = fields.Date.to_date(date_end_str)
            ok = True

        if ok:
            c_months = relativedelta(date_end, date_init).months
            net_wage = categories.BASIC + payslip.AF
            value = (net_wage/6) * c_months

    return value