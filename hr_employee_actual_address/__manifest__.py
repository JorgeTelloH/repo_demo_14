# -*- coding: utf-8 -*-
{
    'name': "Dirección Actual de Empleado",
    'summary': """
        Agrega Direccion Actual del empleado
    """,
    'description': 
    """
        Agrega Dirección Actual y Dirección del Documento de Identidad del empleado.\n
        Esto se visualiza en:\n
        Empleados / Lengueta: Información Personal.
    """
    ,
    'author': "TH",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Human Resources/Employees',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'contacts', 'l10n_latam_base', 'l10n_pe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
    ],
}
