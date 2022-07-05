# -*- coding: utf-8 -*-
{
    "name": "Factura con Descuento por Linea",
    "summary": "Permitir aplicar Dscto en Lineas de Facturas",
    'description': """
        Se aplica mejoras al Descuento por Linea de Factura, agregando:\n
        - Monto de Descuento en Lineas de Facturas.
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
