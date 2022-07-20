# -*- encoding: utf-8 -*-
{
    'name': 'Familia del Empleado',
    'summary': 'Información de la familia del Empleado',
    'description': """
    Agrega información sobre la familia del Empleado
    """,
    'version': '1.0',
    'category': 'Human Resources/Employees',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['base', 'cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_employee_view.xml',
        'views/employee_family.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
