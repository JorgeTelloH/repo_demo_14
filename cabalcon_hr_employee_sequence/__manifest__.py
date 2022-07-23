# -*- coding: utf-8 -*-
{
    'name': 'Generar Código del Empleado',
    'summary': 'Autogenera Código del empleado',
    'description': """
    Autogenera el Código del Empleado con Prefijo y Secuencial.\n
    Configuración:\n
    - Ir al Módulo de Empleados / Configuracion: Código del Empleado
    """,
    'version': '1.1',
    'category': 'Human Resources/Employees',
    'author': "Cabalcon / TH",
    'website': "www.cabalcon.com",
    'depends': ['hr'],
    'data': [
        #'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
}
