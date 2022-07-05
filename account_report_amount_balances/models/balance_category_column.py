# -*- coding: utf-8 -*-
import logging
# import pprint
from odoo import models, fields, api
from odoo.tools import email_split, float_is_zero
from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class BalanceCategoryColumn(models.Model):
	_name = "balance.category.column"
	_description = "Modulo para columnas de Categoría de Balance en Sumas y Saldos"

	name = fields.Char(string="Nombre de Categoría de Balance", required=True)
	code= fields.Char(string="Código de Categoría", required=True)

	_sql_constraints = [
		('code', 'unique(code)',  'Este código para la categoría definida ya existe , revise sus registros creados!'),
	]