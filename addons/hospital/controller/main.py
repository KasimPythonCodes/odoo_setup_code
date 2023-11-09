from odoo import http
from odoo.http import request


class Hospital(http.Controller):
    @http.route('/hospital/doctor/', website=True, auth='public')
    def hospital_doctor(self, **kw):
        return request.render('hospital.patient_page',{})
