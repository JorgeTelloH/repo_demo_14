# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
import calendar
from datetime import datetime, timedelta
import logging

class TableAccountCumSumClosure(models.Model):
	_name = 'table.account.cum.sum.closure'
	_description = "Tabla Buffer Cierre/Apertura Contable"

	closure_id = fields.Many2one('account.closure',string="Cierre/Apertura Contable")
	#############################################
	closing_account_id = fields.Many2one('account.account',string="Cuenta de Cierre/Apertura")
	affected_account_id = fields.Many2one('account.account',string="Cuenta Afecta")
	saldo_soles = fields.Float(strinf="Saldo Soles")
	saldo_dolares = fields.Float(strinf="Saldo Dólares")

