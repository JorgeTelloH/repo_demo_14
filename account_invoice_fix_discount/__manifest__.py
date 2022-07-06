# -*- coding: utf-8 -*-
{
    "name": "Factura con Descuento por Linea",
    "summary": "Factura con Descuento por Linea",
    'description': """
        Se aplica mejoras al Descuento por Linea de Factura:\n
        - Monto total de Descuento en Lineas de Facturas.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    "category": "Accounting",
    "version": "1.1",

    # any module necessary for this one to work correctly
    "depends": ["account"],

    # always loaded
    "data": ['views/account_move_view.xml',
            'reports/report_account_invoice.xml'
    ],
}
