# -*- encoding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _sql_constraints = [
        ('employee_code_unique', 'unique(company_id, code)', 'El código del empleado debe ser único')
    ]

    code = fields.Char('Código de Empleado', copy=False)
    occupational_category_id = fields.Many2one(related='job_id.occupational_category_id', string='Categoría Ocupacional')
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipo de contratación')
    #type_employee = fields.Selection(selection=[("planilla", "Planilla"), ("tercero", "Tercero")], string='Tipo de empleado', default='planilla')
    is_not_dependent = fields.Boolean(string='No es Independiente', compute='_compute_is_not_dependent')
    minor_children = fields.Integer(string='Hijos menores de edad', copy=False)
    is_university = fields.Boolean(string='Cursando Estudios Superiores', copy=False)  # hijos cursando estudios universitarios
    # Campos que se utilizan para la plantilla AFP Net
    regimen_pensions = fields.Selection(string='Régimen pensionario',
                                        selection=[('afp', 'AFP'),
                                                   ('onp', 'ONP'),
                                                   ('srp', 'Sin Regimen Pensionario')],
                                        default='afp')
    afp_id = fields.Many2one('res.afp', string='AFP')
    afp_code = fields.Char(related='afp_id.code', string='Código AFP')
    commission_type = fields.Selection(string='Tipo de comisión',
                                       selection=[('FLUJO', 'FLUJO'),
                                                  ('MIXTA', 'MIXTA')])
    CUSPP = fields.Char(string='CUSPP', help="Código Único de Identificación del Sistema Privado de Pensiones", copy=False)
    type_work = fields.Selection(string='Tipo de trabajo o Rubro',
                                 selection=[('N', 'Dependiente Normal'),
                                            ('C', 'Dependiente Construcción'),
                                            ('M', 'Dependiente Minería'),
                                            ('P', 'Pesquero')])
    date_pensions = fields.Date(string='Fecha registro')
    # fin afp
    # Este campo se usa en el reporte Certificado de trabajo
    opinion = fields.Text(string="Opinión", groups="hr.group_hr_user", copy=False, tracking=True,
        help="Opinión que se plasmara en el Certificado de trabajo")
    age = fields.Integer(compute="_compute_age")
    cts_account = fields.Many2one('res.partner.bank', string='Cuenta CTS', copy=False,
        domain="[('partner_id', '=', address_home_id), ('type', '=', '1'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  tracking=True)
    bank_id = fields.Many2one('res.bank', string='Banco', related='cts_account.bank_id', readonly=1, copy=False)

    bank_account_id = fields.Many2one('res.partner.bank', copy=False,
        domain="[('partner_id', '=', address_home_id), ('type', '=', '2'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    cci = fields.Char(string='CCI', related='bank_account_id.cci', readonly=1)
    account_type = fields.Selection(string='Tipo de cuenta',
                                    selection=[('A', 'Ahorros'),
                                               ('C', 'Corriente'),
                                               ('M', 'Maestra'),
                                               ('B', 'Interbancaria')],
                                    default='A')
    document_type = fields.Many2one('hr.employee.document.type', string='Tipo de documento', help="Tipo de documento de Identidad",
                                    required=True, domain=[('identity', '=', 'True')])

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthday:
                age = relativedelta(fields.Date.today(), record.birthday).years
            record.age = age

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            self.country_of_birth = self.country_id

    @api.onchange('regimen_pensions')
    def _onchange_regimen_pensions(self):
        if self.regimen_pensions and self.regimen_pensions == 'onp':
            self.commission_type = False

    def is_onp(self):
        if self.regimen_pensions == 'onp':
            return 'SI'
        else:
            return ''

    @api.depends("contract_type_id")
    def _compute_is_not_dependent(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        for record in self:
            if record.contract_type_id and record.contract_type_id.id != contract_type:
                record.is_not_dependent = True
            else:
                record.is_not_dependent = False

    @api.constrains('document_type', 'identification_id')
    def _check_identification_id(self):
        for record in self:
            if record.identification_id and record.document_type:
                employee = self.search([('identification_id', '=', record.identification_id), ('document_type', '=', record.document_type.id), ('id', '!=', record.id)])
                if employee:
                    text = any(employee.mapped('name')) and ', '.join(employee.mapped('name')) or ''
                    raise ValidationError('El documento de identificación especificado ya existe para {}'.format(text))


class HrContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string="Tipo de Contrato", translate=True, required=True)