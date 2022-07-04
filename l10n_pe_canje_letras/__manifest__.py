# -*- coding: utf-8 -*-
{
    'name' : 'Canje de letras',
    'summary': 'Canje de letras',
    'description' : """
    Canje de facturas por letras
    """,

    'author' : 'Oswaldo Lopez (Cabalcon)',
    'website': "http://www.cabalcon.com",

    'version' : '1.0',
    'category' : 'Accounting & Finance',

    'depends' : ['account'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'wizard/payment_letra.xml',
        'views/canje_letra.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
