# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, _):
    # Esta instrucción SQL es necesaria para llamar a _install_employee_lastnames()
    # con ello establecer campos de nombre correctamente.
    #
	# Después de la instalación, previamente instalada la dependencia hr_employee_firstname
    # el cual divide el nombre en dos partes: Nombres y Apellidos, así que para este
    # módulo para poder procesar el nuevo campo lastmane2 es necesario
    # restablecer los valores a vacío para poder configurar correctamente los tres campos
    # (Nombres, Apellido paterno y Apellido materno).
    # Por ejemplo:
    #  Después de instalar hr_employee_fisrtname y antes de instalar hr_employee_lastnames:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson Clinton'
    #
    #  Después de instalar hr_employee_lastnames:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson'
    #     lastname2 = 'Clinton'
    cr.execute("UPDATE hr_employee SET firstname = NULL, lastname = NULL")
    env = Environment(cr, SUPERUSER_ID, {})
    env["hr.employee"]._install_employee_lastnames()
    env["ir.config_parameter"].sudo().set_param("employee_names_order", "first_last")
