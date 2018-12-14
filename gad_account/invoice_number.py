# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>).
#    Application developed by: Carlos Andrés Ordóñez P.
#    Country: Ecuador
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import (
    models,
    fields,
    api
)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'state',
        'supplier_invoice_number'
    )
    def _get_invoice_number(self):
        if self.type == 'in_invoice':
            self.invoice_number = '{0}{1}{2}'.format(
                    self.auth_inv_id.serie_entidad,
                    self.auth_inv_id.serie_emision,
                    self.supplier_invoice_number and self.supplier_invoice_number or '*'
                )
        elif self.type == 'out_invoice':
            numero = str('1').zfill(9)
            regs = self.search([('auth_inv_id','=',self.auth_inv_id.id),('id','!=',self.id)], order='supplier_invoice_number desc')
            
            for reg in regs:
                #import pdb
                #pdb.set_trace()
                numero = reg.supplier_invoice_number #reg.invoice_number[6:]
                numero = int(numero) + 1
                numero = str(numero).zfill(9)
                continue
            self.invoice_number = '{0}{1}{2}'.format(
                self.auth_inv_id.serie_entidad,
                self.auth_inv_id.serie_emision,
                numero
            )
            self.supplier_invoice_number = numero
        else:
            self.invoice_number = '{0}{1}{2}'.format(
                self.auth_inv_id.serie_entidad,
                self.auth_inv_id.serie_emision,
                '-'
            )

    invoice_number = fields.Char(
        compute='_get_invoice_number',
        store=True,
        readonly=True,
        copy=False
    )

class ProductCategory(models.Model):
    _inherit = 'product.category'

    taxes_id = fields.Many2many(
            'account.tax', 'categ_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['sale', 'all'])])  # noqa
    supplier_taxes_id = fields.Many2many(
            'account.tax',
            'categ_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])])  # noqa