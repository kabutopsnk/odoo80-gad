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

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class l10n_ec_hr_payslip_employees(osv.osv_memory):

    _inherit ='hr.payslip.employees'

    _columns = {
        'contract_ids': fields.many2many('hr.contract', 'hr_contract_group_rel', 'payslip_id', 'contract_id', 'Contratos'),
        'different_structure': fields.many2one('hr.payroll.structure', 'Aplicar otra estructura', help='Seleccionar en el caso que desee que se aplique otra estructura de salario diferente a la del contrato del servidor'),
#        'employee_ids': fields.many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees'),
#        'contract_type_id': fields.many2one('hr.contract.type','Tipo de contrato'),
        'date_start': fields.date('date start'),
        'date_end': fields.date('date end'),
        #'servicios_complementarios': fields.boolean(u'Servicios Complementarios'),
        'payroll_type': fields.selection([('monthly', u'Mensual'),('bi-weekly', u'Quincenal'),('decimotercero', u'Décimo Tercero'),('decimotercero', u'Décimo Cuarto'),('utilidades', u'Utilidades')], 'Tipo de rol', required=True, readonly=True),
        'rule_category_ids': fields.many2many('hr.salary.rule.category', 'hr_payslipemployees_rulecategory_rel', 'payslip_employees_id', 'category_id', string='Categorias de entradas?', help='Indicar las categorias que se añadirán como entradas al rol'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        obj_contrato = self.pool.get('hr.contract')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note', 'biweekly'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        #biweekly = run_data.get('biweekly', False)
        servicios=False
        if data.has_key('payroll_type'):
          if data['payroll_type']=='utilidades':
            servicios=True
        if servicios==False:
          if not data['contract_ids']:
            raise osv.except_osv(_("Advertencia !"), _("Debe seleccionar al menos 1 empleado para elaborar el rol"))
          #for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
          context['rule_category_ids'] = data['rule_category_ids']
          context['payroll_type'] = data['payroll_type']
          if data.has_key('different_structure'):
            if data['different_structure']!=False:
                context['different_structure'] = data['different_structure']
          for contrato in obj_contrato.browse(cr, uid, data['contract_ids'], context=context):
            emp = contrato.employee_id
            payslip_ids = slip_pool.search(cr, uid, [('payslip_run_id','=',context.get('active_id', False)),('employee_id','=',emp.id),('contract_id','=',contrato.id)])
            if payslip_ids:
                slip_pool.unlink(cr, uid, payslip_ids)
            context.update({'contract':True})
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=contrato.id, context=context)
            department_id = contrato.department_id.id
            job_id = contrato.job_id.id
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': data['different_structure']!=False and data['different_structure'][0] or contrato.struct_id.id,
                'contract_id': contrato.id,
                'company_id': slip_data['value'].get('company_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'department_id': department_id,
                'job_id': job_id,
                'payroll_type': data['payroll_type'],
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        if servicios==True:
          if not data['employee_ids']:
            raise osv.except_osv(_("Advertencia !"), _("Debe seleccionar al menos 1 empleado para elaborar el rol"))
          context['rule_category_ids'] = data['rule_category_ids']
          context['payroll_type'] = data['payroll_type']
          if data.has_key('different_structure'):
            if data['different_structure']!=False:
                context['different_structure'] = data['different_structure']
          for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            payslip_ids = slip_pool.search(cr, uid, [('payslip_run_id','=',context.get('active_id', False)),('employee_id','=',emp.id)])
            if payslip_ids:
                slip_pool.unlink(cr, uid, payslip_ids)
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context, struct_id=data['different_structure'][0])
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': data['different_structure']!=False and data['different_structure'][0] or None,
                'contract_id': slip_data['value'].get('contract_id', False),
                'company_id': slip_data['value'].get('company_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'department_id': slip_data['value'].get('contract_id', False)==True and self.pool.get("hr.contract").browse(cr, uid, slip_data['value'].get('contract_id', False)).department_id.id or None,
                'job_id': slip_data['value'].get('contract_id', False)==True and self.pool.get("hr.contract").browse(cr, uid, slip_data['value'].get('contract_id', False)).job_id.id or None,
                'payroll_type': data['payroll_type'],
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))

        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def get_date_start(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        return payroll.date_start

    def get_date_end(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        return payroll.date_end

    def get_payroll_type(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        return payroll.payroll_type

    def get_category_rules(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        categories = []
        for categ in payroll.rule_category_ids:
            categories.append(categ.id)
        return categories

    _defaults = {
#                'contract_type_id': get_contract_type,
                'date_start': get_date_start,
                'date_end': get_date_end,
                'payroll_type': get_payroll_type,
                'rule_category_ids': get_category_rules,
                'servicios_complementarios': False,
                }

l10n_ec_hr_payslip_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
