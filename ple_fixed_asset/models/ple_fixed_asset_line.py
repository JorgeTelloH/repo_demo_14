
import pytz
import calendar
import base64
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime, timedelta
from odoo.addons import ple_base as tools

import logging
_logger=logging.getLogger(__name__)

class PleFixedAssetLine(models.Model):
	_name='ple.fixed.asset.line'


	ple_fixed_asset_id=fields.Many2one('ple.fixed.asset',string="ID PLE ACTIVOS FIJOS", ondelete="cascade", readonly=True  )
	move_id=fields.Many2one('account.move', string="Asiento Contable" , readonly=True )
	account_id=fields.Many2one('account.account' , string="Cuenta" , readonly=True )
	account_asset_id=fields.Many2one('account.asset.asset' , string="Activo Fijo", readonly=True)
	periodo=fields.Char(string="Periodo PLE") ### ESTO CORRESPONDE AL MES DE LA CREACIÓN DEL PLE !!!
	periodo_apunte=fields.Char(string="Periodo del apunte contable", compute='_compute_campo_periodo_apunte' , store=True , readonly=True ) ### ESTO CORRESPONDE AL MES DE LA CREACIÓN DEL PLE !!!
	asiento_contable = fields.Char(string="Nombre del asiento contable", compute='_compute_campo_asiento_contable' , store=True , readonly=True) #############################
	m_correlativo_asiento_contable=fields.Char(string="M-correlativo asiento contable" ,compute='_compute_campo_m_correlativo_asiento_contable' ,store=True , readonly=True )#

	codigo_catalogo_utilizado=fields.Char(string="Código catálogo Utilizado" ,compute='_compute_campo_codigo_catalogo_utilizado' , store=True , readonly=True)
	codigo_propio_activo=fields.Char(string="Código propio Activo Fijo" , compute='_compute_campo_codigo_propio_activo' , store=True , readonly=True)
	
	codigo_catalogo_utilizado_UNSPSC_GTIN=fields.Char(string="Código catálogo (No acepta valor 9)" ,compute='_compute_campo_codigo_catalogo_utilizado_UNSPSC_GTIN' , store=True , readonly=True)
	codigo_existencia_UNSPSC_GTIN=fields.Char(string="Código de existencia Catálogo Anterior", default='',compute='_compute_campo_codigo_existencia_UNSPSC_GTIN', readonly=True)

	codigo_tipo_activo_fijo=fields.Char(string="Código tipo Activo Fijo" , compute='_compute_campo_codigo_tipo_activo_fijo', store=True,readonly=True)
	
	codigo_cuenta_desagregado=fields.Char(string="Código cuenta contable desagregado" , compute='_compute_campo_codigo_cuenta_desagregado' , store=True ,readonly=True)
	estado_activo_fijo=fields.Char(string="Estado Activo Fijo" , compute='_compute_campo_estado_activo_fijo' , store=True , readonly=True)
	descripcion_activo_fijo=fields.Char(string="Descripción Activo Fijo" , compute='_compute_campo_descripcion_activo_fijo' , store=True , readonly=True)
	marca_activo_fijo=fields.Char(string="Marca Activo Fijo" , compute='_compute_campo_marca_activo_fijo' , store=True , readonly=True)
	modelo_activo_fijo=fields.Char(string="Modelo Activo Fijo" , compute='_compute_campo_modelo_activo_fijo' , store=True , readonly=True)
	numero_serie_placa_activo=fields.Char(string="Número de serie/Placa Activo Fijo" , compute='_compute_campo_numero_serie_placa_activo', store=True , readonly=True)
	importe_saldo_inicial_activo_fijo=fields.Float(string="Importe Saldo Inicial" , compute='_compute_campo_importe_saldo_inicial_activo_fijo', store=True , readonly=True)
	importe_adquisiciones_adiciones=fields.Float(string="Importe Adquisiciones o Adiciones" , compute='_compute_campo_importe_adquisiciones_adiciones',store=True , readonly=True)
	importe_mejoras=fields.Float(string="Importe Mejoras" , compute='_compute_campo_importe_mejoras',store=True , readonly=True)
	importe_retiros_bajas=fields.Float(string="Importe Retiros y/o Bajas" , compute='_compute_campo_importe_retiros_bajas',store=True , readonly=True)
	importe_otros_ajustes=fields.Float(string="Importe Otros Ajustes" , compute='_compute_campo_importe_otros_ajustes',store=True , readonly=True)
	valor_revaluacion_voluntaria_efectuada=fields.Float(string="Valor de Revaluación Voluntaria efectuada" , compute='_compute_campo_valor_revaluacion_voluntaria_efectuada',store=True , readonly=True)
	valor_revaluación_efectuada_reorganizacion_sociedades=fields.Float(string="Valor de Revaluación Voluntaria efectuada" , compute='_compute_campo_valor_revaluacion_efectuada_reorganizacion_sociedades',store=True , readonly=True)
	valor_otras_revaluaciones_efectuadas=fields.Float(string="Valor de Revaluacion Voluntaria efectuada" , compute='_compute_campo_valor_otras_revaluaciones_efectuadas',store=True , readonly=True)
	importe_valor_ajuste_por_inflacion=fields.Float(string="Importe Valor del Ajuste por Inflacion" , compute='_compute_campo_importe_valor_ajuste_por_inflacion',store=True , readonly=True)
	fecha_adquisicion_activo=fields.Date(string="Fecha Adquisicion Activo Fijo" , compute='_compute_campo_fecha_adquisicion_activo',store=True , readonly=True)
	fecha_inicio_uso_activo_fijo=fields.Date(string="Fecha Inicio de Uso del Activo Fijo" , compute='_compute_campo_fecha_inicio_uso_activo_fijo',store=True , readonly=True)
	codigo_metodo_aplicado_calculo_depreciacion=fields.Char(string="Codigo del Método aplicado en Cálculo Depreciacion" , compute='_compute_campo_codigo_metodo_aplicado_calculo_depreciacion',store=True , readonly=True)
	numero_documento_cambio_metodo_depreciacion=fields.Char(string="Nº Documento de autorizacion para cambiar Método Depreciacion" , compute='_compute_campo_numero_documento_cambio_metodo_depreciacion',store=True , readonly=True)
	porcentaje_depreciacion=fields.Float(string="Porcentaje de Depreciacion" , compute='_compute_campo_porcentaje_depreciacion',store=True , readonly=True)
	depreciacion_acumulada_cierre_ejercicio_anterior=fields.Float(string="Depreciacion Acumulada al cierre Ejercicio Anterior" , compute='_compute_campo_depreciacion_acumulada_cierre_ejercicio_anterior',store=True , readonly=True)
	valor_depreciacion_ejercicio_sin_considerar_revaluacion=fields.Float(string="Valor Depreciacion ejercicio sin considerar revaluacion" , compute='_compute_campo_valor_depreciacion_ejercicio_sin_considerar_revaluacion',store=True , readonly=True)
	valor_depreciacion_ejercicio_relacionada_con_retiros_bajas=fields.Float(string="Valor Depreciacion Ejercicio Relacionada con retiros y/o bajas" , compute='_compute_campo_valor_depreciacion_ejercicio_relacionada_con_retiros_bajas',store=True , readonly=True)
	valor_depreciacion_relacionada_con_otros_ajustes=fields.Float(string="Valor Depreciacion Relacionada con Otros Ajustes" , compute='_compute_campo_valor_depreciacion_relacionada_con_otros_ajustes',store=True , readonly=True)
	valor_depre_revaluacion_voluntaria_efectuada=fields.Float(string="Valor de la Depreciación de la Revaluación Voluntaria efectuada" , compute='_compute_campo_valor_depre_revaluacion_voluntaria_efectuada',store=True , readonly=True)
	valor_depreci_de_revaluaci_efectuada_reorgani_soci=fields.Float(string="Valor Depreciacion de Revaluacion efectuada por Reorganizacion de Sociedades" , compute='_compute_campo_valor_depreci_de_revaluaci_efectuada_reorgani_soci',store=True , readonly=True)
	valor_depreciacion_otras_revaluaciones_efectuadas=fields.Float(string="Valor Depreciacion de otras Revaluaciones Efectuadas" , compute='_compute_campo_valor_depreciacion_otras_revaluaciones_efectuadas',store=True , readonly=True)
	valor_ajuste_por_inflacion_de_depreciacion=fields.Float(string="Valor Ajuste por inflacion de Depreciacion" , compute='_compute_campo_Valor_ajuste_por_inflacion_de_depreciacion',store=True , readonly=True)
	estado_operacion=fields.Char(string="Estado de la operacion" , compute='_compute_campo_estado_operacion',store=True , readonly=True)




	@api.depends('move_id')
	def _compute_campo_periodo_apunte(self):
		for rec in self:
			if rec.move_id.date:
				#[anio,mes,dia]=rec.move_id.date.split('-')
				anio = rec.move_id.date.strftime("%Y")
				mes = rec.move_id.date.strftime("%m")
				#mes=(rec.move_id.date.month or '')
				rec.periodo_apunte = "%s%s00" % (anio or 'YYYY', ('0' + str(mes) if int(mes)<10 else str(mes)) or 'MM')
			# rec.periodo_apunte=
			else:
				rec.periodo_apunte = ""



	@api.depends('move_id')
	def _compute_campo_asiento_contable(self):
		for rec in self:
			rec.asiento_contable =rec.move_id.name



	@api.depends('move_id')
	def _compute_campo_m_correlativo_asiento_contable(self):
		for rec in self:
			rec.m_correlativo_asiento_contable = "M1"



	@api.depends('account_asset_id')
	def _compute_campo_codigo_catalogo_existencias_utilizado(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_catalogo_existencias_utilizado = rec.account_asset_id.asset_encoding_type_sunat or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_propio_activo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_propio_activo = rec.account_asset_id.asset_code or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_catalogo_utilizado_UNSPSC_GTIN(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_catalogo_utilizado_UNSPSC_GTIN=rec.account_asset_id.codigo_catalogo_utilizado_UNSPSC_GTIN or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_existencia_UNSPSC_GTIN(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_existencia_UNSPSC_GTIN = rec.account_asset_id.codigo_existencia_UNSPSC_GTIN or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_tipo_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_tipo_activo_fijo = rec.account_asset_id.fixed_asset_type_code_sunat or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_cuenta_desagregado(self):
		for rec in self:
			if rec.account_asset_id:
				rec.codigo_cuenta_desagregado=rec.account_id.code or ''


	# 1 ACTIVOS EN DESUSO
	# 2 ACTIVOS OBSOLETOS
	# 9 RESTO DE ACTIVOS


	@api.depends('account_asset_id')
	def _compute_campo_estado_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.estado_activo_fijo= '9' if rec.account_asset_id.state=='open' else '2' if rec.account_asset_id.state=='close' else '1'



	@api.depends('account_asset_id')
	def _compute_campo_descripcion_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.descripcion_activo_fijo=rec.account_asset_id.name or ''



	@api.depends('account_asset_id')
	def _compute_campo_marca_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.marca_activo_fijo=rec.account_asset_id.brand_id.name or ''



	@api.depends('account_asset_id')
	def _compute_campo_modelo_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.modelo_activo_fijo=rec.account_asset_id.model_id.name or ''



	@api.depends('account_asset_id')
	def _compute_campo_numero_serie_placa_activo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.numero_serie_placa_activo=rec.account_asset_id.serial_number_plate or ''



	@api.depends('account_asset_id')
	def _compute_campo_importe_saldo_inicial_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_saldo_inicial_activo_fijo = rec.account_asset_id.value - rec.account_asset_id.salvage_value



	@api.depends('account_asset_id')
	def _compute_campo_importe_adquisiciones_adiciones(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_adquisiciones_adiciones = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_importe_mejoras(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_mejoras = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_importe_retiros_bajas(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_retiros_bajas = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_importe_otros_ajustes(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_otros_ajustes = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_valor_revaluacion_voluntaria_efectuada(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_revaluacion_voluntaria_efectuada = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_valor_revaluación_efectuada_reorganizacion_sociedades(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_revaluación_efectuada_reorganizacion_sociedades = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_valor_otras_revaluaciones_efectuadas(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_otras_revaluaciones_efectuadas=0.0



	@api.depends('account_asset_id')
	def _compute_campo_importe_valor_ajuste_por_inflacion(self):
		for rec in self:
			if rec.account_asset_id:
				rec.importe_valor_ajuste_por_inflacion = 0.0



	@api.depends('account_asset_id')
	def _compute_campo_fecha_adquisicion_activo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.fecha_adquisicion_activo=rec.account_asset_id.date or ''



	@api.depends('account_asset_id')
	def _compute_campo_fecha_inicio_uso_activo_fijo(self):
		for rec in self:
			if rec.account_asset_id:
				rec.fecha_inicio_uso_activo_fijo=rec.account_asset_id.first_depreciation_manual_date or ''



	@api.depends('account_asset_id')
	def _compute_campo_codigo_metodo_aplicado_calculo_depreciacion(self):
		for rec in self:
			if rec.account_asset_id:
				if rec.account_asset_id.category_id:
					metodo=rec.account_asset_id.category_id.method
					if metodo=='linear':
						rec.codigo_metodo_aplicado_calculo_depreciacion= '1'
					else:
						rec.codigo_metodo_aplicado_calculo_depreciacion= '9'



	@api.depends('account_asset_id')
	def _compute_campo_numero_documento_cambio_metodo_depreciacion(self):
		for rec in self:
			if rec.account_asset_id:
				rec.numero_documento_cambio_metodo_depreciacion=rec.account_asset_id.document_number_for_depreciation_method_change or ''



	@api.depends('account_asset_id')
	def _compute_campo_porcentaje_depreciacion(self):
		for rec in self:
			if rec.account_asset_id:
				rec.porcentaje_depreciacion=rec.account_asset_id.method_progress_factor*100.00



	@api.depends('account_asset_id')
	def _compute_campo_depreciacion_acumulada_cierre_ejercicio_anterior(self):
		for rec in self:
			if rec.account_asset_id:
				rec.depreciacion_acumulada_cierre_ejercicio_anterior=sum(rec.account_asset_id.depreciation_line_ids.filtered(lambda r:r.depreciation_date.strftime("%Y%m%d") < rec.periodo).mapped('amount'))


	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_ejercicio_sin_considerar_revaluacion(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depreciacion_ejercicio_sin_considerar_revaluacion=sum([line.amount for line in rec.account_asset_id.depreciation_line_ids if line.depreciation_date.strftime("%Y-%m-%d")[:4]==rec.periodo[:4]])



	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_ejercicio_relacionada_con_retiros_bajas(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depreciacion_ejercicio_relacionada_con_retiros_bajas=0.00



	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_relacionada_con_otros_ajustes(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depreciacion_relacionada_con_otros_ajustes=0.0


	@api.depends('account_asset_id')
	def _compute_campo_valor_depre_revaluacion_voluntaria_efectuada(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depre_revaluacion_voluntaria_efectuada = 0.00



	@api.depends('account_asset_id')
	def _compute_campo_valor_depreci_de_revaluaci_efectuada_reorgani_soci(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depreci_de_revaluaci_efectuada_reorgani_soci=0.0



	@api.depends('account_asset_id')
	def _compute_campo_valor_depreciacion_otras_revaluaciones_efectuadas(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_depreciacion_otras_revaluaciones_efectuadas=0.0



	@api.depends('account_asset_id')
	def _compute_campo_valor_ajuste_por_inflacion_de_depreciacion(self):
		for rec in self:
			if rec.account_asset_id:
				rec.valor_ajuste_por_inflacion_de_depreciacion=0.0



	@api.depends('account_asset_id')
	def _compute_campo_estado_operacion(self):
		## 1 8 9
		for rec in self:
			if rec.account_asset_id:
				rec.estado_operacion='1'
		#self.estado_operacion='1' if (self.periodo==self.periodo_apunte and self.account_asset_id.declared_ple==False) else '8' if (self.periodo > self.periodo_apunte and self.account_asset_id.declared_ple==False) else '9' if (self.periodo > self.periodo_apunte and self.account_asset_id.declared_ple==True) else ''

