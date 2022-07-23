# -*- coding: utf-8 -*-

{
    'name': 'Nómina de empleados',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Human Resources',
    'summary': 'Personalización de la nómina.',
    'depends': ['hr_payroll', 'cabalcon_hr_contract', 'cabalcon_hr_holidays', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_contract_views.xml',
        'reports/report_liquidation.xml',
        'reports/report_payroll_voucher_templates.xml',
        'reports/payroll_report.xml',
        'reports/afp_net_report_xlsx.xml',
        'reports/report_liquidation_cts.xml',
        'reports/matrix_report_xlsx.xml',
        'wizard/liquidation_wizard_views.xml',
        'wizard/afp_net_wizard_views.xml',
        'wizard/liquidation_cts_wizard_views.xml',
        'wizard/matrix_wizard_views.xml'
    ],
    'installable': True,
    'application': False,
}
