# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Doctor Management',
    'version': '11.10.0.0',
    'category': 'Management',
    'description': '',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'doctor.xml',
        'view/css/css_loader.xml',
        'data/sequence.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
