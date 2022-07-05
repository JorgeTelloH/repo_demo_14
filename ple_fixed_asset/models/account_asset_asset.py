import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

class AccountAssetAsset(models.Model):
	_inherit='account.asset.asset'
	
	brand_id=fields.Many2one('asset.asset.brand',string="Marca del Activo")
	model_id=fields.Many2one('asset.asset.model',string="Modelo del Activo")
	serial_number_plate=fields.Char(string="Número de serie/placa")
	asset_encoding_type_sunat=fields.Selection(selection=[('1','NACIONES UNIDAS'),('3','GS1 (EAN-UCC)'),('9','OTROS')], string="Código Catálogo utilizado")
	asset_code=fields.Char(string="Código propio del Activo")

	######################################################
	codigo_catalogo_utilizado_UNSPSC_GTIN=fields.Selection(selection=[('1','NACIONES UNIDAS-UNSPSC'),('3','GS1 (EAN-UCC)')], string="Código Catálogo comprobante de Pago")
	codigo_existencia_UNSPSC_GTIN=fields.Char(string="Código de Existencia UNIDAS-UNSPSC")
	#####################################################
	
	fixed_asset_type_code_sunat=fields.Selection(string="Tipo de Activo Fijo", selection=[('1','NO REVALUADO O REVALUADO SIN EFECTO TRIBUTARIO'),('2','REVALUADO CON EFECTO TRIBUTARIO')], required=True)

	document_number_for_depreciation_method_change=fields.Char(string="Número de Documento de autorización para cambio de método de depreciación")
	
	declared_ple=fields.Boolean(string="Registro Declarado")