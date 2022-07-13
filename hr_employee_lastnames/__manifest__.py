# -*- encoding: utf-8 -*-
{
    "name": "HR Nombres, Apellido Paterno y Materno del Empleado",
    "summary": "Divide el Nombre del Empleado en Nombres, Apellido Paterno y Materno",
    "description": """
       Divide el Nombre del Empleado en Nombres, Apellido Paterno y Materno
    """,
    "version": "1.1",
    "author": "Vauxoo, Odoo Community Association (OCA), TH",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr_employee_firstname"],
    "data": ["views/hr_views.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
