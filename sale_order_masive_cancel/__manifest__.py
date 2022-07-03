# -*- coding: utf-8 -*-
{
    'name': "Cambio masivo de ordenes de ventas a borrador",

    'summary': """
        Cambia las ordenes de ventas seleccionadas a borrador """,

    'description': """
        Cambia las ordenes de ventas seleccionadas a borrador
    """,

    'author': "Oswaldo Lopez S. (Cabalcon)",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],

}
