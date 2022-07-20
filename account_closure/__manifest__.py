# -*- coding: utf-8 -*-
{
	'name': 'Proceso de Cierre/Apertura Contable',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','account_element','account_fiscal_year_period','unique_library_accounting_queries'],
	'description':'''
		Modulo para Proceso de Cierre/Apertura Contable.
			> Cierre/Apertura Contable
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/relationship_between_accounts_view.xml',
		'views/account_closure_view.xml',
		'views/closing_account_move_view.xml',

	],
	'installable': True,
    'auto_install': False,
}