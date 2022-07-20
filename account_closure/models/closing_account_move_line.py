# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import calendar
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ClosingAccountMoveLine(models.Model):
	_name = 'closing.account.move.line'
	_description = "Apunte Contable de Cierre"
	# _rec_name = "date_adjustment"

	account_closure_id=fields.Many2one('account.closure' , string="Cierre Contable", ondelete="cascade")
	closing_account_move_id= fields.Many2one('closing.account.move',string="Asiento Contable de Cierre", ondelete="cascade")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )] ,readonly=True)

	account_id = fields.Many2one('account.account', string="Cuenta")
	#branch_id = fields.Many2one('res.branch')
	date=fields.Date(string="Fecha")
	name = fields.Char(string="Etiqueta")
	amount_currency=fields.Float(string="Moneda de Importes")

	currency_id = fields.Many2one('res.currency', string="Moneda")

	saldo=fields.Float(string="Saldo S/.")
	saldo_currency=fields.Float(string="Saldo US$")

	debit= fields.Float(string="Debe")
	credit=fields.Float(string="Haber")

	debit_currency=fields.Float(string="Debe US$")
	credit_currency=fields.Float(string="Haber US$")

