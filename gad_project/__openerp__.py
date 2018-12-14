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
    'name': 'GAD - Proyectos',
    'version': '1.0',
    'author': 'Carlos Andrés Ordóñez P.',
    'category': 'Project Management',
    'depends': [
        'project',
        'gad_account_budget',
    ],
    'description': """
Este módulo permite la Gestión de Proyectos, Actividades y Presupuesto anual en el GAD
    """,
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'project_report.xml',
        'report/report_contrato_hoja_garantia.xml',
        'report/report_contrato_garantia_oficio_renovacion.xml',
        'report/report_contrato_garantia_oficio_ejecucion.xml',
        'wizard/wizard_project_view.xml',
        'project_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
