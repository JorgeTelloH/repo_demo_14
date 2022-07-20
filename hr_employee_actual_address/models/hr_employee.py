# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    
    address_country_id = fields.Many2one('res.country', string='Pais', ondelete='restrict')
    address_state_id = fields.Many2one("res.country.state", string='Dpto', ondelete='restrict', domain="[('country_id', '=?', address_country_id)]")
    address_city_id = fields.Many2one('res.city', string='Provincia')
    address_l10n_pe_district = fields.Many2one('l10n_pe.res.city.district', string='Distrito')
    address_street = fields.Char(string='Dirección Actual', help='Dirección donde reside actualmente el Empleado')
    address_ref = fields.Char(string='Referencia', help='Referencia de la Dirección Actual donde reside el Empleado')


    @api.onchange("address_state_id")
    def onchange_address_state_id(self):
        self.address_country_id = self.address_state_id.country_id.id

    @api.onchange("address_city_id")
    def onchange_address_city_id(self):
        self.address_state_id = self.address_city_id.state_id.id

    @api.onchange("address_l10n_pe_district")
    def onchange_address_l10n_pe_district(self):
        self.address_city_id = self.address_l10n_pe_district.city_id.id
