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


class gad_res_users(osv.osv):

    _inherit = 'res.users'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', u'Empleado'),
    }

    def _check_employee(self, cr, uid, ids):
        for partner in self.browse(cr, uid, ids):
            #import pdb
            #pdb.set_trace()
            if partner.id!=1 and not partner.employee_id:
                return False
            else:
                return True
        return True

    _constraints = [
        (_check_employee, 'Error de usuario, TODO usuario debe estar relacionado a un EMPLEADO', ['employee_id'])
        ]
    
    def onchange_employee(self, cr, uid, ids, employee_id, context={}):
        res = {}
        if employee_id:
            obj_employee = self.pool.get("hr.employee")
            empleado = obj_employee.browse(cr, uid, employee_id)
            res['value'] = {'name': empleado.name_related or ''}
        return res

gad_res_users()

