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
    'name': 'GAD - Presupuesto',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Este módulo permite el manejo de Presupuesto en el GAD
""",
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['account','account_budget','project','hr'],
    'data': [
        'report/budget_doc.xml',
        'report/budget_certificate.xml',
        'report/budget_reform.xml',
        'report/cedula_gastos.xml',
        'report/cedula_ingresos.xml',
        'report/estado_ejecucion.xml',
        'security/account_budget_security.xml',
        'security/ir.model.access.csv',
        'account_budget_sequence.xml',
        'account_budget_report.xml',
        'account_budget_view.xml',
        'wizard/wizard_budget_query_view.xml',
        #'account_budget_report.xml',
        #'wizard/account_budget_crossovered_report_view.xml',
        #'views/report_analyticaccountbudget.xml',
        #'views/report_budget.xml',
        #'views/report_crossoveredbudget.xml',
    ],
    #'demo': ['account_budget_demo.xml'],
    #'test': [
    #    'test/account_budget.yml',
    #    'test/account_budget_report.yml',
    #],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
