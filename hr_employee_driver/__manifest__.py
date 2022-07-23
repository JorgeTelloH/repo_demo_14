# -*- coding: utf-8 -*-
{
    'name': "Conductores en Empleados",
    'summary': """
        Agrega Datos de Conductor en Empleados""",

    'description': """
        Agrega Datos de Conductor en Empleados:
        - Licencias de Conducir
        - Activar a Empleado como Conductor
        - SOAT
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Human Resources/Employees',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_type_driver_license_view.xml',
        'data/data_type_driver_license.xml',
    ],

}
