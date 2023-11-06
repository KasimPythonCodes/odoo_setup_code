# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Hospital Management',
    'version': '11.10.0.0',
    'category': 'Management',
    'description': '',
    'summary':'Managing the budget and finances of the hospital. '
              'Recruiting and training staff, as well as overseeing their work. '
              'Ensuring that the hospital follows all applicable rules and laws.',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'Patient_Appointment/patient_appointment_file.xml',
        'doctor.xml',
        'view/css/css_loader.xml',
        'data/sequence.xml',
        'reports/report.xml',
        'reports/report_doctor.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
