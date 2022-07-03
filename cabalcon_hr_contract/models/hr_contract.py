# -*- coding: utf-8 -*-
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _inherit = 'hr.contract'

    department_id = fields.Many2one(tracking=True)
    job_id = fields.Many2one(tracking=True)
    structure_type_id = fields.Many2one(tracking=True)
    resource_calendar_id = fields.Many2one(tracking=True)
    reason = fields.Text(string="Razón", help='Especifique la razón de la cancelación')
    contract_type_id = fields.Many2one('hr.contract.type', 'Contract Type', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('near_expire', 'Near to Expire'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')
    # Informacion de la afp del empleado
    afp_id = fields.Many2one('res.afp', string='AFP', compute="_compute_afp_info")
    afp_seat = fields.Float(string='Fondo', compute="_compute_afp_info")
    afp_commission_flow = fields.Float(string='Comisión flujo', compute="_compute_afp_info")
    afp_commission_mixed = fields.Float(string='Comisión mixta', compute="_compute_afp_info")
    afp_insurance = fields.Float(string='Seguro', compute="_compute_afp_info")
    # campo para marcar si tiene impuesto a la renta de quinta categoría
    has_rent_5ta = fields.Boolean(string='Ret. Renta 5ta', default=False,
                                  help='Marque esta casilla se el empleado se acoge al impuesto a la renta de quinta categoría')
    # campos para la seguridad social
    has_social_security = fields.Selection([('Y', 'Si'), ('N', 'No')], string='Seguro Social')
    social_security_id = fields.Many2one('hr.employee.health.entity', string='Aseguradora de salud')

    eps = fields.Boolean(string='Tiene EPS', default=False)
    eps_amount = fields.Monetary(string='Importe EPS')
    eps_credit = fields.Integer(string='Cantidad de credito EPS')

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.employee_id:
                name = record.name + ' - ' + record.employee_id.name
            res.append((record.id, name))
        return res

    @api.onchange('eps')
    def _onchange_eps(self):
        if not self.eps:
            self.eps_amount = 0
            self.eps_credit = 0

    def _compute_afp_info(self):
        for contract in self:
            if contract.employee_id.afp_id:
                contract.afp_id = contract.employee_id.afp_id
                contract.afp_seat = contract.employee_id.afp_id.seat
                contract.afp_commission_flow = contract.employee_id.afp_id.commission_flow
                contract.afp_commission_mixed = contract.employee_id.afp_id.commission_mixed
                contract.afp_insurance = contract.employee_id.afp_id.insurance
            else:
                contract.afp_id = False
                contract.afp_seat = 0
                contract.afp_commission_flow = 0
                contract.afp_commission_mixed = 0
                contract.afp_insurance = 0

    def manage_contract_expiration(self):
        date_today = fields.Date.from_string(fields.Date.today())
        outdated_days = fields.Date.to_string(date_today + relativedelta(days=+self.env['res.users'].browse(self._context['uid']).company_id.alert_contract))
        nearly_expired_contracts = self.search([('state', '=', 'open'), ('date_end', '<', outdated_days)])
        nearly_expired_contracts.write({'state': 'near_expire'})
        expired_contracts = self.search([('state', '=', 'near_expire'), ('date_end', '<', fields.Date.today())])
        expired_contracts.write({'state': 'close'})

    def notification_contract_expiration(self):
        date_today = fields.Date.from_string(fields.Date.today())
        company = self.env['res.users'].browse(self._context['uid']).company_id
        outdated_days = fields.Date.to_string(date_today + relativedelta(days=company.alert_contract))
        nearly_expired_contracts = self.search([('state', '=', 'open'), ('date_end', '<', outdated_days)])
        if not company.notification_contract_expiration_ids:
            raise ValidationError("No se ha configurado el/los empleado al que se le notificara los contratos próximos a expirar")

        template = self.env.ref('cabalcon_hr_contract.email_template_notification_contract')
        users = company.notification_contract_expiration_ids
        for contract in nearly_expired_contracts:
            for user in users:
                if user.work_email:
                    template.write({'email_to': user.work_email})
                    template.send_mail(contract.id, force_send=True)

    def create_partner(self, contract):
        partner = self.env['res.partner']
        values = {'name': contract.employee_id.name,
                  'employee': True,
                  'employee_id': contract.employee_id.id,
                  'company_type': 'person',
                  'type': 'contact'
                  }
        partner.create(values)

    @api.depends('employee_id')
    def _compute_employee_contract(self):
        super(Contract, self)._compute_employee_contract()
        for contract in self.filtered('employee_id'):
            contract.contract_type_id = contract.employee_id.contract_type_id

    @api.model
    def create(self, vals):
        res = super(Contract, self).create(vals)
        res.employee_id.write({'department_id': res.department_id.id, 'job_id': res.job_id.id, 'contract_type_id': self.contract_type_id.id})
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_formal_independent').id
        if contract_type == vals.get('contract_type_id'):
            self.create_partner(res)

        return res

    def write(self, vals):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_formal_independent').id
        if 'contract_type_id' in vals and vals['contract_type_id'] == contract_type:
            partner = self.env['res.partner'].search([('employee_id', '=', self.employee_id.id)])
            if not partner:
                self.create_partner(self)
        res = super(Contract, self).write(vals)
        if 'department_id' in vals:
            self.mapped('employee_id').write({'department_id': vals.get('department_id')})
        if 'job_id' in vals:
            self.mapped('employee_id').write({'job_id': vals.get('job_id')})
        if 'contract_type_id' in vals:
            self.mapped('employee_id').write({'contract_type_id': vals.get('contract_type_id')})
        return res




