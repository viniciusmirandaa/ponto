from odoo import fields, models


class EmployeePisPunch(models.TransientModel):
    _name = "employee.pis.punch"

    pendent_employee_pis_ids = fields.One2many(
        comodel_name="pendent.pis.punch",
        inverse_name="employee_pis_id"
    )

    message = fields.Char()

    def save(self):
        for line in self.pendent_employee_pis_ids:
            self.env['hr.employee'].create({'name': line.name, 'employee_pis': line.employee_pis})
