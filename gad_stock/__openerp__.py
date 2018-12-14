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
{
    'name': 'GAD - Inventarios',
    'category': 'Warehouse Management',
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['gad_account', 'stock', 'stock_account'],
    'version': '1.0',
    'description': """
Inventarios para Empresa Pública de Ecuador
=====================

    - Ingresos en Bodega
    - Egresos en Bodega
    - Costo Promedio

    """,

    'active': False,
    'data': [
             'security/ir.model.access.csv',
             'report/report_stockpicking.xml',
             'product_view.xml',
             'stock_view.xml',
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
