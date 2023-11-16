# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Chadha Industrial Company",
    'summary': 'This company handle various industrial employment',
    'sequence':'1',
    'description': "IT Solutions",
    'category': 'Hidden',
    'version': '11.0.0.0',
    'depends': [],
    'data': [
        'views/company.xml',
        'views/partner.xml',
        'views/parameters.xml',
        'security/ir.model.access.csv',
             ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
