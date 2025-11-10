# -*- coding: utf-8 -*-
# Copyright 2025 - Anjas Amar Pradana, PT. Sas Kreasindo Utama Applicant
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    """
    Mewarisi sale.order untuk menambah field dan logika kustom terkait
    Pesanan Pembelian (Purchase Order) sesuai kebutuhan tes teknis.
    """
    _inherit = 'sale.order'

    # ===========================================================================
    # FIELDS (Requirement 1)
    # ===========================================================================

    # Req 1.1: Field untuk Vendor Permintaan (res.partner)
    x_request_vendor_id = fields.Many2one('res.partner', string='Vendor Permintaan',
                                          help="Vendor yang akan digunakan untuk Pesanan Pembelian.")

    # Req 1.2: Field untuk Nomor Kontrak (Char)
    x_no_kontrak = fields.Char(string='No Kontrak', copy=False,
                               help="Nomor kontrak yang terasosiasi dengan pesanan penjualan ini.")

    # Req 1.3: Field untuk Dengan PO (Boolean)
    x_with_po = fields.Boolean(string='Dengan PO', default=False,
                               help="Centang kotak ini untuk mengaktifkan fitur pembuatan Pesanan Pembelian.")

    # Req 1.5: Field One2many untuk relasi ke Pesanan Pembelian
    x_po_ids = fields.One2many('purchase.order', 'x_sale_order_id', string='Pesanan Pembelian',
                               readonly=True, help="Menampilkan semua Pesanan Pembelian yang dibuat dari Pesanan Penjualan ini.")

    # ===========================================================================
    # BUSINESS LOGIC (Requirement 2)
    # ===========================================================================

    # Req 2.3: Modifikasi logika tombol confirm untuk validasi 'No Kontrak'
    @api.model
    def action_confirm(self):
        """
        Meng-override aksi confirm untuk menambahkan validasi.
        Memastikan bahwa 'No Kontrak' unik di antara pesanan yang sudah terkonfirmasi.
        """
        for order in self:
            if order.x_no_kontrak:
                # Cari pesanan lain yang sudah terkonfirmasi dengan nomor kontrak yang sama.
                domain = [
                    ('x_no_kontrak', '=', order.x_no_kontrak),
                    ('id', '!=', order.id),
                    ('state', 'in', ['sale', 'done'])
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(_('No Kontrak "%s" sudah pernah diinputkan sebelumnya...!') % order.x_no_kontrak)
        return super(SaleOrder, self).action_confirm()

    # Req 2.1: Aksi tombol untuk membuat Pesanan Pembelian (PO)
    def action_create_po(self):
        """
        Metode ini dipicu oleh tombol 'Buat PO'.
        Membuat sebuah Purchase Order baru berdasarkan data dari Sales Order ini.
        """
        self.ensure_one()
        if not self.x_request_vendor_id:
            raise ValidationError(_('Silakan pilih "Vendor Permintaan" sebelum membuat Pesanan Pembelian.'))

        # Menyiapkan data untuk Pesanan Pembelian baru.
        po_vals = {
            'partner_id': self.x_request_vendor_id.id,
            'partner_ref': self.name,  # Referensi Vendor diambil dari nomor SO.
            'x_sale_order_id': self.id, # Relasi ke SO ini.
            'order_line': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'name': line.name,
                    'date_planned': fields.Date.today(),
                }) for line in self.order_line
            ]
        }
        po = self.env['purchase.order'].create(po_vals)

        # Mengembalikan action untuk membuka form view dari PO yang baru dibuat.
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }


class PurchaseOrder(models.Model):
    """
    Mewarisi purchase.order untuk menambahkan relasi Many2one kembali ke sale.order.
    Ini diperlukan agar field One2many di sale.order dapat berfungsi.
    """
    _inherit = 'purchase.order'

    # Field untuk menyimpan relasi ke sumber Sales Order
    x_sale_order_id = fields.Many2one('sale.order', string='Pesanan Penjualan Terkait',
                                      readonly=True, copy=False)
