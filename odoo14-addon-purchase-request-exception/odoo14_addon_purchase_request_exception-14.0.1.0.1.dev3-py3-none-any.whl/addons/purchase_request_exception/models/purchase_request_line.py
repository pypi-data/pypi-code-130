# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = ["purchase.request.line", "base.exception.method"]
    _name = "purchase.request.line"

    ignore_exception = fields.Boolean(
        related="request_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("request_id")

    @api.model
    def _reverse_field(self):
        return "purchase_request_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("request_id")
