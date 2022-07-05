{
	'name': 'SUNAT PLE-Activos Fijos',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','ple_base','om_account_asset'],#'account_asset_extended'],
	'description':'''
		Modulo de reportes PLE de Activos Fijos.
			> Libro de Activos Fijos
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/account_asset_asset_view.xml',
		'views/ple_fixed_asset_view.xml',
		'views/ple_fixed_asset_line_view.xml',

		'data/report_paperformat.xml',
		'report/report.xml',
		'report/templates_a4.xml',

	],
	'installable': True,
    'auto_install': False,
}