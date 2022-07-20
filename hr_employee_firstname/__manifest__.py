# -*- coding: utf-8 -*-
{
    "name": "HR Nombres y Apellidos del Empleado",
    "summary": "Agrega Nombre al Empleado",
    "description": """
       Agrega Nombre al Empleado
    """,
    "version": "1.1",
    "author": "Savoir-faire Linux, Fekete Mihai (Forest and Biomass Services Romania), "
    "Onestein, Odoo Community Association (OCA), TH",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr"],
    "data": [
       "views/hr_view.xml", 
       "views/base_config_view.xml"
       ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
