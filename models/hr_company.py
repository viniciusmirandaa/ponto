from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.base import misc
    from erpbrasil.base.fiscal import cnpj_cpf, ie
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class HrCompany(models.Model):
    _name = "hr.company"
    _inherit = ["image.mixin", 'mail.thread', 'mail.activity.mixin']

    name = fields.Char()

    cnpj_cpf = fields.Char(
        string="CNPJ",
        size=18,
    )

    inscr_est = fields.Char(
        string="State Tax Number",
        size=17,
    )

    inscr_mun = fields.Char(
        string="Municipal Tax Number",
        size=18,
    )

    legal_name = fields.Char(
        size=128,
        help="Used in fiscal documents",
    )

    city_id = fields.Many2one(
        string="City of Address",
        comodel_name="res.city",
    )

    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        ondelete='restrict',
        domain="[('country_id', '=?', country_id)]"
    )

    country_id = fields.Many2one(
        comodel_name="res.country.state",
        default=lambda self: self.env.ref("base.br"),
    )

    district = fields.Char(
        size=32,
    )

    street = fields.Char()

    street2 = fields.Char()

    zip = fields.Char(change_default=True)

    city = fields.Char()

    @api.onchange("cnpj_cpf")
    def _onchange_cnpj_cpf(self):
        self.cnpj_cpf = cnpj_cpf.formata(str(self.cnpj_cpf))

    @api.onchange("zip")
    def _onchange_zip(self):
        self.zip = misc.format_zipcode(self.zip, self.country_id.code)

    # TODO: O metodo tanto no res.partner quanto no res.company chamam
    #  _onchange_state e aqui também deveria, porém por algum motivo
    #  ainda desconhecido se o metodo estiver com o mesmo nome não é
    #  chamado, por isso aqui está sendo adicionado o final _id
    @api.onchange("state_id")
    def _onchange_state_id(self):
        self.city_id = None

    @api.constrains("cnpj_cpf", "country_id")
    def _check_cnpj_cpf(self):
        result = True
        for record in self:

            disable_cnpj_ie_validation = record.env[
                                             "ir.config_parameter"
                                         ].sudo().get_param(
                "l10n_br_base.disable_cpf_cnpj_validation", default=False
            ) or self.env.context.get(
                "disable_cpf_cnpj_validation"
            )
            if not disable_cnpj_ie_validation:
                if record.country_id:
                    country_code = record.country_id.code
                    if country_code:
                        if record.cnpj_cpf and country_code.upper() == "BR":
                            if record.is_company:
                                if not cnpj_cpf.validar(record.cnpj_cpf):
                                    result = False
                                    document = "CNPJ"
                            elif not cnpj_cpf.validar(record.cnpj_cpf):
                                result = False
                                document = "CPF"
                if not result:
                    raise ValidationError(_("{} Invalid!").format(document))
