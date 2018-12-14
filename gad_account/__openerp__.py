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
    'name': 'GAD - Contabilidad',
    'category': 'Accounting & Finance',
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['account',
                'account_accountant',
                'account_voucher',
                'account_budget',
                'gad_account_budget',
                'gad_project',
                'hr_payroll',
                'stock',
                'stock_account'],
    'version': '1.0',
    'description': """
Presupuesto, Contabilidad y Financiero  para Ecuador
=====================

    - Tipos de comprobante
    - Sustento comprobante
    - Empresas con RUC
    - Cuentas Contables con Relacion Presupuestaria

    """,

    'active': False,
    'data': [
             'security/ir.model.access.csv',
             'menu_view.xml',
             'res_partner_view.xml',
             #'sri_view.xml',
             'authorisation_view.xml',
             'data/account.ats.doc.csv',
             'data/account.ats.sustento.csv',
             'data/account.fiscal.position.csv',
             'invoice_workflow.xml',
             
             'invoice_view.xml',
             'account_view.xml',
             'budget_view.xml',
             #'retention_view.xml',
             'spi_voucher_view.xml',
             'report/asiento_contable.xml',
             'report/asiento_factura.xml',
             'report/comprobante_ie.xml',
             'report/spi_report.xml',
             'wizard/wizard_ats_view.xml',
             'wizard/wizard_report_view.xml',
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
