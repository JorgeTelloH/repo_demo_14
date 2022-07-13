# -*- coding: utf-8 -*-
{
    'name': "Agregar atributos de conductor al personal",

    'summary': """
        Adiciona datos de conductor al personal""",

    'description': """
        Adiciona nuevos atributos de Conductor al personal: Datos de Conductor, si es de planta o externo, entre otros.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Human Resources',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
    ],

}
