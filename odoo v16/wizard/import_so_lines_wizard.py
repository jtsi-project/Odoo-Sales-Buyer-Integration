# -*- coding: utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ImportSoLinesWizard(models.TransientModel):
    """
    This transient model (wizard) is used to import Sales Order lines from an Excel file.
    """
    _name = 'ancom_sales_orders.import.so.lines.wizard'
    _description = 'Import SO Lines Wizard'

    file_upload = fields.Binary(
        string='Upload File',
        required=True,
        help="Upload the Excel file with SO lines to import."
    )
    file_name = fields.Char(
        string='File Name',
        help="Name of the uploaded file."
    )

    def action_import_lines(self):
        """
        This is the main action of the wizard. It reads the uploaded Excel file,
        validates the data, and creates new Sales Order Lines.
        """
        self.ensure_one()

        # Get the active Sales Order record from the context.
        active_so_id = self.env.context.get('active_id')
        if not active_so_id:
            raise UserError("Could not find the active Sales Order. Please launch this wizard from a Sales Order form.")
        
        sale_order = self.env['sale.order'].browse(active_so_id)

        # Check if the SO is in a state that allows modification.
        if sale_order.state not in ['draft', 'sent']:
            raise UserError("You can only import lines to a Sales Order that is in 'Quotation' or 'Quotation Sent' state.")

        # Decode the file content from base64.
        try:
            file_data = base64.b64decode(self.file_upload)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
        except Exception as e:
            raise UserError(f"Error reading the Excel file. Please make sure it is a valid .xls or .xlsx file.\n\nError: {e}")

        so_lines_vals = []
        # Loop through rows, starting from the second row to skip the header.
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            
            # Extract data from the row.
            product_code = row[0]
            quantity = row[1]
            unit_price = row[2]

            # --- Data Validation ---
            if not product_code:
                raise ValidationError(f"Missing 'Product Code' in row {row_idx + 1}.")
            
            # Find the product by its 'default_code' (Internal Reference).
            product = self.env['product.product'].search([('default_code', '=', str(product_code))], limit=1)
            if not product:
                raise ValidationError(f"Product with code '{product_code}' not found (row {row_idx + 1}).")

            # --- Prepare SO Line Values ---
            line_vals = {
                'order_id': sale_order.id,
                'product_id': product.id,
                'product_uom_qty': float(quantity),
                'price_unit': float(unit_price),
            }
            so_lines_vals.append((0, 0, line_vals))

        # Create the SO lines by updating the 'order_line' field.
        if so_lines_vals:
            sale_order.write({'order_line': so_lines_vals})

        # Return an action to close the wizard.
        return {'type': 'ir.actions.act_window_close'}
