# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
import calendar
from datetime import datetime, timedelta
import logging
from odoo.addons import unique_library_accounting_queries as unique_queries
_logger = logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

class AccountClosure(models.Model):
	_name = 'account.closure'
	_description = "Cierre Contable"
	_rec_name = "name"

	state = fields.Selection(selection=[('draft','Borrador'),('generated','Generado'),('posted','Publicado'),('cancel','Cancelado')],
		readonly=True, states={'draft': [('readonly', False)]},
		string="Estado", default="draft")

	closing_account_move_ids= fields.One2many('closing.account.move', 'account_closure_id', string="Asientos contables de Cierre/Apertura")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )] , readonly=True)
	
	name = fields.Char(string="Nombre")
	date=fields.Date(string="Fecha de Cierre/Apertura Contable")

	################################# CAMPOS PARA EXTENDER LA FUNCIONALIDAD DEL CIERRE/APERTURA
	type_closing_opening = fields.Selection(selection=[('1','Cierre Hasta la Fecha'),('2','Cierre en un rango de Fechas')],
		string="Tipo de Cierre/Apertura", default="1", required=True)
	
	date_from=fields.Date(string="Desde:" ,readonly=True , states={'draft': [('readonly', False)]})
	date_to=fields.Date(string="Hasta:" ,readonly=True , states={'draft': [('readonly', False)]})

	################################################

	partner_ids = fields.Many2many('res.partner','account_closure_partner_rel','partner_id','account_closure_i' ,string="Socios")
	partner_option=fields.Selection(selection=options , string="")

	account_ids = fields.Many2many('account.account','account_closure_account_rel','account_id','account_closure_id',string='Cuentas')
	account_option=fields.Selection(selection=options , string="")

	journal_ids = fields.Many2many('account.journal','account_closure_journal_rel','journal_id','account_closure_id',string="Diarios")
	journal_option=fields.Selection(selection=options , string="")

	move_ids = fields.Many2many('account.move','account_closure_move_rel','move_id','account_closure_id',string='Asientos Contables')
	move_option=fields.Selection(selection=options , string="")
	#############################################################################

	closing_account_move_line_ids = fields.One2many('closing.account.move.line' , 'account_closure_id', string="Apuntes Contables Generados")
	## BALANCE DE SUMAS Y SALDOS
	
	fecha_inicio=fields.Date(string="Fecha Inicio" )
	fecha_final=fields.Date(string="Fecha Final" )

	report_amount_balances_ids = fields.One2many('report.amount.balances' , 'account_closure_id' , string="Balance de Sumas y Saldos", readonly=True)


	tabla_cuentas_saldos=[]

	def get_filter_clause(self):
		filter_clause=''

		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			filter_clause += " and aml.partner_id %s %s" % (self.partner_option or 'in', str(partners) if len_partners!=1 else str(partners)[0:len(str(partners))-2] + ')')

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			filter_clause += " and aml.journal_id %s %s " % (self.journal_option or 'in', str(journals) if len_journals!=1 else str(journals)[0:len(str(journals))-2] + ')')

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			filter_clause += " and aml.move_id %s %s " % (self.move_option or 'in', str(moves) if len_moves!=1 else str(moves)[0:len(str(moves))-2] + ')')

		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			filter_clause += " and aml.account_id %s %s " % (self.account_option or 'in', str(accounts) if len_accounts!=1 else str(accounts)[0:len(str(accounts))-2] + ')')

		return filter_clause

	#######################################

	
	def fill_table_balance(self):
		# formato de la tabla : (cuenta_cierre , cuenta_afecta , saldo)
		self.tabla_cuentas_saldos=[]
		for line in self.closing_account_move_ids:
			self.tabla_cuentas_saldos.append([line.closing_account_id, line.affected_account_ids[0] if len(line.affected_account_ids.ids or '')==1 else '',0.00,0.00])

	
	def search_saldo_account_in_table(self,account):
		saldo_soles = -sum([item[2] for item in self.tabla_cuentas_saldos if item[0]==account])
		saldo_dolares = -sum([item[3] for item in self.tabla_cuentas_saldos if item[0]==account])
		return [saldo_soles or 0.00,saldo_dolares or 0.00]


	
	def generate_accounting_entry(self):
		i=0
		for line in self.closing_account_move_ids:
			#if line.operation_type=='closure':
			saldo_inicial_soles=0.00
			saldo_inicial_dolares=0.00
			if len(line.affected_account_ids.ids or '')==1:
				saldo_inicial_soles, saldo_inicial_dolares= self.search_saldo_account_in_table(line.affected_account_ids[0])
			saldo_final_soles , saldo_final_dolares =line.generate_accounting_entries(saldo_inicial_soles_cuenta_afecta=saldo_inicial_soles,saldo_inicial_dolares_cuenta_afecta=saldo_inicial_dolares)
			self.tabla_cuentas_saldos[i][2]=-saldo_final_soles
			self.tabla_cuentas_saldos[i][3]=-saldo_final_dolares
			i += 1



	
	def run_closure(self):
		if not len(self.closing_account_move_ids.ids or ''):
			raise UserError(_('NO SE COMPLETÓ EL PROCESO. LLENE POR LO MENOS UNA ENTRADA EN LOS ASIENTOS DE CIERRE !'))
		# checkando que todas las entradas tengan cuentas de cierre y afectas
		for line in self.closing_account_move_ids:
			if not line.closing_account_id:
				raise UserError(_('TODAS LAS ENTRADAS DEBEN TENER UNA CUENTA DE CIERRE !'))
		self.fill_table_balance()
		# for line in self.closing_account_move_ids:
		self.generate_accounting_entry()
		self.state="generated"


	def limpiar_apuntes_contables_generados(self):
		self.closing_account_move_line_ids.unlink()


	def post_account_moves(self):
		for line in self.closing_account_move_ids:
			line.post()
		self.state="posted"


	def cancel(self):
		for line in self.closing_account_move_ids:
			line.generated_account_move_id.button_cancel()
			line.generated_account_move_id.unlink()	
		self.state="cancel"


	def draft(self):
		self.state="draft"


	
	def limpiar_campos(self):
		self.name=None
		self.date=None
		self.closing_account_move_ids=None
		self.closing_account_move_line_ids=None



	
	def query_balance_of_sums_and_balances(self,fecha_movimiento_debe,fecha_movimiento_haber):
		query = unique_queries.query_account_amount_balances(fecha_movimiento_debe,fecha_movimiento_haber,'')

		
		self.env.cr.execute(query)
		records = self.env.cr.dictfetchall()
		return records


	
	def run_balance_of_sums_and_balances(self):
		self.report_amount_balances_ids.unlink()
		registro= []

		records=self.query_balance_of_sums_and_balances(self.fecha_inicio,self.fecha_final)
		saldo=[0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00]
		for line in records:
			account_id=self.env['account.account'].browse(line['id'])
			saldos_finales_deudor=(line['debit_saldo_inicial'] or 0.00) + (line['debit_movimiento_periodo'] or 0.00)
			saldos_finales_acreedor=(line['credit_saldo_inicial'] or 0.00) + (line['credit_movimiento_periodo'] or 0.00)

			balance_inicial=(line['debit_saldo_inicial'] or 0.00) - (line['credit_saldo_inicial'] or 0.00)

			balance=saldos_finales_deudor - saldos_finales_acreedor
			registro.append((0,0,{
				'account_id':line['id'],
				'name_account':' '.join([line['code'] or '' , line['name'] or '']),
				'saldos_iniciales_deudor':'{:,.2f}'.format(abs(balance_inicial)) if balance_inicial>0 else '',
				'saldos_iniciales_acreedor':'{:,.2f}'.format(abs(balance_inicial)) if balance_inicial<0 else '',
				'anio_fiscal_debe':'{:,.2f}'.format(line['debit_movimiento_periodo'] or 0.00) if line['debit_movimiento_periodo'] else '',
				'anio_fiscal_haber':'{:,.2f}'.format(line['credit_movimiento_periodo'] or 0.00) if line['credit_movimiento_periodo'] else '',
				'saldos_finales_deudor':'{:,.2f}'.format(abs(balance)) if balance>0 else '',
				'saldos_finales_acreedor':'{:,.2f}'.format(abs(balance)) if balance<0 else '',
				'balance_general_activo': '{:,.2f}'.format(abs(balance)) if account_id.balance_category=="balance" and balance>0 else '',
				'balance_general_pas_y_patr':'{:,.2f}'.format(abs(balance)) if account_id.balance_category=="balance" and balance<0 else '',
				'resultados_naturaleza_perdidas':'{:,.2f}'.format(abs(balance)) if account_id.balance_category in ["nature","function_nature"] and balance>0 else '',
				'resultados_naturaleza_ganancias':'{:,.2f}'.format(abs(balance)) if account_id.balance_category in ["nature","function_nature"] and balance<0 else '',
				'resultados_funcion_perdidas':'{:,.2f}'.format(abs(balance)) if account_id.balance_category in ["function","function_nature"] and balance>0 else '',
				'resultados_funcion_ganancias':'{:,.2f}'.format(abs(balance)) if account_id.balance_category in ["function","function_nature"] and balance<0 else '',
			}))
			saldo[0] += abs(balance_inicial)
			saldo[1] += abs(balance_inicial)
			saldo[2] += abs(line['debit_movimiento_periodo'] or 0.00)
			saldo[3] += abs(line['credit_movimiento_periodo'] or 0.00)
			saldo[4] += abs(balance) if balance>0 else 0.00
			saldo[5] += abs(balance) if balance<0 else 0.00
			saldo[6] += abs(balance) if account_id.balance_category=="balance" and balance>0 else 0.00
			saldo[7] += abs(balance) if account_id.balance_category=="balance" and balance<0 else 0.00
			saldo[8] += abs(balance) if account_id.balance_category in ["nature","function_nature"] and balance>0 else 0.00
			saldo[9] += abs(balance) if account_id.balance_category in ["nature","function_nature"] and balance<0 else 0.00
			saldo[10] += abs(balance) if account_id.balance_category in ["function","function_nature"] and balance>0 else 0.00
			saldo[11] += abs(balance) if account_id.balance_category in ["function","function_nature"] and balance<0 else 0.00

		registro.append((0,0,{
				'name_account':'SUMAS ',
				'saldos_iniciales_deudor':'{:,.2f}'.format(saldo[0]),
				'saldos_iniciales_acreedor':'{:,.2f}'.format(saldo[1]),
				'anio_fiscal_debe':'{:,.2f}'.format(saldo[2]),
				'anio_fiscal_haber':'{:,.2f}'.format(saldo[3]),
				'saldos_finales_deudor':'{:,.2f}'.format(saldo[4]),
				'saldos_finales_acreedor':'{:,.2f}'.format(saldo[5]),
				'balance_general_activo': '{:,.2f}'.format(saldo[6]),
				'balance_general_pas_y_patr':'{:,.2f}'.format(saldo[7]),
				'resultados_naturaleza_perdidas':'{:,.2f}'.format(saldo[8]),
				'resultados_naturaleza_ganancias':'{:,.2f}'.format(saldo[9]),
				'resultados_funcion_perdidas':'{:,.2f}'.format(saldo[10]),
				'resultados_funcion_ganancias':'{:,.2f}'.format(saldo[11]),
			}))
		
		resultado=[saldo[i-1]-saldo[i] for i in [1,3,5,7,9,11]]
		registro.append((0,0,{
				'name_account':'RESULTADO ',
				'saldos_iniciales_deudor':'{:,.2f}'.format(abs(resultado[0]) if resultado[0]>0 else 0.00),
				'saldos_iniciales_acreedor':'{:,.2f}'.format(abs(resultado[0]) if resultado[0]<=0 else 0.00),
				'anio_fiscal_debe':'{:,.2f}'.format(abs(resultado[1]) if resultado[1]>0 else 0.00),
				'anio_fiscal_haber':'{:,.2f}'.format(abs(resultado[1]) if resultado[1]<=0 else 0.00),
				'saldos_finales_deudor':'{:,.2f}'.format(abs(resultado[2]) if resultado[2]>0 else 0.00),
				'saldos_finales_acreedor':'{:,.2f}'.format(abs(resultado[2]) if resultado[2]<=0 else 0.00),
				'balance_general_activo': '{:,.2f}'.format(abs(resultado[3]) if resultado[3]<0 else 0.00),
				'balance_general_pas_y_patr':'{:,.2f}'.format(abs(resultado[3]) if resultado[3]>=0 else 0.00),
				'resultados_naturaleza_perdidas':'{:,.2f}'.format(abs(resultado[4]) if resultado[4]<0 else 0.00),
				'resultados_naturaleza_ganancias':'{:,.2f}'.format(abs(resultado[4]) if resultado[4]>=0 else 0.00),
				'resultados_funcion_perdidas':'{:,.2f}'.format(abs(resultado[5]) if resultado[5]<0 else 0.00),
				'resultados_funcion_ganancias':'{:,.2f}'.format(abs(resultado[5]) if resultado[5]>=0 else 0.00),
			}))

		registro.append((0,0,{
				'name_account':'TOTALES ',
				'saldos_iniciales_deudor':'0.00',
				'saldos_iniciales_acreedor':'0.00',
				'anio_fiscal_debe':'0.00',
				'anio_fiscal_haber':'0.00',
				'saldos_finales_deudor':'0.00',
				'saldos_finales_acreedor':'0.00',
				'balance_general_activo': '{:,.2f}'.format((abs(resultado[3]) if resultado[3]<0 else 0.00)+ saldo[6]),
				'balance_general_pas_y_patr':'{:,.2f}'.format((abs(resultado[3]) if resultado[3]>0 else 0.00)+ saldo[7]),
				'resultados_naturaleza_perdidas':'{:,.2f}'.format((abs(resultado[4]) if resultado[4]<0 else 0.00)+ saldo[8]),
				'resultados_naturaleza_ganancias':'{:,.2f}'.format((abs(resultado[4]) if resultado[4]>0 else 0.00)+ saldo[9]),
				'resultados_funcion_perdidas':'{:,.2f}'.format((abs(resultado[5]) if resultado[5]<0 else 0.00)+ saldo[10]),
				'resultados_funcion_ganancias':'{:,.2f}'.format((abs(resultado[5]) if resultado[5]>0 else 0.00)+ saldo[11]),
			}))
		

		self.report_amount_balances_ids=registro
