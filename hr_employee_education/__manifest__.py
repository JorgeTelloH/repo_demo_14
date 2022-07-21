# -*- coding: utf-8 -*-
{
    'name': 'Estudios del Empleado',
    'summary': 'Información de Estudios del Empleado',
    'description': """
    Agrega información sobre Estudios del Empleado
    """,
    'version': '1.0',
    'category': 'Human Resources/Employees',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['base', 'cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_employee_education_view.xml',
        'views/hr_study_center_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
