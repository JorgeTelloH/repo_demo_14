# -*- coding: utf-8 -*-
{
    'name': 'Contratos de Empleados',
    'summary': '',
    'description': """
Personalización del módulo de Contratos de empleado:
    - EPS
    - Motivos de Salida de la Compañia
    - Alerta de Vencimiento de Contratos
    - Autogenerar Codigo de Empleado

    """,
    'version': '1.0',
    'category': 'Human Resources/Contracts',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'sequence': 180,
    'depends': ['base_automation', 'hr_contract', 'cabalcon_hr'],
    "data": [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_contract_type_views.xml',
        'views/hr_contract_views.xml',
        'views/health_entity_views.xml',
        'views/hr_employee_departure_reason_views.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_views.xml',
        'views/resource_views.xml',
        'report/report_withdrawal_letter_cts.xml',
        'report/report_work_certificates.xml',
        'data/hr_contract_cron_data.xml',
        'data/hr_contract_health_entity.xml',
        'data/hr_employee_departure_reason.xml',
        'data/email_template.xml',
        'wizard/work_certificates_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
