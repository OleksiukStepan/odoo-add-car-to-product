from odoo import models, fields


class ProductTemplateIsAutoparts(models.Model):
    _inherit = "product.template"

    is_autoparts = fields.Boolean(string="Is autopart", store=True)
