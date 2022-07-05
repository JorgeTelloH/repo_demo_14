# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	declared_ple_0701_0704 = fields.Boolean(string="Registro declarado en PLE 07.01-07.04")
	### CAMPO PARA EVITAR QUE LAS FACTURAS O BOLETAS DECLARADAS EN EL PLE SEAN ELIMINADAS

	#habilitar dichos metodos, son muy necesarios
	# @api.multi
	# def unlink (self):
	# 	for line in self:
	# 		if line.declared_ple==True:
	# 			raise UserError(_('ESTO(S) APUNTES(S) CONTABLE(S) NO SE PUEDE(N) ELIMINAR , YA SE ENCUENTRA(N) DECLARADO(S) EN SU PLE RESPECTIVO !!!'))
	# 		else:
	# 			return super(AccountMoveLine,self).unlink()


	# @api.multi
	# def button_cancel(self):
	# 	if self.declared_ple == True:
	# 		raise UserError(_('ESTE ASIENTO NO SE PUEDE CANCELAR , YA SE ENCUENTRA DECLARADA EN SU PLE RESPECTIVO !!!'))
	# 	else:
	# 		return super(AccountMove,self).button_cancel()
	


	# @api.one
	# def write(self,object):
	# 	# for line in self:	
	# 	if self.declared_ple == True:
	# 		raise UserError(_('ESTE APUNTE NO SE PUEDE EDITAR , YA SE ENCUENTRA DECLARADO EN SU PLE RESPECTIVO !!!'))
	# 	else :
	# 		return super(AccountMoveLine,self).write(object)


