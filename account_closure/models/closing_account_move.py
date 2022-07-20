# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
from itertools import *
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ClosingAccountMove(models.Model):
	_name = 'closing.account.move'
	_description = "Asiento Contable de Cierre"

	account_closure_id= fields.Many2one('account.closure',string="Cierre Contable", ondelete="cascade")
	account_move_line_ids = fields.One2many('closing.account.move.line','closing_account_move_id', string="Apuntes contables")

	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids])], readonly=True)

	date=fields.Date(string="Fecha Asiento", required=True)
	journal_id = fields.Many2one('account.journal',string="Diario", required=True)
	ref=fields.Char(string="Referencia", required=True)

	## cuenta de cierre contable y cuentas afectas
	closing_account_id=fields.Many2one('account.account', string="Cuenta de Cierre",required=True)
	relationship_between_accounts_id=fields.Many2one('relationship.between.accounts', string="Conjunto de Cuentas de Cierre",required=True)
	operation_type=fields.Char(string="Tipo de Operación",compute='_compute_campo_operation_type')
	affected_account_ids = fields.Many2many('account.account','account_account_closing_rel','account_id','closing_id',string="Cuentas Afectas",required=True)

	### ASIENTO CONTABLE GENERADO
	generated_account_move_id=fields.Many2one('account.move' , string="Asiento Contable Generado")

	#########################################################
	#################################################################

	name_relationship = fields.Char(string="Etiqueta", compute="compute_campo_name_relationship")
	exist_move_id = fields.Boolean(string="¿Existen Asiento Contable Generado?",compute='compute_exist_move_id')


	
	@api.depends('generated_account_move_id')
	def compute_exist_move_id(self):
		for rec in self:
			if rec.generated_account_move_id:
				rec.exist_move_id = True
			else:
				rec.exist_move_id = False


	
	def button_view_account_move(self):
		if self.exist_move_id:
			return {
				'name': 'Asiento Contable Generado',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.move',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in',[self.generated_account_move_id.id] or [])],
				'context': {
					'journal_id': self.journal_id.id,
				}
			}

	
	@api.depends('relationship_between_accounts_id')
	def compute_campo_name_relationship(self):
		for rec in self:
			if rec.relationship_between_accounts_id:
				rec.name_relationship=rec.relationship_between_accounts_id.name

	
	@api.depends('relationship_between_accounts_id')
	def _compute_campo_operation_type(self):
		for rec in self:
			if rec.relationship_between_accounts_id:
				rec.operation_type=rec.relationship_between_accounts_id.operation_type


	@api.onchange('closing_account_id')
	def onchange_relationship_between_accounts_id(self):
		for rec in self:
			if rec.closing_account_id:
				rec.relationship_between_accounts_id=self.env['relationship.between.accounts'].search([('closing_opening_account_id','=',rec.closing_account_id.id)],limit=1)




	@api.onchange('closing_account_id')
	def set_domain_for_relationship_between_accounts_id(self):
		for rec in self:
			records=[]
			if rec.closing_account_id:
				records=self.env['relationship.between.accounts'].search([('closing_opening_account_id','=',rec.closing_account_id.id),('company_id','=',rec.company_id.id)])
				res={}
				res['domain'] = {'relationship_between_accounts_id':[('id','in',[i.id for i in records])]}
				return res



	@api.onchange('closing_account_id','relationship_between_accounts_id')
	def onchange_campo_affected_account_ids(self):
		for rec in self:
			if rec.closing_account_id:
				if rec.relationship_between_accounts_id:
					rec.affected_account_ids=rec.relationship_between_accounts_id.mapped('affected_account_ids')
				else:
					rec.affected_account_ids=self.env['relationship.between.accounts'].search([('closing_opening_account_id','=',rec.closing_account_id.id)],limit=1).mapped('affected_account_ids')
			else:
				rec.affected_account_ids=None


	
	def get_query_balance_accounts(self,tuple_account_ids):
		# acac.code as code,
		query_accounts=""

		filter_clause = self.account_closure_id.get_filter_clause()

		if self.account_closure_id.type_closing_opening=='1':

			if self.operation_type =='closure':
				query_accounts="""select acac.id as id,sum(aml.balance) as balance,sum(aml.amount_currency) as amount_currency
					from account_move_line aml
					join account_account acac on aml.account_id = acac.id
					join account_move as am on am.id= aml.move_id where
					am.state='posted' and
					aml.date<='%s' and acac.id in %s group by acac.id order by acac.id""" % (self.date,
						str(tuple_account_ids) if len(tuple_account_ids)!=1 else str(tuple_account_ids)[0:len(str(tuple_account_ids))-2] + ')')
			
			elif self.operation_type == 'opening':
				query_accounts="""select acac.id as id,sum(aml.balance) as balance,sum(aml.amount_currency) as amount_currency
					from account_move_line aml
					join account_account acac on aml.account_id = acac.id
					join account_move as am on am.id= aml.move_id where
					am.state='posted' and
					aml.date<'%s' and acac.id in %s group by acac.id order by acac.id""" % (self.date,
						str(tuple_account_ids) if len(tuple_account_ids)!=1 else str(tuple_account_ids)[0:len(str(tuple_account_ids))-2] + ')')
		
		elif self.account_closure_id.type_closing_opening=='2':

			if self.operation_type =='closure':
				query_accounts="""select acac.id as id,sum(aml.balance) as balance,sum(aml.amount_currency) as amount_currency
					from account_move_line aml
					join account_account acac on aml.account_id = acac.id
					join account_move as am on am.id= aml.move_id where
					am.state='posted' and
					aml.date<='%s' and aml.date>='%s' and acac.id in %s 
					group by acac.id order by acac.id""" % (self.account_closure_id.date_to,self.account_closure_id.date_from,
						str(tuple_account_ids) if len(tuple_account_ids)!=1 else str(tuple_account_ids)[0:len(str(tuple_account_ids))-2] + ')')
			
			elif self.operation_type == 'opening':
				query_accounts="""select acac.id as id,sum(aml.balance) as balance,sum(aml.amount_currency) as amount_currency
					from account_move_line aml
					join account_account acac on aml.account_id = acac.id
					join account_move as am on am.id= aml.move_id where
					am.state='posted' and
					aml.date<='%s' and aml.date>='%s' and acac.id in %s 
					group by acac.id order by acac.id""" % (self.account_closure_id.date_to,self.account_closure_id.date_from,
						str(tuple_account_ids) if len(tuple_account_ids)!=1 else str(tuple_account_ids)[0:len(str(tuple_account_ids))-2] + ')')

		query_accounts += filter_clause

		self.env.cr.execute(query_accounts)
		records = self.env.cr.dictfetchall()
		return records


	
	def generate_accounting_entries(self,saldo_inicial_soles_cuenta_afecta=0.00,saldo_inicial_dolares_cuenta_afecta=0.00):
		self.account_move_line_ids.unlink()
		registro= []
		second_currency_id=self.env['res.currency'].search([('name','=','USD')],limit=1).id
		sum_total_saldo=0.00
		sum_total_saldo_currency=0.00
		if not len(self.affected_account_ids.ids or ''):
			raise UserError(_('NO SE COMPLETÓ EL PROCESO. LA CUENTA DE CIERRE %s NO TIENE ASOCIADA CUENTAS AFECTAS, CONFIGURE DICHA CUENTA !'%(self.closing_account_id.code)))

		# self.affected_account_ids=self.env['relationship.between.accounts'].search([('closing_account_id','=',self.closing_account_id.id)], limit=1).mapped('affected_account_ids.id')
		if self.operation_type=='opening':
			records = self.get_query_balance_accounts(tuple(self.affected_account_ids.ids))
			for line in records:
				registro.append((0,0,{'account_id':line['id'],
					
					'date':self.date,
					'date':self.date,
					'name':self.ref,
					'currency_id':second_currency_id,
					'amount_currency':line['amount_currency'],
					'saldo':-line['balance'],
					'saldo_currency':-line['amount_currency'],
					'debit':0.00 if line['balance']<0 else abs(line['balance']),
					'credit':0.00 if line['balance']>=0 else abs(line['balance']),
					'debit_currency':0.00 if line['amount_currency']<0 else abs(line['amount_currency']),
					'credit_currency':0.00 if line['amount_currency']>=0 else abs(line['amount_currency']),
					'account_closure_id':self.account_closure_id.id
				}))
				sum_total_saldo += line['balance']
				sum_total_saldo_currency += line['amount_currency']

		
		else:
			if len(tuple(self.affected_account_ids.ids))==1 and saldo_inicial_soles_cuenta_afecta :
				registro.append((0,0,{'account_id':self.affected_account_ids[0].id,
					
					'date':self.date,
					'date':self.date,
					'name':self.ref,
					'currency_id':second_currency_id,
					'amount_currency':-saldo_inicial_dolares_cuenta_afecta,
					'saldo':saldo_inicial_soles_cuenta_afecta,
					'saldo_currency':saldo_inicial_dolares_cuenta_afecta,
					'debit':abs(saldo_inicial_soles_cuenta_afecta) if saldo_inicial_soles_cuenta_afecta<0 else 0.00,
					'credit':abs(saldo_inicial_soles_cuenta_afecta) if saldo_inicial_soles_cuenta_afecta>=0 else 0.00,
					'debit_currency':abs(saldo_inicial_dolares_cuenta_afecta) if saldo_inicial_dolares_cuenta_afecta<0 else 0.00,
					'credit_currency':abs(saldo_inicial_dolares_cuenta_afecta) if saldo_inicial_dolares_cuenta_afecta>=0 else 0.00,
					'account_closure_id':self.account_closure_id.id
				}))
				sum_total_saldo += saldo_inicial_soles_cuenta_afecta
				sum_total_saldo_currency += saldo_inicial_dolares_cuenta_afecta
			else:
				records = self.get_query_balance_accounts(tuple(self.affected_account_ids.ids))
				for line in records:
					registro.append((0,0,{'account_id':line['id'],
						
						'date':self.date,
						'date':self.date,
						'name':self.ref,
						'currency_id':second_currency_id,
						'amount_currency':-line['amount_currency'],
						'saldo':line['balance'],
						'saldo_currency':line['amount_currency'],
						'debit':0.00 if line['balance']>=0 else abs(line['balance']),
						'credit':0.00 if line['balance']<0 else abs(line['balance']),
						'debit_currency':0.00 if line['amount_currency']>=0 else abs(line['amount_currency']),
						'credit_currency':0.00 if line['amount_currency']<0 else abs(line['amount_currency']),
						'account_closure_id':self.account_closure_id.id
					}))
					sum_total_saldo += line['balance']
					sum_total_saldo_currency += line['amount_currency']

		if self.operation_type == 'closure':
			registro.append((0,0,{'account_id':self.closing_account_id.id,
				
				'date':self.date,
				'date':self.date,
				'name':self.ref,
				'currency_id':second_currency_id,
				'amount_currency':sum_total_saldo_currency,
				'saldo':-sum_total_saldo,
				'saldo_currency':-sum_total_saldo_currency,
				'debit':0.00 if sum_total_saldo<0 else abs(sum_total_saldo),
				'credit':0.00 if sum_total_saldo>=0 else abs(sum_total_saldo),
				'debit_currency':0.00 if sum_total_saldo_currency<0 else abs(sum_total_saldo_currency),
				'credit_currency':0.00 if sum_total_saldo_currency>=0 else abs(sum_total_saldo_currency),
				'account_closure_id':self.account_closure_id.id
			}))
		else:
			registro.append((0, 0, {'account_id': self.closing_account_id.id,
				'date': self.date,
				'date':self.date,
				'name': self.ref,
				'currency_id': second_currency_id,
				'amount_currency': sum_total_saldo_currency,
				'saldo': -sum_total_saldo,
				'saldo_currency': -sum_total_saldo_currency,
				'debit': 0.00 if sum_total_saldo >= 0 else abs(sum_total_saldo),
				'credit': 0.00 if sum_total_saldo < 0 else abs(sum_total_saldo),
				'debit_currency': 0.00 if sum_total_saldo_currency < 0 else abs(sum_total_saldo_currency),
				'credit_currency': 0.00 if sum_total_saldo_currency >= 0 else abs(sum_total_saldo_currency),
				'account_closure_id': self.account_closure_id.id}))
		
		self.account_move_line_ids = registro
		return sum_total_saldo,sum_total_saldo_currency


	def update_amount_residual_zero(self,move_id):
		string_update="""UPDATE account_move_line SET amount_residual=0.00 , amount_residual_currency=0.00 where move_id=%s"""%(move_id)
		self.env.cr.execute(string_update)

	
	def update_account_period_fiscal_year(self):

		query_account_period= """select id from account_period where code='%s/%s' and special=true"""%(
				'00' if self.operation_type=='opening' else '13',self.date.split('-')[0])

		self.env.cr.execute(query_account_period)
		id_account_period_init=self.env.cr.dictfetchall()
		id_account_period=[]

		if len(id_account_period_init or ''):
			id_account_period = id_account_period_init[0]['id']

		if id_account_period:
			self.env.cr.execute("""update account_move_line set period_id=%s where move_id=%s"""%(
				id_account_period,
				self.generated_account_move_id.id))


			self.env.cr.execute("""update account_move set period_id=%s where id=%s""" % (
				id_account_period,
				self.generated_account_move_id.id))



	
	def post(self):
		self.generated_account_move_id = self.env['account.move'].create({'date':self.date,'date':self.date,'ref':self.ref,'journal_id':self.journal_id.id})#,'branch_id':self.branch_id.id})
		new_account_move_line = self.env['account.move.line'].with_context(check_move_validity=False)

		for line in self.account_move_line_ids:
			#has_distribution=line.account_id.has_distribution
			#line.account_id.write({'has_distribution':False})

			apunte_contrapartida_conciliacion = new_account_move_line.create({
				'move_id':self.generated_account_move_id.id,
				'account_id':line.account_id.id,
				#'branch_id':line.branch_id.id ,
				'name':line.name or '',
				'date':line.date,
				# 'currency_id':line.currency_id.id or line.account_id.currency_id.id,
				# 'amount_currency':-line.amount_currency,
				# 'amount_currency':0.00,
				# 'amount_residual':0.00,
				# 'amount_residual_currency':0.00,
				'debit': line.debit,
				'credit': line.credit,
				'analytic_tag_ids':None
			})
			# apunte_contrapartida_conciliacion.write({'has_distribution':has_distribution})
			#line.account_id.write({'has_distribution':has_distribution})
		self.generated_account_move_id.post()

		self.update_amount_residual_zero(self.generated_account_move_id.id)
		self.update_account_period_fiscal_year()


	# self.env.cr.execute("UPDATE account_payment_detail SET account_id = " + str(invoice_id.account_id.id) + " WHERE id = " + str(line.id))

	


