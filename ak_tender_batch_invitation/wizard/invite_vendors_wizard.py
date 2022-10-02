# -*- coding: utf-8 -*-
from odoo import models, fields, _


class InviteVendorsWizard(models.TransientModel):
    _name = 'invite.vendors.wizard'
    _description = 'Create RFQs in batch'

    # borrower_ids = fields.Many2many('res.partner', string="Borrowers")
    # misc = fields.Char('Misc')

    def get_requisition_lines(self, requisition_id):
        lines_list = []
        for line in requisition_id.line_ids:
            lines_list.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.product_qty,
                # 'product_uom_id': line.product_uom_id.id,
                'price_unit': line.price_unit,
                'date_planned': requisition_id.date_end,
            }))
        return lines_list

    def display_notification(self,title, message, type, action):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': type,
                'sticky': False,
                'next': action,
            }
        }


    def create_rfq_for_vendor(self, partner_line, requisition_id):
        print('generating rfq for vendor: ', partner_line.partner_id.name)
        purchase_order_id = self.env['purchase.order'].create({
            'partner_id': partner_line.partner_id.id,
            'requisition_id': requisition_id.id,
            'origin': requisition_id.name,
            'date_order': requisition_id.date_end or fields.Date.today(),
            'order_line': self.get_requisition_lines(requisition_id)
        })
        return purchase_order_id

    def send_rfq_email(self, partner_id, purchase_order_id):
        if partner_id.email:
            print('sending invitation to vendor: ', partner_id.name)
            template = self.env.ref('purchase.email_template_edi_purchase')
            template.send_mail(purchase_order_id.id, force_send=False)
            purchase_order_id.state = 'sent'
            return True
        else:
            print(f'No email address for vendor: {partner_id.name}')
            return False

    def action_create_rfq_with_email(self):
        # get requisition_id with model as active id from context:
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and udpate partner line:
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                # send the email to vendor:
                email_attempt = self.send_rfq_email(partner_line.partner_id, purchase_order_id)
                if email_attempt:
                    partner_line.invitation_state = 'sent_with_email'
                else:
                    partner_line.invitation_state = 'sent'
            else:
                print('rfq already created for vendor: ', partner_line.partner_id.name)
        #close current wizard:
        if new_vendors_count > 0:
            return self.display_notification('Invites Sent', f'{new_vendors_count} new RFQ(s) created. Invites sent to vendors with email addresses.', 'success', {'type': 'ir.actions.act_window_close'}) 
        else:
            return self.display_notification('No RFQs created', 'No new vendors found', 'danger', {'type': 'ir.actions.act_window_close'})

    def action_create_rfq_only(self):
        # get requisition_id with model as active id from context:
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and udpate partner line:
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                partner_line.invitation_state = 'sent'
            else:
                print('rfq already created for vendor: ', partner_line.partner_id.name)
        if new_vendors_count > 0:
            return self.display_notification('RFQs created', f'{new_vendors_count} new RFQ(s) created.', 'success', {'type': 'ir.actions.act_window_close'})
        else:
            return self.display_notification('No RFQs created', 'No new vendors found', 'danger', {'type': 'ir.actions.act_window_close'})


