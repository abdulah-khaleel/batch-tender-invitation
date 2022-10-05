# -*- coding: utf-8 -*-

from hashlib import new
from odoo import models, fields, api, _

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    partner_ids = fields.One2many('requisition.vendor', 'requisition_id', string='Vendors')
    

class RequisitionVendors(models.Model):
    _name = 'requisition.vendor'

    partner_id = fields.Many2one('res.partner', string="Vendor")
    requisition_id = fields.Many2one('purchase.requisition', string="Requisition")
    invitation_state = fields.Selection([
        ('new', 'New'),
        ('sent', 'RFQ'),
        ('sent_with_email', 'RFQ sent'),
    ], string="Invitation Status", default="new", required=True)
    purchase_order_id = fields.Many2one('purchase.order', string="RFQ", readonly=True)

