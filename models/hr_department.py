from odoo import fields, models, api


class HrDepartment(models.Model):
    _name = "hr.department"
    _inherit = _name

    job_ids = fields.Many2many(
        comodel_name="hr.job",
        relation="job_hr_department_rel"
    )
