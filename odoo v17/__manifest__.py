# -*- coding: utf-8 -*-
# Copyright 2025 - Anjas Amar Pradana, PT. Sas Kreasindo Utama Applicant
{
    'name': "Integrasi Penjualan & Pembelian (Anjas Amar Pradana)",
    'version': '17.0',
    'summary': """
        Modul Tes Teknis untuk PT. SAS Kreasindo Utama.
        Dibuat oleh Anjas Amar Pradana.
        Modul ini menghubungkan Sales Order (SO) dengan Purchase Order (PO),
        menambahkan field kustom, validasi, dan fitur impor dari Excel.
    """,
    'author': 'Anjas Amar Pradana',
    'website': "https://www.linkedin.com/in/anjas-amar-pradana/",
    'category': 'Sales/Purchase',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'wizard/import_so_lines_wizard_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
