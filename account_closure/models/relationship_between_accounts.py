# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
import logging
_logger = logging.getLogger(__name__)

class RelationshipBetweenAccounts(models.Model):
	_name = 'relationship.between.accounts'
	_description = "Relación entre cuentas para Cierre y Apertura"

		## cuenta de cierre contable y cuentas afectas
	name=fields.Char(string="Nombre")
	closing_opening_account_id=fields.Many2one('account.account', string="Cuenta de Cierre/Apertura",required=True)
	affected_account_ids = fields.Many2many('account.account','account_relationship_between_account_rel','account_id','relationship_between_id',string="Cuentas Afectas",required=True)
	operation_type=fields.Selection(selection=[('closure','Cierre Contable'),('opening','Apertura Contable')], required=True , default='closure')
	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )], readonly=True)

	def clear_fields(self):
		self.name=""
		self.closing_opening_account_id=None
		self.affected_account_ids=None
		self.operation_type=None

	def clear_affected_account_ids(self):
		self.affected_account_ids=None