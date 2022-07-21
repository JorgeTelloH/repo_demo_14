# -*- coding: utf-8 -*-
from odoo import models, fields, _, api

class HrStudyCenter(models.Model):
    _name = 'hr.study.center'
    _description = 'Centro de Estudios'

    name = fields.Char(string='Institución Educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)
