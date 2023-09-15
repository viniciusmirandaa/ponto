from odoo import models, fields, api
from datetime import datetime, timedelta


class PunchClockIntegration(models.Model):
    _name = 'punch.clock'

    employee_id = fields.Many2one(comodel_name="hr.employee")

    employee_date_punch_ids = fields.One2many(
        comodel_name="punch.clock.lines",
        inverse_name="punch_clock_id"
    )

    punch_date = fields.Date(
        string="Data"
    )

    punch_id = fields.Integer()

    def name_get(self):
        return [(rec.id, "{} / {}".format(rec.employee_id.name, rec.punch_date)) for rec in self]


class PunchClockLines(models.Model):
    _name = "punch.clock.lines"
    _inherit = "domain.entity.abstract"

    punch_clock_id = fields.Many2one(
        comodel_name="punch.clock"
    )

    time = fields.Datetime()

    color = fields.Integer(
        default=11
    )

    formated_time = fields.Float(string="Horários")

    # create on one2many view porpouse
    formated_time_char = fields.Char(string="Horários")

    @api.onchange("punch_clock_id")
    def _onchange_punch_clock_id(self):
        if 'default_time' in self._context:
            self.time += timedelta(hours=3)

    def name_get(self):
        return [(rec.id, rec.time.time().strftime("%H:%M")) for rec in self]

    @api.model
    def create(self, vals_list):
        if 'not_manual' in self._context:
            return super(PunchClockLines, self).create(vals_list=vals_list)
        else:
            vals_list['formated_time'] = (
                    datetime.strptime(vals_list.get("time"), "%Y-%m-%d %H:%M:%S") - timedelta(hours=3)).time().strftime(
                "%H:%M")
            rtn = super(PunchClockLines, self).create(vals_list=vals_list)
            rtn.write({'time': self.decrease_utc_time(rtn.time)})
            return rtn

