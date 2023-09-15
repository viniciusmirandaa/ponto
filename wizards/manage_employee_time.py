from odoo import models, fields, _
import datetime
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta


class ManageEmployeeTime(models.TransientModel):
    _name = 'manage.employee.time'

    filter = fields.Selection(
        [('range', 'Intervalo de Dias'),
         ('day', 'Dia'),
         ('month', 'Consulta Mensal')],
        string="Opções de Pesquisa")

    punch_time_ids = fields.One2many(
        'punch.time',
        'manage_employee_time_id',
        string="Horarios"
    )

    day_to_search = fields.Date(
        string="Dia a pesquisar"
    )

    last_day = fields.Date(
        string="Dia final"
    )

    month = fields.Selection([('01', 'Janeiro'),
                              ('02', 'Fevereiro'),
                              ('03', 'Março'),
                              ('04', 'Abril'),
                              ('05', 'Maio'),
                              ('06', 'Junho'),
                              ('07', 'Julho'),
                              ('08', 'Agosto'),
                              ('09', 'Setembro'),
                              ('10', 'Outubro'),
                              ('11', 'Novembro'),
                              ('12', 'Dezembro')
                              ], string="Mês")

    year = fields.Integer("Ano")

    employee_id = fields.Many2one(
        'hr.employee',
        string="Funcionário"
    )

    monthly_hours = fields.Char(readonly=True)

    attrs_bool = fields.Boolean()

    def search_employee_punch(self):
        if self.punch_time_ids:
            self.punch_time_ids.unlink()
        domain = []
        if self.filter == 'range':
            domain.append(('punch_datetime', '>=', self.day_to_search))
            domain.append(('punch_datetime', '<=', self.last_day))
        elif self.filter == 'day':
            domain.append(('punch_datetime', '>=', self.day_to_search))
            domain.append(('punch_datetime', '<', self.day_to_search + datetime.timedelta(days=1)))
        else:
            domain.append(('employee_pis', '=', self.employee_id.employee_pis))
            data_inicial = datetime.datetime(self.year, int(self.month), 1)
            data_final = data_inicial + relativedelta(months=1, days=-1, hours=23, minutes=59)
            domain.append(('punch_datetime', '>=', data_inicial))
            domain.append(('punch_datetime', '<=', data_final))

        punch_ids = self.env['punch.clock'].search(domain)
        if not punch_ids:
            raise Warning(_("Não há resultados para essa pesquisa."))
        else:
            ctx = dict()
            if self.filter == 'range':
                for pis in punch_ids.mapped('employee_pis'):
                    days_range = self.last_day - self.day_to_search
                    days_range = days_range.days + 1
                    i = self.day_to_search
                    for day in range(days_range):
                        employee_punch_ids = punch_ids.filtered(
                            lambda lm: lm.employee_pis == pis and lm.punch_datetime.date() == i)
                        vals = {
                            'manage_employee_time_id': self.id,
                            'employee_id': self.env['hr.employee'].search([('employee_pis', '=', pis)]).id,
                            'punch_clock_ids': employee_punch_ids.ids,
                            'datetime': i,
                            'employee_pis': pis,
                        }
                        i += datetime.timedelta(days=1)
                        self.env['punch.time'].create(vals)
            elif self.filter == 'day':
                for pis in punch_ids.mapped('employee_pis'):
                    employee_punch_ids = punch_ids.filtered(lambda lm: lm.employee_pis == pis)
                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.env['hr.employee'].search([('employee_pis', '=', pis)]).id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'employee_pis': pis,
                    }
                    self.env['punch.time'].create(vals)
            else:
                days_range = data_final - data_inicial
                days_range = days_range.days + 1
                i = data_inicial.date()
                seconds_diference = 0
                for index, day in enumerate(range(days_range)):
                    employee_punch_ids = punch_ids.filtered(lambda lm: lm.punch_datetime.date() == i)
                    first = employee_punch_ids[0].punch_datetime if employee_punch_ids else 0
                    last = employee_punch_ids[-1].punch_datetime if employee_punch_ids else 0
                    diference = (last) - (first)
                    seconds_diference += diference.seconds if employee_punch_ids else 0
                    if len(employee_punch_ids.ids) >= 4:
                        intraday = employee_punch_ids[2].punch_datetime - employee_punch_ids[1].punch_datetime
                        seconds_diference -= intraday.seconds
                    vals = {
                        'manage_employee_time_id': self.id,
                        'employee_id': self.employee_id.id,
                        'punch_clock_ids': employee_punch_ids.ids,
                        'datetime': i,
                        'employee_pis': self.employee_id.employee_pis,
                    }
                    i += datetime.timedelta(days=1)
                    self.env['punch.time'].create(vals)
                    if index == days_range - 1:
                        horas = seconds_diference // 3600  # 3600 segundos em uma hora
                        minutos = (seconds_diference % 3600) // 60
                        self.monthly_hours = str(horas) + ":" + str(minutos)
                ctx.update({
                    'default_attrs_bool': True,
                    'default_monthly_hours': self.monthly_hours,
                })
            ctx.update({
                'default_day_to_search': self.day_to_search,
                'default_punch_time_ids': self.punch_time_ids.ids,
                'default_filter': self.filter,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pesquisa de ponto',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'manage.employee.time',
                'views': [[self.env.ref("punch_clock_integration.manage_employee_time_form").id, 'form']],
                'context': ctx,
                'target': 'new'
            }
