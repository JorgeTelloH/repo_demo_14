from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AccountInvoiceReconcilePayment(models.TransientModel):
	_name = 'account.invoice.reconcile.payment'
	_description = "Conciliación de Facturas Abiertas con Pagos posteados"
	
	criterios=fields.Boolean(string="Búsqueda por criterios",default=False)

	type_invoice=fields.Selection(selection=[('in_invoice','Facturas Proveedor'),('out_invoice','Facturas Cliente'),('all','Todas')])

	date_from=fields.Date(string="Fecha Desde")
	date_to=fields.Date(string="Fecha Hasta")

	currency_id=fields.Many2one('res.currency',string="Moneda de factura")

	partner_ids = fields.Many2many('res.partner','invoice_reconcile_payment_partner_rel','partner_id','payment_id' ,string="Socios")

	facturas_directas=fields.Boolean(string="Selección Directa de Facturas")

	invoice_ids=fields.Many2many('account.move','invoice_reconcile_payment_rel','invoice_id','payment_id',
		string="Facturas a pagar/cobrar",
		domain="[('amount_residual', '!=',0.00),('move_type','in',['in_invoice','out_invoice']),('state','=','posted')]")
		#,'in_refund','out_refund'])]")


	@api.onchange('criterios','facturas_directas')
	def onchange_criterios(self):
		for rec in self:
			if rec.criterios:
				rec.facturas_directas=False
			else:
				rec.facturas_directas=True


	@api.onchange('criterios','facturas_directas')
	def onchange_facturas_directas(self):
		for rec in self:
			if rec.facturas_directas:
				rec.criterios=False
			else:
				rec.criterios=True


	def payment_invoice_massive(self):
		cadena_busqueda=[]
		records=[]
		if self.criterios:

			if len(self.invoice_ids or ''):
				cadena_busqueda.append(('id','in',[i.id for i in self.invoice_ids]))

			if len(self.partner_ids or ''):
				cadena_busqueda.append(('partner_id','in',[i.id for i in self.partner_ids]))
			if self.date_from:
				cadena_busqueda.append(('date','>=',self.date_from))
			if self.date_to:
				cadena_busqueda.append(('date','<=',self.date_to))
			if self.currency_id:
				cadena_busqueda.append(('currency_id','in',[self.currency_id.id]))

			if self.type_invoice=='in_invoice':
				cadena_busqueda.append(('move_type','in',['in_invoice']))
			elif self.type_invoice=='out_invoice':
				cadena_busqueda.append(('move_type','in',['out_invoice']))
			elif self.type_invoice=='all':
				cadena_busqueda.append(('move_type','in',['out_invoice','in_invoice']))

			cadena_busqueda.append(('state','in',['posted']))
			cadena_busqueda.append(('amount_residual','!=',0.00))

			records= self.env['account.move'].search(cadena_busqueda)

		elif self.facturas_directas:
			if len(self.invoice_ids or ''):
				cadena_busqueda.append(('id','in',[i.id for i in self.invoice_ids]))

			records= self.env['account.move'].search(cadena_busqueda)

		if not(records or ''):
			raise UserError(_('NO SE ENCONTRARON FACTURAS QUE CUMPLAN LAS CONDICIONES INDICADAS !!'))

		self.payment_massive(records)


	def payment_invoice(self,invoice_id):

		if invoice_id:

			aml_id = ''

			if invoice_id.move_type in ['in_invoice']:
				aml_id = invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('payable'))

			elif invoice_id.move_type in ['out_invoice']:
				aml_id = invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable'))

			
			account_id = ''

			if aml_id:
				account_id = aml_id[0].account_id

			domain=[('ref','=',invoice_id.name),('state', '=', 'posted'),('destination_account_id','=',account_id.id)]

			if invoice_id.move_type in ['in_invoice']:
				domain.append(('payment_type','in',['outbound']))

			elif invoice_id.move_type in ['out_invoice']:
				domain.append(('payment_type','in',['inbound']))

			payment_id = self.env['account.payment'].search(domain)

			if payment_id:

				payment_move_line_id = payment_id[0].mapped('move_id.line_ids').filtered(lambda t:t.account_id == account_id)
				invoice_move_line_id = aml_id
				if payment_move_line_id:
					(payment_move_line_id + invoice_move_line_id).reconcile()



	def payment_massive(self,invoice_ids):
		if invoice_ids:
			for invoice_id in invoice_ids:
				self.payment_invoice(invoice_id)