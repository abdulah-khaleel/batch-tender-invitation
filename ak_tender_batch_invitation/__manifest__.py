# -*- coding: utf-8 -*-
################################################################################# 
#
#    Author: Abdullah Khalil. Copyrights (C) 2022-TODAY reserved. 
#    Email: abdulah.khaleel@gmail.com
#    You may use this app as per the rules outlined in the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3. 
#    See <http://www.gnu.org/licenses/> for more detials.
#   
#
################################################################################# 

{
    'name': "Invite Vendors in Batch",   
    'summary': "Create multiple RFQs in a Call for Tender and send out email invitations to vendors in batch",   
    'description': """
        Create RFQs for multiple vendors in a call for tenders in batch. Send out email invitations 
        to multiple vendors when creating the RFQs.
    """,   
    'author': "Abdullah Khalil",
    'website': "https://github.com/abdulah-khaleel",
    'category': 'Purchase',
    'version': '14.0.0.0',
     "license": "LGPL-3",
    'depends': ['base','purchase','purchase_requisition'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invite_vendors_wizard_views.xml',
        'views/purchase_requisition_views.xml',
    ],
    'images': ["static/description/banner-v14.png"],
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
} 
