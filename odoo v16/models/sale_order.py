# -*- coding: utf-8 -*-

# Mengimpor modul yang diperlukan dari Odoo.
# 'models' digunakan untuk mendefinisikan model Odoo.
# 'fields' digunakan untuk mendefinisikan tipe field dalam model.
# 'api' menyediakan decorator dan utilitas untuk metode model.
from odoo import models, fields, api
# Mengimpor ValidationError untuk menangani kesalahan validasi kustom.
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """
    Kelas ini mewarisi model 'sale.order' untuk menambahkan field dan fungsionalitas baru
    sesuai dengan persyaratan tes teknis.
    """
    _inherit = 'sale.order'

    # ===================================================
    # DEFINISI FIELD (Persyaratan 1)
    # ===================================================

    x_request_vendor_id = fields.Many2one(
        'res.partner',
        string='Request Vendor', # Label field yang akan ditampilkan di antarmuka pengguna.
        # Domain untuk memfilter partner, hanya menampilkan yang ditandai sebagai vendor.
        domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]",
        help="Vendor yang akan digunakan untuk Purchase Order yang dibuat."
    )

    x_no_kontrak = fields.Char(
        string='No Kontrak', # Label field untuk nomor kontrak.
        copy=False,  # Field ini tidak boleh disalin saat menduplikasi Sales Order.
        help="Nomor kontrak unik untuk transaksi penjualan ini."
    )

    x_with_po = fields.Boolean(
        string='Dengan PO', # Label field untuk menunjukkan apakah PO diperlukan.
        default=False, # Nilai default field ini adalah False.
        help="Centang kotak ini jika Purchase Order perlu dibuat untuk Sales Order ini."
    )

    # Field One2many ini menghubungkan ke Purchase Order yang dibuat dari Sales Order ini.
    # Metode komputasi kustom '_compute_related_pos' digunakan untuk menemukan PO-PO ini.
    x_po_line_ids = fields.One2many(
        'purchase.order', # Model target untuk hubungan One2many.
        compute='_compute_related_pos', # Metode yang akan menghitung nilai field ini.
        string='Purchase Orders', # Label field untuk daftar Purchase Order.
        help="Menampilkan Purchase Order yang dibuat dari Sales Order ini."
    )

    # Field Integer ini menghitung jumlah Purchase Order yang terkait dengan Sales Order ini.
    # Ini ditambahkan untuk mengatasi kesalahan "Missing field string information".
    purchase_order_count = fields.Integer(
        string='Jumlah Purchase Order', # Label field untuk jumlah Purchase Order.
        compute='_compute_purchase_order_count', # Metode yang akan menghitung nilai field ini.
        help="Jumlah Purchase Order yang terhubung ke Sales Order ini."
    )

    # ===================================================
    # METODE KOMPUTASI
    # ===================================================

    @api.depends('x_po_line_ids') # Metode ini akan dijalankan setiap kali 'x_po_line_ids' berubah.
    def _compute_purchase_order_count(self):
        # Mengiterasi setiap Sales Order dalam recordset.
        for order in self:
            # Menghitung jumlah Purchase Order terkait dan menetapkannya ke field.
            order.purchase_order_count = len(order.x_po_line_ids)

    @api.depends('name') # Metode ini akan dijalankan setiap kali field 'name' berubah.
    def _compute_related_pos(self):
        """
        Metode komputasi ini menemukan semua Purchase Order yang dibuat dari Sales Order ini.
        Ini mencari Purchase Order di mana field 'origin' cocok dengan nama Sales Order ini.
        Ini adalah praktik standar Odoo untuk menghubungkan dokumen.
        """
        # Mengiterasi setiap Sales Order dalam recordset.
        for order in self:
            # Mencari Purchase Order yang memiliki nama Sales Order ini di field 'origin' mereka.
            related_pos = self.env['purchase.order'].search([('origin', '=', order.name)])
            # Menetapkan Purchase Order yang ditemukan ke field 'x_po_line_ids'.
            order.x_po_line_ids = related_pos

    # ===================================================
    # METODE AKSI (Persyaratan 2)
    # ===================================================

    def action_create_po(self):
        """
        Aksi ini dipicu oleh tombol 'Buat PO'. Ini membuat Purchase Order baru
        berdasarkan informasi dari Sales Order ini.
        """
        self.ensure_one()  # Memastikan metode ini dipanggil pada satu record saja.

        # Memeriksa apakah vendor telah dipilih.
        if not self.x_request_vendor_id:
            raise ValidationError("Mohon pilih 'Request Vendor' sebelum membuat Purchase Order.")

        # Menyiapkan nilai-nilai untuk Purchase Order baru.
        po_vals = {
            'partner_id': self.x_request_vendor_id.id, # Mengambil ID partner dari Request Vendor.
            'origin': self.name,  # Menghubungkan PO kembali ke SO.
            'partner_ref': self.name,  # Menetapkan Referensi Vendor dari nomor SO.
            'order_line': [], # Inisialisasi daftar baris order.
        }

        # Menyiapkan baris-baris untuk Purchase Order.
        for so_line in self.order_line:
            po_line_vals = {
                'product_id': so_line.product_id.id, # ID produk dari baris SO.
                'name': so_line.name, # Nama produk dari baris SO.
                'product_qty': so_line.product_uom_qty, # Kuantitas produk dari baris SO.
                'product_uom': so_line.product_uom.id, # Unit pengukuran produk dari baris SO.
                'price_unit': so_line.price_unit, # Harga satuan produk dari baris SO.
                'date_planned': fields.Datetime.now(), # Tanggal yang direncanakan untuk PO.
            }
            po_vals['order_line'].append((0, 0, po_line_vals)) # Menambahkan baris PO.

        # Membuat Purchase Order.
        purchase_order = self.env['purchase.order'].create(po_vals)

        # Mengembalikan aksi untuk membuka Purchase Order yang baru dibuat dalam tampilan formulir.
        return {
            'type': 'ir.actions.act_window', # Tipe aksi adalah membuka jendela.
            'res_model': 'purchase.order', # Model yang akan dibuka.
            'res_id': purchase_order.id, # ID record yang akan dibuka.
            'view_mode': 'form', # Mode tampilan adalah formulir.
            'target': 'current', # Membuka di jendela saat ini.
        }

    # ===================================================
    # METODE YANG DITIMPA (OVERRIDDEN METHODS) (Persyaratan 2)
    # ===================================================

    def action_confirm(self):
        """
        Metode ini menimpa (override) 'action_confirm' asli untuk menambahkan pemeriksaan validasi
        pada field 'No Kontrak'.
        """
        # Mengiterasi setiap Sales Order dalam recordset.
        for order in self:
            # Memeriksa hanya jika 'No Kontrak' telah diatur.
            if order.x_no_kontrak:
                # Mencari Sales Order lain dengan nomor 'No Kontrak' yang sama.
                # Kita mengecualikan record saat ini dari pencarian.
                domain = [
                    ('x_no_kontrak', '=', order.x_no_kontrak), # Mencari 'No Kontrak' yang sama.
                    ('id', '!=', order.id), # Mengecualikan ID record saat ini.
                ]
                existing_order = self.search(domain, limit=1) # Mencari satu record yang cocok.
                if existing_order:
                    # Jika ditemukan Sales Order dengan 'No Kontrak' yang sama, tampilkan pesan kesalahan.
                    raise ValidationError(
                        "No Kontrak sudah pernah diinputkan sebelumnya...!"
                    )

        # Jika validasi berhasil, panggil aksi konfirmasi asli.
        return super(SaleOrder, self).action_confirm()
