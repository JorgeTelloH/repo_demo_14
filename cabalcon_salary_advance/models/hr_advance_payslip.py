# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models


class SalaryRuleInput(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(SalaryRuleInput, self).get_inputs(contract_ids, date_from, date_to)
        # res = self.input_line_ids
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        adv_salary = self.env['salary.advance'].search([('employee_id', '=', emp_id.id)])
        for adv_obj in adv_salary:
            current_date = date_from.month
            date = adv_obj.date
            existing_date = date.month
            result = res.filtered(lambda a: a.code == 'SAR')
            if result:
                result['amount'] = adv_obj.advance
            else:
                input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'SAR')], limit=1)
                values = {'input_type_id': input_type.id, 'amount': adv_obj.advance}
                res += result.new(values)
            # if current_date == existing_date:
            #     state = adv_obj.state
            #     amount = adv_obj.advance
            #     for result in res:
            #         if state == 'approve' and amount != 0 and result.get('code') == 'SAR':
            #             result['amount'] = amount
        return res
