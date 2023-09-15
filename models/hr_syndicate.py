from odoo import fields, models, api


class HrSyndicate(models.Model):
    _name = "hr.syndicate"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_ids = fields.One2many(
        comodel_name="hr.employee",
        inverse_name="syndicate_id",
        string="Funcionários"
    )

    name = fields.Char(
        string="Nome"
    )

    events_values_ids = fields.One2many(
        comodel_name="hr.event.value",
        inverse_name="syndicate_id"
    )
