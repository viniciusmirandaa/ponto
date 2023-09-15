from odoo import fields, models, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_pis = fields.Char(string="PIS")

    syndicate_id = fields.Many2one(
        comodel_name="hr.syndicate"
    )

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id:
            return {'domain': {
                'job_id': [('id', 'in', self.department_id.job_ids.ids)]
            }}
