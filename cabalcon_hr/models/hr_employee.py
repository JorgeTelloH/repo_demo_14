# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _sql_constraints = [
        ('employee_code_unqiue', 'unique(company_id, code)', 'El código del empleado debe ser único')
    ]

    code = fields.Char('Código', copy=False)
    occupational_category_id = fields.Many2one(related='job_id.occupational_category_id', string='Categoría ocupacional')
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipo de empleado')
    is_not_dependent = fields.Boolean(string='No es un indepandiente', compute='_compute_is_not_dependent')

    # Campos que se utilizan para la plantilla AFP Net
    afp_id = fields.Many2one('res.afp', string='AFP')
    afp_code = fields.Char(related='afp_id.code')
    commission_type = fields.Selection(string='Tipo de comisión',
                                       selection=[('FLUJO', 'FLUJO'),
                                                  ('MIXTA', 'MIXTA')])

    CUSPP = fields.Char(string='CUSPP', help="Código Único de Identificación del Sistema Privado de Pensiones")
    # type_document = fields.Many2one('hr.employee.type.document', string='Tipo de documento', help="Tipo de documento", required=True)

    # type_document = fields.Selection(string='Tipo de documento',
    #                                  selection=[('01', 'DNI'),
    #                                             ('04', 'Carnet de Extranjería'),
    #                                             ('2', 'Carnet Militar y Policial'),
    #                                             ('3', 'Libreta Adolecentes Trabajador'),
    #                                             ('07', 'Pasaporte'),
    #                                             ('5', 'Inexistente/Afilia'),
    #                                             ('22', 'Carné de Ident.-RR EE'),
    #                                             ('23', 'Carné PTP'),
    #                                             ('23', 'Documento de identidad extranjero'),
    #                                             ('09', 'Carné de Solicit. de Refugio')
    #                                             ],
    #                                  help="Tipo de documento de identidad")
    type_work = fields.Selection(string='Tipo de trabajo o Rubro',
                                 selection=[('N', 'Dependiente Normal'),
                                            ('C', 'Dependiente Contrucción'),
                                            ('M', 'Dependiente Minería'),
                                            ('P', 'Pesquero')])
    # fin afp

    # Este campo se usa en el reporte Certificado de trabajo
    opinion = fields.Text(string="Opinión", groups="hr.group_hr_user", copy=False, tracking=True,
                          help="Opinión que se plasmara en el Certificado de trabajo")

    age = fields.Integer(compute="_compute_age")
    cts_account = fields.Many2one('res.partner.bank', 'Cuenta CTS',
                                  domain="[('partner_id', '=', address_home_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  tracking=True)

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

    @api.onchange('afp_id')
    def _onchange_afp_id(self):
        if self.afp_id and self.afp_id.code == 'ONP':
            self.commission_type = False

    def is_onp(self):
        if self.env.ref('cabalcon_hr.afp_ONP').id == self.afp_id.id:
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


class HrContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string="Tipo", translate=True, required=True)