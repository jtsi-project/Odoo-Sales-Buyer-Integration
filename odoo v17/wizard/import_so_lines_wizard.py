# -*- coding: utf-8 -*-
# Copyright 2025 - Anjas Amar Pradana, PT. Sas Kreasindo Utama Applicant
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Coba impor library xlrd, yang dibutuhkan untuk membaca file .xls
try:
    import xlrd
except ImportError:
    xlrd = None

class ImportSOLinesWizard(models.TransientModel):
    """
    Wizard ini memungkinkan pengguna untuk mengimpor Baris Pesanan Penjualan (SO Lines)
    dari sebuah file Excel. Ini memenuhi Requirement 3 dari tes teknis.
    """
    _name = 'import.so.lines.wizard'
    _description = 'Wizard untuk Impor Baris Pesanan Penjualan'

    # ===========================================================================
    # FIELDS
    # ===========================================================================

    file_data = fields.Binary(string='Unggah File Anda', required=True,
                              help="File Excel yang akan diimpor (.xls atau .xlsx).")
    file_name = fields.Char(string='Nama File', help="Nama dari file yang diunggah.")

    # ===========================================================================
    # BUSINESS LOGIC (Requirement 3)
    # ===========================================================================

    def action_import_so_lines(self):
        """
        Metode ini dipicu oleh tombol 'Impor' di wizard.
        Membaca file Excel yang diunggah dan membuat record sale.order.line.
        """
        self.ensure_one()

        # Validasi
        if not self.file_data:
            raise UserError(_('Silakan unggah file untuk melanjutkan.'))
        if not xlrd:
            raise UserError(_('Library Python "xlrd" tidak terinstal. Silakan instal untuk menggunakan fitur ini.'))

        # Ambil record Sales Order yang aktif dari context.
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))

        try:
            # Decode data file base64 dan buka sebagai workbook Excel.
            book = xlrd.open_workbook(file_contents=base64.b64decode(self.file_data))
            sheet = book.sheet_by_index(0)
        except xlrd.XLRDError as e:
            raise UserError(_('Format file tidak didukung atau file rusak. Silakan gunakan file Excel yang valid. Error: %s') % e)
        except Exception as e:
            raise UserError(_('Terjadi kesalahan tak terduga saat membaca file: %s') % e)

        # Iterasi setiap baris dari sheet Excel, lewati baris header (index 0).
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)

            # Ekstrak data dari kolom: Kode Produk, Kuantitas, Harga Satuan
            product_code = row[0]
            try:
                quantity = float(row[1])
                unit_price = float(row[2])
            except (ValueError, IndexError):
                # Jika baris memiliki qty/harga non-numerik atau tidak lengkap, lewati.
                # Implementasi lebih lanjut bisa mencatat error ini.
                continue

            # Lewati baris jika kode produk kosong.
            if not product_code:
                continue

            # Cari produk di database menggunakan referensi internalnya (Kode Produk).
            product = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
            if not product:
                # Jika produk tidak ditemukan, lewati baris ini.
                # Versi lebih lanjut bisa memunculkan error atau membuat produk baru.
                continue

            # Buat Baris Pesanan Penjualan baru dengan data dari baris Excel.
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': product.id,
                'product_uom_qty': quantity,
                'price_unit': unit_price,
                'product_uom': product.uom_id.id, # Atur UoM default dari produk
                'name': product.name, # Atur deskripsi default dari produk
            })

        # Tutup wizard dan segarkan tampilan.
        return {'type': 'ir.actions.act_window_close'}
