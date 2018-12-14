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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools

class l10n_ec_hr_expenses(osv.osv):
    _name = 'hr.expenses'
    _description = 'Tipos de gastos para las proyecciones personales'
    _order = 'name'

    _columns = {
        'name': fields.char(u'Tipo de gasto', size=50, required=True),
        'description': fields.text(u'Descripción'),
    }

l10n_ec_hr_expenses()

class l10n_ec_hr_sri_taxable(osv.osv):
    
    _name = 'hr.sri.taxable'
    _description = 'Tabla de Base Imponible para calculo de impuesto a la renta'
    _order = 'name asc'    

    _columns = {
        'name': fields.char(u'Descripcion',required=True , size=40),
        'date_start': fields.date(u'Fecha de inicio'),
        'date_stop': fields.date(u'Fecha fin'),
        'taxable_lines': fields.one2many('hr.sri.taxable.line', 'taxable_id', u'Detalle de base imponible'),
        'expense_lines': fields.one2many('hr.sri.max_expense', 'taxable_id', u'Maximos deducibles'),
        }

    _defaults = {
        'name': 'Base Imponible',
        }


l10n_ec_hr_sri_taxable()

class l10n_ec_hr_sri_taxable_line(osv.osv):

    _name = 'hr.sri.taxable.line'
    _description = 'Lineas de Base Imponible para el cálculo de impuesto a la renta'

    _columns= {
        'basic_fraction': fields.float(u'Fracción Básica', required=True),
        'excess_to': fields.float(u'Exceso Hasta', required=True),
        'basic_fraction_tax': fields.float(u'Imp. Fracción Básica', required=True),
        'excess_fraction_percent': fields.float(u'% Fracción Excedente', required=True),
        'taxable_id': fields.many2one('hr.sri.taxable', u'Base imponible', ondelete='cascade'),
        }

l10n_ec_hr_sri_taxable_line()

class l10n_ec_hr_sri_max_expense(osv.osv):
    _name = 'hr.sri.max_expense'
    _description = 'Valor máximo a deducir por gastos personales'

    _columns = {
        'name': fields.many2one('hr.expenses', u'Tipo', required=True),
        'max_value': fields.float(u'Valor maximo deducible', required=True),
        'taxable_id': fields.many2one('hr.sri.taxable', u'Base imponible', ondelete='cascade'),
        }

l10n_ec_hr_sri_max_expense()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
