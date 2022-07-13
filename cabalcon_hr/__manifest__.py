# -*- encoding: utf-8 -*-
{
    'name': 'HR Empleados :: Personalización',
    'summary': 'Personalización de Empleados',
    'description': """
    Personalización del módulo de Recursos Humanos
	""",
    'version': '1.0',
    'category': 'Human Resources/Employees',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'sequence': 180,
    'depends': ['hr', 'hr_employee_lastnames', 'report_xlsx', 'product', 'l10n_pe', 'hr_employee_driver'],
    "data": [
        'security/ir.model.access.csv',
        'data/afp_data.xml',
        'data/hr_occupational_category_data.xml',
        'data/hr_educational_situation_data.xml',
        'data/hr_contract_type_data.xml',
        'views/hr_job_views.xml',
		'views/document_type_view.xml',
        'views/hr_employee_views.xml',
        'views/afp_views.xml',
        'views/res_company_view.xml',
        'views/hr_occupational_category_views.xml',
        'views/hr_educational_situation_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner.xml',
        'wizard/hr_departure_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
