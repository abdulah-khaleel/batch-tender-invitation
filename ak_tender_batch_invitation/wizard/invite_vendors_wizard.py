# -*- coding: utf-8 -*-
from odoo import models, fields, _

class InviteVendorsWizard(models.TransientModel):
    _name = 'invite.vendors.wizard'
    _description = 'Create RFQs in batch'

    create_rfq = fields.Char('Create RFQs', help="You can only send RFQs")

    def get_product_name(self, product_id):
            if product_id.default_code:
                return f'[{product_id.default_code }] '+ product_id.name
            return product_id.name

    def get_requisition_lines(self, requisition_id):
        lines_list = []
        for line in requisition_id.line_ids:
            lines_list.append((0, 0, {
                'product_id': line.product_id.id,
                'name': self.get_product_name(line.product_id),
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'date_planned': line.schedule_date or fields.Date.today(),
            }))
        return lines_list  

    def display_notification(self,title, message, type):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': type,
                'sticky': False,
                'next':  {'type': 'ir.actions.act_window_close'},
            }
        }

    def create_rfq_for_vendor(self, partner_line, requisition_id):
        purchase_order_id = self.env['purchase.order'].create({
            'partner_id': partner_line.partner_id.id,
            'requisition_id': requisition_id.id,
            'origin': requisition_id.name,
            'notes': requisition_id.description,
            'date_order': requisition_id.schedule_date or fields.Date.today(),
            'date_planned': requisition_id.schedule_date or fields.Date.today(),
            'order_line': self.get_requisition_lines(requisition_id)
        })
        return purchase_order_id

    def send_rfq_email(self, partner_id, purchase_order_id):
        if partner_id.email:
            template = self.env.ref('purchase.email_template_edi_purchase')
            template.send_mail(
                purchase_order_id.id, 
                force_send=False,
                email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
                )
            purchase_order_id.state = 'sent'
            return True
        else:
            return False

    def action_create_rfq_with_email(self):
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and udpate partner line:
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                # send the email to vendor:
                email_sent = self.send_rfq_email(partner_line.partner_id, purchase_order_id)
                if email_sent:
                    partner_line.invitation_state = 'sent_with_email'
                else:
                    partner_line.invitation_state = 'sent'
        if new_vendors_count > 0:
            return self.display_notification('Invites Sent', f'{new_vendors_count} new RFQ(s) created.', 'success') 
        else:
            if len(requisition_id.partner_ids) == 0:
                return self.display_notification('No Vendors', 'Please add vendors from the "Vendors" tab and try again.', 'danger')
            else:
                return self.display_notification('No RFQs created', 'No new vendors found', 'danger')


    def action_create_rfq_only(self):
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and update partner line
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                partner_line.invitation_state = 'sent'
        if new_vendors_count > 0:
            return self.display_notification('RFQ created', f'{new_vendors_count} new RFQ(s) created', 'success')
        else:
            if len(requisition_id.partner_ids) == 0:
                return self.display_notification('No Vendors', f'Please add vendors from the "Vendors" tab and try again.', 'danger')
            else:
                return self.display_notification('No RFQs created', f'No new vendors found', 'danger')



    
