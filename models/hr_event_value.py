from odoo import api, models, fields


class HrEventValue(models.Model):
    _name = "hr.event.value"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    syndicate_id = fields.Many2one(
        comodel_name="hr.syndicate"
    )

    event_id = fields.Many2one(
        comodel_name="hr.event"
    )

    value = fields.Char(
        string="Valor"
    )
