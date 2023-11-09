# from odoo import models, fields, api, exceptions
#
# TP, OP, RA = [], [], []
#
#
# class ParameterModel(models.Model):
#     _name = 'hospital.parameter'
#     _description = 'Parameter'
#
#     parameter = fields.Selection([
#         ('TP', 'Technical Parameter'),
#         ('OP', 'Other Parameter'),
#         ('RA', 'Requirement Area'),
#         ], string="Parameter")
#     value = fields.Text(string='Value')
#
#     @api.onchange('value')
#     def parameter_value(self):
#         for i in self:
#             if i.parameter == 'TP':
#                 if i.value in TP:
#                     raise exceptions.ValidationError('Cannot Repeat Value with same Parameter')
#                 TP.append(i.value)
#
#             if i.parameter == 'OP':
#                 if i.value in OP:
#                     raise exceptions.ValidationError('Cannot Repeat Value with same Parameter')
#                 OP.append(i.value)
#
#             if i.parameter == 'RA':
#                 if i.value in RA:
#                     raise exceptions.ValidationError('Cannot Repeat Value with same Parameter')
#                 RA.append(i.value)
from odoo import models, fields, api, exceptions

TP, OP, RA = [], [], []


class ParameterModel(models.Model):
    _name = 'hospital.parameter'
    _description = 'Parameter'
    parameter = fields.Selection([
        ('TP', 'Technical Parameter'),
        ('OP', 'Other Parameter'),
        ('RA', 'Requirement Area'),
    ], string="Parameter")
    value = fields.Text(string='Value')

    @api.constrains('parameter', 'value')
    def _check_parameter_and_value(self):
        for rec in self:
            if rec.parameter and not rec.value:
                raise exceptions.ValidationError("Please fill in the 'Value' for the provided 'Parameter'.")
            if rec.parameter == rec.value:
                raise exceptions.ValidationError("The 'Parameter' and 'Value' should not be the same.")

    @api.constrains('value', 'parameter')
    def _check_unique_value(self):
        for rec in self:
            if rec.parameter == 'TP' and rec.value in TP:
                raise exceptions.ValidationError('Cannot Repeat Value with the same Parameter')
            elif rec.parameter == 'OP' and rec.value in OP:
                raise exceptions.ValidationError('Cannot Repeat Value with the same Parameter')
            elif rec.parameter == 'RA' and rec.value in RA:
                raise exceptions.ValidationError('Cannot Repeat Value with the same Parameter')
            else:
                if rec.parameter == 'TP':
                    TP.append(rec.value)
                elif rec.parameter == 'OP':
                    OP.append(rec.value)
                elif rec.parameter == 'RA':
                    RA.append(rec.value)
