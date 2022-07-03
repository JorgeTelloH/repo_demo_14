# -*- encoding: utf-8 -*-

{
    'name': 'Ausencias - Cabalcon',
    'category': 'Human Resources',
    'author': 'Cabalcon',
    'website': '',
    'depends': ['hr_holidays', 'hr_work_entry_contract'],
    'version': '1.0',
    'active': True,
    'data': ['views/import_error_view.xml',
             'wizard/wizard_import_vacations_view.xml',
             'security/ir.model.access.csv',
             'data/hr_holidays_data.xml'
    ],
    'css': [],
    'test': [

    ],

    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
