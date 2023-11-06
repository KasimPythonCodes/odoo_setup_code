from odoo import api, models, _


class PatientCardReport(models.AbstractModel):
    _name = 'report.om_hospital.report_patient'
    _description = 'Patient card Report'

    @api.model
    def get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'hospital.patient',
            'docs': self.env['hospital.patient'].browse(docids),
            # Other data you want to pass to the report template
        }
