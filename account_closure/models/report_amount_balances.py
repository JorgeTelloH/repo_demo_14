# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
import calendar
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ReportAmountBalances(models.Model):
	_name = 'report.amount.balances'
	_description = "Balance de Comprobación"
	# _rec_name = "name"
	account_closure_id= fields.Many2one('account.closure',string="Cierre Contable", ondelete="cascade", readonly=True)
	account_id = fields.Many2one('account.account', string="Cuenta", readonly=True)
	name_account=fields.Char(string="Cuenta", readonly=True)
	saldos_iniciales_deudor = fields.Char(string="Saldos Iniciales Deudor", readonly=True)
	saldos_iniciales_acreedor = fields.Char(string="Saldos Iniciales Acreedor", readonly=True)
	anio_fiscal_debe= fields.Char(string="Periodo Debe", readonly=True)
	anio_fiscal_haber= fields.Char(string="Periodo Haber", readonly=True)

	saldos_finales_deudor=fields.Char(string="Saldos Finales Deudor", readonly=True)
	saldos_finales_acreedor=fields.Char(string="Saldos Finales Acreedor", readonly=True)

	balance_general_activo=fields.Char(string="Balance General Activo", readonly=True)
	balance_general_pas_y_patr=fields.Char(string="Balance General Pas y Patr", readonly=True)

	resultados_naturaleza_perdidas=fields.Char(string="Resultados por Naturaleza Pérdidas", readonly=True)
	resultados_naturaleza_ganancias=fields.Char(string="Resultados por Naturaleza Ganancias", readonly=True)

	resultados_funcion_perdidas=fields.Char(string="Resultados por Función Pérdidas", readonly=True)
	resultados_funcion_ganancias=fields.Char(string="Resultados por Función Ganancias", readonly=True)






