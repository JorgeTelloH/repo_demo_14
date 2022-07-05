# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
import calendar
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ReportAmountBalancesOptimizedLine(models.Model):
	_name = 'report.amount.balances.optimized.line'
	_description = "Balance de Sumas y Saldos"
	# _rec_name = "name"
	report_amount_balances_optimized_id = fields.Many2one('report.amount.balances.optimized',string="Balance de Sumas y Saldos", ondelete="cascade", readonly=True)# , store=True)
	account_id = fields.Many2one('account.account', string="Cuenta", readonly=True)# , store=True)
	name_account=fields.Char(string="Cuenta", readonly=True)# , store=True)
	saldos_iniciales_deudor = fields.Char(string="Saldos Iniciales Deudor", readonly=True)# , store=True)
	saldos_iniciales_acreedor = fields.Char(string="Saldos Iniciales Acreedor", readonly=True)# , store=True)
	anio_fiscal_debe= fields.Char(string="Periodo Debe", readonly=True)# , store=True)
	anio_fiscal_haber= fields.Char(string="Periodo Haber", readonly=True)# , store=True)

	saldos_finales_deudor=fields.Char(string="Saldos Finales Deudor", readonly=True)# , store=True)
	saldos_finales_acreedor=fields.Char(string="Saldos Finales Acreedor", readonly=True)# , store=True)

	balance_general_activo=fields.Char(string="Balance General Activo", readonly=True)# , store=True)
	balance_general_pas_y_patr=fields.Char(string="Balance General Pas y Patr", readonly=True)# , store=True)

	resultados_naturaleza_perdidas=fields.Char(string="Resultados por Naturaleza Pérdidas", readonly=True)# , store=True)
	resultados_naturaleza_ganancias=fields.Char(string="Resultados por Naturaleza Ganancias", readonly=True)# , store=True)

	resultados_funcion_perdidas=fields.Char(string="Resultados por Función Pérdidas", readonly=True)# , store=True)
	resultados_funcion_ganancias=fields.Char(string="Resultados por Función Ganancias", readonly=True)# , store=True)






