# -*- coding: utf-8 -*-
{
    'name': 'Ancom Sales Orders',
    'version': '16.0.1.0.0',
    'summary': 'Custom module for linking Sales Orders with Purchase Orders and adding custom fields.',
    'description': """
This module is a technical test submission. It enhances the Sales Order functionality by:
- Adding new fields: Request Vendor, No Kontrak, and With PO.
- Adding a new tab to display related Purchase Orders.
- Allowing the creation of a Purchase Order directly from a Sales Order.
- Validating the 'No Kontrak' field to ensure it is unique.
- Providing a wizard to import Sales Order lines from an Excel file.
    """,
    'author': 'Anjas Amar Pradana',
    'website': 'https://www.linkedin.com/in/anjas-amar-pradana/',
    'category': 'Sales',
    'depends': [
        'sale_management',
        'purchase',
        'sale_purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_so_lines_wizard_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
