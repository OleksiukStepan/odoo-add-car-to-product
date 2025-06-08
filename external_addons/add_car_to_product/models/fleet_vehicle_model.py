from odoo import models, fields


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    model_year_from = fields.Integer("Year from")
    model_year_to = fields.Integer("Year to")
    model_type = fields.Char("Model type")
    volume = fields.Many2one("vehicle.engine.volume", string="Volume")
    ovoko_car_id = fields.Char("Ovoko Car ID")
