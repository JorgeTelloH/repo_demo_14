# -*- coding: utf-8 -*-
{
    'name': 'Documentos del Empleado',
    'summary': 'Administrar Documentos del Empleado',
    'description': """
    Administrar Documentos del Empleado
    """,
    'version': '1.0',
    'category': 'Human Resources/Employees',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['base', 'cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_document_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
