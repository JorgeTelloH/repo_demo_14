{
	'name': 'SUNAT PLE-Diario-Mayor-Simplificado',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','ple_base'],
	'description':'''
		Modulo de reportes PLE de Libro Diario-Mayor-Simplificado.
			> Libro Diario-Mayor-Simplificado
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_diary_view.xml',
		'views/ple_diary_line_view.xml',
		'data/report_paperformat.xml',
		'report/report.xml',
		'report/templates_a4_new.xml',
		'report/templates_a4_simplificado.xml',
		'report/templates_a4_ledger.xml',
	],
	'installable': True,
    'auto_install': False,
}