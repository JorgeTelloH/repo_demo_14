# -*- coding: utf-8 -*-
from odoo import models, fields, _, api

class HrStudyCenter(models.Model):
    _name = 'hr.study.center'
    _description = 'Centro de Estudios'

    name = fields.Char(string='Institución Educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

class HrEmployeeEducation(models.Model):
    _name = "hr.employee.education"
    _description = "Estudios del Empleado"

    employee_id = fields.Many2one('hr.employee', string="Empleado", invisible=1)
    name = fields.Char(string='Profesión/Especialidad', required=True)
    study_level = fields.Selection([
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('tecnico', 'Técnico'),
        ('universitario', 'Universitario'),
        ('bachiller', 'Bachiller'),
        ('titulado', 'Titulado'),
        ('especializacion', 'Especialización'),
        ('diplomado', 'Diplomado'),
        ('curso', 'Curso'),
        ('maestria', 'Maestria'),
        ('Doctorado', 'Doctorado')
        ], string='Nivel de Estudio', required=True)
	study_center_id = fields.Many2one('hr.study.center', string="Centro de Estudios")
	study_situation_id = fields.Many2one('hr.educational.situation', string="Situación de Estudios")
	start_date = fields.Date(string="Fecha Inicio", tracking=True)
	finish_date = fields.Date(string="Fecha Fin", tracking=True)

    #Solo en caso sea Primaria o Secundaria
    @api.onchange('study_level')
    def _onchange_study_level(self):
        if self.study_level and self.study_level in ('primaria','secundaria'):
            self.name = self.study_level.title()

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    education_ids = fields.One2many('hr.employee.education', 'employee_id', string='Educación', help='Información de Estudios del Empleado')

