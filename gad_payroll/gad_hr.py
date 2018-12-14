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
import unicodedata
import datetime


class ec_hr_job(osv.osv):
    _inherit = 'hr.job'
    _order = 'name asc'

    _columns = {
        'active': fields.boolean(u'Activo'),
    }

    _defaults = {
        'active': True,
    }

ec_hr_job()

class ec_hr_department(osv.osv):
    _inherit = 'hr.department'
    _order = 'name asc'

    _columns = {
        'active': fields.boolean(u'Activo'),
    }

    _defaults = {
        'active': True,
    }


ec_hr_department()

class ec_hr_grupos_cuentas(osv.osv):
    _name = 'hr.grupos_cuentas'
    _description = 'Grupos Contables utilizada para exportar Rol de Pagos'
    _order = 'name asc'

    _columns = {
        #'code': fields.char(u'Código', size=24, required=True),
        'name': fields.char(u'Grupo', size=100, required=True),
        'account_id': fields.many2one('account.account', u'Cuenta Contable', help='Coloque una cuenta en este casillero en caso que todo el rubro se refleje en ella, sin diferenciar el Proyecto.'),
        #'cuenta_sobregiro': fields.many2one('hr.cuenta_contable', u'Cuenta Sobregiro', help='Coloque un numero de cuenta en este casillero en caso que el rubro sea menor a cero, sin diferenciar el Centro de Costo.'),
        'line_ids': fields.one2many('hr.grupos_linea', 'grupo_id', u'Detalle'),
    }

ec_hr_grupos_cuentas()

class ec_hr_grupos_linea(osv.osv):
    _name = 'hr.grupos_linea'
    _description = 'Detalle del Grupo Contable utilizado para exportar Rol de Pagos'
    _order = 'project_id, task_id, budget_line_id'

    _columns = {
                'grupo_id': fields.many2one('hr.grupos_cuentas', u'Grupo de cuentas', required=True, ondelete='cascade'),
                'budget_line_id': fields.many2one('crossovered.budget.lines', u'Partida Presupuestaria', required=True),
                'project_id': fields.related('budget_line_id', 'project_id', type='many2one', relation='project.project', string= u'Proyecto', store=True),
                'task_id': fields.related('budget_line_id', 'task_id', type='many2one', relation='project.task', string= u'Actividad', store=True),
                'account_id': fields.many2one('account.account', u'Cuenta Contable', required=True),
                #'cuenta_haber': fields.many2one('hr.cuenta_contable', u'Cuenta Haber'),
    }

ec_hr_grupos_linea()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
