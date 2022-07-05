{
	'name': 'Balance de Sumas y Saldos',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','account_element','report_formats','unique_library_accounting_queries'],
	'description':'''
		Modulo de Balance de Sumas y Saldos.
			> Balance de Sumas y Saldos
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/report_amount_balances_view.xml',
		'data/balance.category.column.csv',
	],
	'installable': True,
    'auto_install': False,
}
