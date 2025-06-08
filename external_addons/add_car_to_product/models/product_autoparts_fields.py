from odoo import models, fields, api


class ProductProductAutopart(models.Model):
    _inherit = "product.product"

    is_autoparts = fields.Boolean(
        string="Is autopart",
        related="product_tmpl_id.is_autoparts",
        store=True
    )
    compatible_vehicle_ids = fields.Many2many(
        comodel_name="fleet.vehicle.model",
        relation="product_compatible_vehicle_rel",
        column1="product_id",
        column2="vehicle_model_id",
        string="Compatible Vehicles",
    )
    for_all_models = fields.Boolean(string="Fits All Models")
    oem = fields.Char(string="OEM")
    ovoko_part_id = fields.Char(string="Ovoko Part ID")

    vehicle_info = fields.Char(
        string="Vehicle Info",
        compute="_compute_vehicle_info",
        store=True,
    )

    @api.depends("compatible_vehicle_ids")
    def _compute_vehicle_info(self):
        for rec in self:
            if rec.compatible_vehicle_ids:
                v = rec.compatible_vehicle_ids[0]

                parts = filter(
                    None,
                    [
                        v.brand_id.name,
                        v.name,
                        v.model_type,
                        self._get_years(v.model_year_from, v.model_year_to),
                    ],
                )
                rec.vehicle_info = " ".join(parts)
            else:
                rec.vehicle_info = ""

    # Return formatted year range string like "2010 - 2015", "... - 2015", etc.
    def _get_years(self, year_from, year_to):
        if year_from and year_to:
            return f"{year_from} - {year_to}"
        elif year_from:
            return f"{year_from} - ..."
        elif year_to:
            return f"... - {year_to}"
        return ""
