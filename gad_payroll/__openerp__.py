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
    'name': 'GAD - Talento Humano',
    'category': 'Localization/Payroll',
    'author': 'Carlos Andrés Ordóñez P.',
    'depends': ['hr_payroll','gad_tools'],
    'version': '1.0',
    'description': """
Talento Humano para Ecuador
=====================

    - Empleados con 2 nombres y 2 apellidos
    - Cédula como nombre de empleado
    - Cargas familiares, permitiendo descuentos de la Función Judicial
    - Aplicación del impuesto a la renta, fórmula en rol de pagos, como deducciones de gastos personales
    - Ingresos y Egresos adicionales
    - Fórmula de aportes al IESS
    - Fórmula de fondos de reserva

    """,

    'active': False,
    'data': [
             'security/ir.model.access.csv',
             'gad_hr_view.xml',
             'gad_res_country_view.xml',
             'gad_income_tax_view.xml',
             'gad_employee_view.xml',
             'gad_contract_view.xml',
             'gad_holidays_view.xml',
             'gad_hr_io_view.xml',
             'gad_payroll_view.xml',
             'gad_res_users_view.xml',
             'gad_marcaciones_view.xml',
             #'res_partner_view.xml',
             'wizard/gad_payroll_payslips_by_employees_view.xml',
             'wizard/gad_io_import_xls_view.xml',
             'wizard/gad_he_import_xls_view.xml',
             'wizard/gad_import_employee_projection_view.xml',
             'wizard/archivo_iess_view.xml',
             'wizard/modificar_salario_view.xml',
             #'wizard/exportar_asiento_view.xml',
             #'wizard/exportar_provisiones_view.xml',
             'report/report.xml',
             'report/solicitud_ausencia.xml',
             'report/rol_individual.xml',
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
