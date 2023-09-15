from odoo import models, fields


class PunchTime(models.TransientModel):
    _name = 'punch.time'

    manage_employee_time_id = fields.Many2one('manage.employee.time')
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    punch_clock_ids = fields.Many2many('punch.clock', string="Batidas")
    employee_pis = fields.Char(string="PIS do Funcionário")
    datetime = fields.Date()
