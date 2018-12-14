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
    'name': 'GAD - Activos Fijos',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Este módulo permite el manejo de Activos Fijos en el GAD
""",
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['account','account_asset','gad_payroll'],
    'data': [
       'account_asset_report.xml',
       'report/report_gad_account_asset_activo.xml',
       'report/report_gad_account_asset_transfer.xml',
       'report/report_gad_account_asset_baja.xml',
       'report/report_gad_account_asset_ingreso.xml',
       'report/report_gad_account_asset_tarjeta.xml',
       'report/report_gad_account_asset_certificado_no.xml',
       'wizard/wizard_gad_asset_view.xml', 
       'security/account_asset_security.xml',
       'security/ir.model.access.csv',
       'account_asset_view.xml',
     ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
