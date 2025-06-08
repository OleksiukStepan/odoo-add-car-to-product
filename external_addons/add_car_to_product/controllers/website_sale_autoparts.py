from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute


class WebsiteSaleAutoparts(WebsiteSale):

    def _match_product_template(
        self, product_template, manufacturer_id, model_id, year_from, year_to, volume
    ):
        for p_variant in product_template.product_variant_ids:
            for vehicle in p_variant.compatible_vehicle_ids:
                if self._vehicle_matches_criteria(
                    vehicle, manufacturer_id, model_id, year_from, year_to, volume
                ):
                    return True
        return False

    def _vehicle_matches_criteria(
        self, vehicle, manufacturer_id, model_id, year_from, year_to, volume
    ):
        if not self._check_manufacturer(vehicle, manufacturer_id):
            return False
        if not self._check_model(vehicle, model_id):
            return False
        if not self._check_year(vehicle, year_from, year_to):
            return False
        if not self._check_volume(vehicle, volume):
            return False
        return True

    def _check_manufacturer(self, vehicle, manufacturer_id):
        if manufacturer_id and str(vehicle.brand_id.id) != manufacturer_id:
            return False
        return True

    def _check_model(self, vehicle, model_id):
        if model_id and vehicle.id != int(model_id):
            return False
        return True

    def _check_year(self, vehicle, year_from, year_to):
        if not (year_from or year_to):
            return True

        int_year_from_filter = int(year_from) if year_from else -float("inf")
        int_year_to_filter = int(year_to) if year_to else float("inf")

        vehicle_year_from = vehicle.model_year_from
        vehicle_year_to = vehicle.model_year_to

        if (not vehicle_year_from and not vehicle_year_to) or (
            vehicle_year_from == 0 and vehicle_year_to == 0
        ):
            return False

        effective_vehicle_year_from = (
            vehicle_year_from if vehicle_year_from else -float("inf")
        )
        effective_vehicle_year_to = vehicle_year_to if vehicle_year_to else float("inf")

        return (effective_vehicle_year_from <= int_year_to_filter) and (
            effective_vehicle_year_to >= int_year_from_filter
        )

    def _check_volume(self, vehicle, volume):
        if volume and vehicle.volume.name != volume:
            return False
        return True

    @http.route(["/shop"], type="http", auth="public", website=True)
    def shop(self, page=0, search="", **post):
        response = super().shop(page=page, search=search, **post)

        manufacturer_id = post.get("manufacturer_id")
        model_id = post.get("model_id")
        year_from = post.get("year_from")
        year_to = post.get("year_to")
        volume = post.get("volume")

        products = response.qcontext["products"]
        filtered_products = products.filtered(
            lambda p: self._match_product_template(
                p, manufacturer_id, model_id, year_from, year_to, volume
            )
        )

        response.qcontext["products"] = filtered_products

        ppg = response.qcontext.get("ppg", 20)
        ppr = response.qcontext.get("ppr", 4)
        response.qcontext["bins"] = TableCompute().process(filtered_products, ppg, ppr)

        BrandModel = request.env["fleet.vehicle.model.brand"]
        response.qcontext["brands"] = BrandModel.search([])

        VehicleModel = request.env["fleet.vehicle.model"]
        if manufacturer_id:
            models = VehicleModel.search([("brand_id", "=", int(manufacturer_id))])
        else:
            models = VehicleModel.search([])
        response.qcontext["models"] = models

        EngineVolume = request.env["vehicle.engine.volume"]
        response.qcontext["volumes"] = EngineVolume.search([])

        return response
