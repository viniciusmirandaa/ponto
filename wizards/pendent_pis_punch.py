from odoo import fields, models, api


class PendentPisPunch(models.TransientModel):
    _name = "pendent.pis.punch"

    employee_pis_id = fields.Many2one(
        comodel_name="employee.pis.punch"
    )

    employee_name = fields.Char(
        string="Funcionário"
    )

    employee_pis = fields.Char(
        string="PIS"
    )
