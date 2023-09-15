import datetime
from odoo import models, fields
import base64
import os


class PunchClockIntegration(models.TransientModel):
    _name = 'punch.clock.integration'

    afd_file = fields.Binary(string="Arquivo AFD")

    def criar(self):
        message = ""
        machine_info = []
        content = base64.b64decode(self.afd_file)
        content = content.decode('utf-8').split('\r\n')
        punch_file = os.path.dirname(os.path.abspath(__file__)) + '\\ponto.txt'

        if not os.path.exists(punch_file):  # primeiro registro
            with open(punch_file, 'w') as file:  # w significa write
                # Cria um arquivo de ponto e copia o arquivo escolhido para armazenar os pontos
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)
            # as 4 primeiras linhas dizem respeito ao relogio(no txt são 7 linhas mas ao testar pegou os registros que não
            # deveriam ser retornados por isso aqui na função so pego 4 linhas), por isso são salvas e removidas da lista de ponto
            for i in range(4):
                machine_info.append(content[i])
                content.remove(content[i])

        else:  # proximos registros
            # edita o arquivo txt apenas adicionando as linhas novas
            with open(punch_file, 'r') as file:  # r significa read
                lines = len(file.readlines())
                content = content[lines:]  # variável content recebe apenas as novas linhas de ponto

            # arquivo recebe as novas linhas de ponto
            with open(punch_file, 'a') as file:  # a significa append
                file.write('\n')
                for index, line in enumerate(content):
                    if index != (len(content) - 1):
                        file.write(line + '\n')
                    else:
                        file.write(line)

        # existem alguns registros que contem o nome do colaborador concatenado, e um caracter na string,
        # aqui a string é verificada e limpa
        character_to_remove = []
        for rec in content:
            if len(rec) > 34:
                rec = rec[0:35]
                for character in rec:
                    if character.isalpha():
                        character_to_remove.append(character)
                for i in character_to_remove:
                    rec = rec.replace(i, '')

        # aqui os dados da string são tratados e criados

        for line in content:
            punch_id = int(line[0:9])
            punch_datetime = datetime.datetime.strptime(line[10:22], '%d%m%Y%H%M')
            if any(char.isalpha() for char in line):
                employee_pis = str(line[24:35])
                employee_name = str(line[35:])
            else:
                employee_pis = str(line[23:])
                employee_name = False

                employee_id = self.env['hr.employee'].search([('employee_pis', '=like', employee_pis)])
                if not employee_id and not employee_name:
                    if employee_pis not in message:
                        message += "{}\n".format(employee_pis)
                elif not employee_id:
                    employee_id = self.env['hr.employee'].create(
                        {'name': employee_name,
                         'employee_pis': employee_pis})
                if employee_id:
                    punch_clock_id = self.env['punch.clock'].search(
                        [('employee_id', '=', employee_id.id), ('punch_date', '=', punch_datetime.date())])
                    formated_line = float(punch_datetime.time().strftime(
                                 "%H:%M").replace(":", "."))
                    formated_time_char = punch_datetime.time().strftime(
                                 "%H:%M")
                    if punch_clock_id:
                        self.env['punch.clock.lines'].with_context({'not_manual': True}).create(
                            {'punch_clock_id': punch_clock_id.id,
                             'time': punch_datetime,
                             'color': 7,
                             'formated_time': formated_line,
                             'formated_time_char': formated_time_char
                             })
                    else:
                        pc = self.env['punch.clock'].create({
                            'employee_id': employee_id.id or False,
                            'punch_id': punch_id,
                            'punch_date': punch_datetime.date()
                        })
                        self.env['punch.clock.lines'].with_context({'not_manual': True}).create(
                            {'punch_clock_id': pc.id,
                             'time': punch_datetime,
                             'color': 7,
                             'formated_time': formated_line,
                             'formated_time_char': formated_time_char
                             })

        if len(message) > 1:
            ctx = self._context.copy()
            ctx.update({'default_message': message})
            return {
                'view_mode': 'form',
                'res_model': 'employee.pis.punch',
                'views': [
                    [
                        self.env.ref("punch_clock_integration.employee_pis_punch_wizard_form").id, 'form'
                    ]
                ],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': ctx
            }
