# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, Warning
import requests
import json
URL_RENIEC = 'https://dniruc.apisperu.com/api/v1/dni'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    occupational_category_id = fields.Many2one(related='job_id.occupational_category_id', string='Categoría Ocupacional')
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipo de contratación')
    is_not_dependent = fields.Boolean(string='No es Independiente', compute='_compute_is_not_dependent')
    # Campos que se utilizan para la plantilla AFP Net
    regimen_pensions = fields.Selection(string='Régimen pensionario',
                                        selection=[('afp', 'AFP'),
                                                   ('onp', 'ONP'),
                                                   ('srp', 'Sin Regimen Pensionario')], default='afp')
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
        help="Opinión que se colocará en el Certificado de trabajo")
    age = fields.Integer(compute="_compute_age")
    cts_account = fields.Many2one('res.partner.bank', string='Cuenta CTS', copy=False,
        domain="[('partner_id', '=', address_home_id), ('type', '=', '1'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  tracking=True)
    bank_id = fields.Many2one('res.bank', string='Banco de CTS', related='cts_account.bank_id', readonly=1, copy=False)

    bank_account_id = fields.Many2one('res.partner.bank', string='Cuenta Bancaria', copy=False,
        domain="[('partner_id', '=', address_home_id), ('type', '=', '2'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    cci = fields.Char(string='CCI Bancario', related='bank_account_id.cci', readonly=1)
    account_type = fields.Selection(string='Tipo de Cuenta',
                                    selection=[('A', 'Ahorros'),
                                               ('C', 'Corriente'),
                                               ('M', 'Maestra'),
                                               ('B', 'Interbancaria')],
                                    default='A')
    document_type = fields.Many2one('hr.employee.document.type', string='Tipo de documento', help="Tipo de documento de Identidad",
                                    required=True, domain=[('identity', '=', 'True')])
    mobile_personal = fields.Char('Celular Personal')


    #Buscamos el movil personal del Empleado
    @api.onchange('address_home_id')
    def _onchange_mobile_address_home_id(self):
        if not self.mobile_personal and self.address_home_id:
            self.mobile_personal = self.address_home_id.mobile

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

    #============= INI CONSULTAR DNI =============
    def action_get_dni(self):
        self.ensure_one()
        if self.identification_id and self.document_type.code == '01':
            if len(self.identification_id) == 8 and int(self.identification_id):
                self._update_dni()
            else:
                raise Warning('Documento de Identidad incorrecto!')

    def _update_dni(self):
        company_id = self.company_id or self.env['res.company'].browse(self.env.company.id) 
        if not company_id.search_api_peru:
            raise Warning('Configure el token en la compañia')
        token = company_id.token_api_peru
        #Arma consulta RENIEC con el DNI y Token
        url = ('%s/%s?token=%s' % (URL_RENIEC, self.identification_id, token))
        ses = requests.session()
        res = ses.get(url)
        if res.status_code == 200:
            dic_res = json.loads(res.text)
            if dic_res:
                nombres = dic_res.get('nombres')
                apellidoPaterno = dic_res.get('apellidoPaterno')
                apellidoMaterno = dic_res.get('apellidoMaterno')

                self.firstname = nombres
                self.lastname = apellidoPaterno
                self.lastname2 = apellidoMaterno

        return True
    #============= FIN CONSULTAR DNI =============
