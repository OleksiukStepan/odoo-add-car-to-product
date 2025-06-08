from odoo import models, fields


class VehicleEngineVolume(models.Model):
    _name = "vehicle.engine.volume"
    _description = "Engine Volume"

    name = fields.Char("Volume", required=True)
