{
    'name': 'punch_clock_integration',
    'version': '14.0.1.0.1',
    'summary': "",
    'description': "",
    'category': '',
    'author': 'Thiago Francelino Santos',
    'contributors': [
        'Mila Feitosa Martins'
    ],
    'depends': ['base', 'hr', 'base_address_city', 'domain-entity-abstract'],
    'company': 'SUPERGLASS',
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizards/manage_employee_time.xml',
        'wizards/punch_clock_integration_view.xml',
        'wizards/employee_pis_punch.xml',
        'views/punch_clock_lines.xml',
        'views/punch_clock_view.xml',
        'views/hr_company.xml',
        'views/hr_department.xml',
        'views/hr_employee_view.xml',
        'views/hr_syndicate.xml',
        'views/hr_event.xml',
        'data/hr_job_data.xml',
        'data/hr_event_data.xml',
        'data/hr_employee_data.xml'
    ],
    'license': 'LGPL-3',
}
