from odoo import api, fields, models


class HrEvent(models.Model):
    _name = "hr.event"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Descrição"
    )

    code = fields.Integer(
        string="Código"
    )

