# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Hospital Management',
    'version': '11.10.1.0',
    'category': 'Management',
    'description': '',
    'sequence':'1',
    'summary':'Managing the budget and finances of the hospital. '
              'Recruiting and training staff, as well as overseeing their work. ',
    'depends': ['sale','mail'],
    'data':['security/ir.model.access.csv',
            'reports/report.xml',
            'reports/report_doctor.xml',
            'reports/appointment_pdf.xml',
            'reports/report_xlsx.xml',
            'reports/sales_report_inherit.xml',
            'data/sequence.xml',
            'data/email_templates.xml',
            'data/appointment.xml',
            'wizard/create_appointment.xml',
            'patient.xml',
            'controller/template.xml'],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
