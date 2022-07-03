# -*- coding: utf-8 -*-
{
    'name' : 'Asientos de Destino',
    'version' : '1.0',
    'author' : 'Oswaldo Lopez (Cabalcon)',
    'category' : 'Accounting',
    'summary': 'Asiento de destino automáticos al publicar un asiento.',
    'license': 'AGPL-3',
    'description' : """
	Cuentas destino automáticos al publicar un asiento.
    """,
    'website': "http://www.cabalcon.com",
    'depends' : ['account','account_pe'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/analytic_account_view.xml',
        'views/account_move_destiny_view.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "sequence": 1,
}
