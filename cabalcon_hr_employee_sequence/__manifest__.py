# -*- coding: utf-8 -*-
{
    'name': 'Generar código del Empleado',
    'summary': 'Autogenera código del empleado',
    'description': """
    Autogenera el Código del Empleado con Prefijo y Secuencial.\n
    Configuración:\n
    - Ir al Módulo de Empleados / Configuracion: Código del Empleado
    """,
    'version': '1.0',
    'category': 'Human Resources/Employees',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': ['cabalcon_hr'],
    'data': [
        #'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
}
