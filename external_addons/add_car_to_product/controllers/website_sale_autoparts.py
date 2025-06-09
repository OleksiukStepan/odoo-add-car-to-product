from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute


class WebsiteSaleAutoparts(WebsiteSale):

    @http.route(["/shop"], type="http", auth="public", website=True)
    def shop(self, page=0, search="", **post):
        response = super().shop(page=page, search=search, **post)

        # Get filter params
        manufacturer_id = post.get("manufacturer_id")
        model_id = post.get("model_id")
        year_from = post.get("year_from")
        year_to = post.get("year_to")
        volume = post.get("volume")

        # Filter products
        products = response.qcontext["products"]
        filtered = products.filtered(
            lambda p: self._match_product_template(p, manufacturer_id, model_id, year_from, year_to, volume)
        )

        # Update qcontext
        response.qcontext["products"] = filtered
        response.qcontext["bins"] = TableCompute().process(filtered, response.qcontext.get("ppg", 20), response.qcontext.get("ppr", 4))

        # Inject available filter options
        self._inject_filter_options(response.qcontext, manufacturer_id)

        return response

    def _match_product_template(
        self,
        product_template,
        manufacturer_id,
        model_id,
        year_from,
        year_to,
        volume
    ):
        for variant in product_template.product_variant_ids:
            for vehicle in variant.compatible_vehicle_ids:
                if self._vehicle_matches(
                    vehicle,
                    manufacturer_id,
                    model_id,
                    year_from,
                    year_to,
                    volume
                ):
                    return True
        return False

    def _vehicle_matches(
        self,
        vehicle,
        manufacturer_id,
        model_id,
        year_from,
        year_to,
        volume
    ):
        return (
            self._vehicle_field_matches(vehicle.brand_id.id, manufacturer_id)
            and self._vehicle_field_matches(vehicle.id, model_id)
            and self._vehicle_year_matches(vehicle, year_from, year_to)
            and self._vehicle_field_matches(vehicle.volume.name, volume)
        )

    def _vehicle_field_matches(self, vehicle_value, filter_value):
        return not filter_value or str(vehicle_value) == str(filter_value)

    def _vehicle_year_matches(self, vehicle, year_from, year_to):
        if not (year_from or year_to):
            return True

        from_filter = int(year_from) if year_from else -float("inf")
        to_filter = int(year_to) if year_to else float("inf")

        from_vehicle = (
            vehicle.model_year_from
            if vehicle.model_year_from else -float("inf")
        )
        to_vehicle = (
            vehicle.model_year_to
            if vehicle.model_year_to else float("inf")
        )

        if from_vehicle == to_vehicle == 0:
            return False

        return from_vehicle <= to_filter and to_vehicle >= from_filter

    def _inject_filter_options(self, qcontext, manufacturer_id):
        qcontext["brands"] = request.env["fleet.vehicle.model.brand"].search([])
        qcontext["models"] = request.env["fleet.vehicle.model"].search(
            [("brand_id", "=", int(manufacturer_id))]
            if manufacturer_id else []
        )
        qcontext["volumes"] = request.env["vehicle.engine.volume"].search([])
