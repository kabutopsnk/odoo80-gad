# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'GAD - Gestión de Compras',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Este módulo permite la Gestión de Compras y Requerimientos
""",
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['purchase_requisition'],
    'data': [
       'security/purchase_security.xml',
       'security/ir.model.access.csv',
       'purchase_report.xml',
       'report/report_purchaseorder.xml',
       'report/report_solicitud_compra.xml',
       'wizard/wizard_gad_purchase_view.xml', 
       'purchase_sequence.xml',
       'purchase_view.xml',
     ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
