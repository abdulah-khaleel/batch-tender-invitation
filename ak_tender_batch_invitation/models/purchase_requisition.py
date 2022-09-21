# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

#     partner_ids = fields.Many2many('rces.partner', string='Vendors')
    partner_ids = fields.One2many('requisition.vendor', 'requisition_id', string='Vendors')

    def action_send_invitation(self):
        for rec in self:
            print('Creating rfqs for a total of partners:', len(rec.partner_ids))
            for partner in rec.partner_ids:
                if partner.invitation_state == 'new':
                    print('generating rfq for vendor: ', partner.partner_id.name)
                    purchase_order_id = self.env['purchase.order'].create({
                        'partner_id': partner.partner_id.id,
                        'requisition_id': rec.id,
                        'origin': rec.name,
                        'date_order': rec.date_end or fields.Date.today(),
                        'order_line': [(0, 0, {
                            'product_id': rec.line_ids.product_id.id,
                            'name': rec.line_ids.product_id.name,
                            'product_qty': rec.line_ids.product_qty,
                            'product_uom': rec.line_ids.product_uom_id.id
                        })]
                    })
                    partner.invitation_state = 'sent'
                    if partner.partner_id.email:
                        print('sending invitation to vendor: ', partner.partner_id.name)
                        template = self.env.ref('purchase.email_template_edi_purchase')
                        template.send_mail(purchase_order_id.id, force_send=True)
                        # purchase_order_id.action_rfq_send()
                        purchase_order_id.state = 'sent'
                    else:
                        print(f'No email address for vendor: {partner.partner_id.name}')





class RequisitionVendors(models.Model):
    _name = 'requisition.vendor'

    partner_id = fields.Many2one('res.partner', string="Vendor")
    requisition_id = fields.Many2one('purchase.requisition', string="Requisition")
    invitation_state = fields.Selection([
        ('new', 'New'),
        ('sent', 'Invite Sent'),
    ], default="new", required=True)