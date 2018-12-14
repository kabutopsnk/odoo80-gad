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
import datetime
import math
import calendar
from operator import attrgetter
from openerp.addons.gad_tools import easy_datetime
from openerp.tools.safe_eval import safe_eval as eval
from openerp import netsvc
from openerp.tools.translate import _

class l10n_ec_hr_holidays_configuration(osv.osv):
    _name = 'hr.holidays.configuration'
    _description = 'Configuracion de reglas para vacaciones'
    _columns = {
        'rule_vac_normal': fields.many2one('hr.salary.rule', u'Regla vacaciones tomadas', required=True),
        'rule_vac_normal_ajuste': fields.many2one('hr.salary.rule', u'Regla vacaciones tomadas - Ajuste', required=True),
        #'rule_bono_vac_normal': fields.many2one('hr.salary.rule', u'Regla bono vacaciones normales', required=True),
        #'rule_vac_extra': fields.many2one('hr.salary.rule', u'Regla vacaciones adicionales', required=True),
        #'rule_bono_vac_extra': fields.many2one('hr.salary.rule', u'Regla bono vacaciones adicionales', required=True),
        #'rule_novac_normal': fields.many2one('hr.salary.rule', u'Regla vacaciones no gozadas normales', required=True),
        #'rule_bono_novac_normal': fields.many2one('hr.salary.rule', u'Regla bono vacaciones no gozadas normales', required=True),
        'rule_novac_extra': fields.many2one('hr.salary.rule', u'Regla vacaciones adicionales - No gozadas', required=True),
        #'rule_bono_novac_extra': fields.many2one('hr.salary.rule', u'Regla bono vacaciones no gozadas adicionales', required=True),
    }

l10n_ec_hr_holidays_configuration()

class l10n_ec_hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    
    _order = 'name asc'
    
    _columns = {
                'code': fields.char(u'Codigo', size=15, help=u'Valor mediante el cual este tipo de ausencia será reconocido en las reglas salariales'),
                }

l10n_ec_hr_holidays_status()

class l10n_ec_hr_holidays(osv.osv):
    _inherit = "hr.holidays"

    _columns = {
        'date_from': fields.date(u'Fecha Inicio', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'date_to': fields.date(u'Fecha Fin', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        #'date_from_reference': fields.datetime(u'Fecha inicial real', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        #'date_to_reference': fields.datetime(u'Fecha final real', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        #'vacation_type': fields.selection([('normal','Normales'),('extra','Adicionales')],'Descontar de?', help=u'En caso que la ausencia sea descontada de vacaciones, debe indicar de cuales', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'employee_holidays': fields.many2one('hr.employee.holidays', u'Vacaciones asignadas al empleado', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'tax_value': fields.float(u'Valor Aportable', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'tax_value_ajuste': fields.float(u'Valor Aportable - Ajuste', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        #'notax_value': fields.float(u'Valor No Aportable',readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'calc_type': fields.selection([('calc','Calculados'),('digit','Digitados')], u'Valor a utilizar?', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'line_ids': fields.one2many('hr.io.line', 'holidays_id', u'Detalle', readonly=True),
        'date': fields.date(u'Fecha Solicitud', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
    }

    _order = "date_from desc, date_to asc"

    _defaults = {
        'calc_type': 'calc',
    }

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        #if date_from and not date_to:
        #    date_to_with_delta = datetime.datetime.strptime(date_from, '%Y-%m-%d')# + datetime.timedelta(hours=8)
        #    result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_vacation_type(self, cr, uid, ids, vacation_type, context={}):
        return {'value': {'employee_holidays':False}}

    def onchange_employee_holidays(self, cr, uid, ids, employee_holidays, days, calc_type, context={}):
        if not employee_holidays or not days or not calc_type:
            return {}
        emp_holidays = self.pool.get('hr.employee.holidays').browse(cr, uid, employee_holidays, context=context)
        if calc_type=='digit':
            ajuste = (emp_holidays.employee_id.contract_id.wage/30.0)*days
            return {'value': {'tax_value': (days*emp_holidays.tax_typed_value)/360.0,
                              'tax_value_ajuste': (ajuste>(days*emp_holidays.tax_typed_value)/360.0) and (ajuste-(days*emp_holidays.tax_typed_value)/360.0) or 0.0 }}
                              #'notax_value': (days*emp_holidays.notax_typed_value)/(24.0*15)}}
        if calc_type=='calc':
            ajuste = (emp_holidays.employee_id.contract_id.wage/30.0)*days
            return {'value': {'tax_value': (days*emp_holidays.tax_calc_value)/360.0, 
                              'tax_value_ajuste': (ajuste>(days*emp_holidays.tax_calc_value)/360.0) and (ajuste-(days*emp_holidays.tax_calc_value)/360.0) or 0.0 }}
                              #'notax_value': (days*emp_holidays.notax_calc_value)/(24.0*15)}}
        return {}

    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'] = {'department_id': employee.department_id.id, 'employee_holidays':False}
            #print {'department_id': employee.department_id.id, 'employee_holidays':False, 'nombre': employee.name_related}
        return result

    def holidays_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'class': 'confidential'
                }   
                #Add the partner_id (if exist) as an attendee             
                if record.user_id and record.user_id.partner_id:
                    meeting_vals['partner_ids'] = [(4,record.user_id.partner_id.id)]
                    
                ctx_no_email = dict(context or {}, no_email=True)
                meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=ctx_no_email)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                for leave_id in leave_ids:
                    # TODO is it necessary to interleave the calls?
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)
            if record.employee_holidays:
                conf_obj = self.pool.get('hr.holidays.configuration')
                line_obj = self.pool.get('hr.io.line')
                conf_ids = conf_obj.search(cr, uid, [], context=context)
                if not conf_ids:
                    raise osv.except_osv(u'Operación no permitida!', u'No existe tabla de configuración de las reglas de vacaciones')
                conf = conf_obj.browse(cr, uid, conf_ids[0], context=context)
                fecha_inicial = datetime.datetime.strptime(record.date_from, "%Y-%m-%d")
                fecha_final = datetime.datetime.strptime(record.date_to, "%Y-%m-%d")
                line_ids = line_obj.search(cr, uid, [('holidays_id','=',record.id),('state','in',('draft','send'))], context=context)
                line_obj.write(cr, uid, line_ids, {'state':'draft'}, context=context)
                line_obj.unlink(cr, uid, line_ids, context=context)
                while fecha_final.month != fecha_inicial.month:
                    ultimo_dia = calendar.monthrange(fecha_inicial.year,fecha_inicial.month)[1]
                    dias_mes = 1 + ultimo_dia - fecha_inicial.day
                    tax_val_mes = ((record.tax_value or 0.0)/record.number_of_days_temp)*dias_mes
                    tax_val_mes_ajuste = ((record.tax_value_ajuste or 0.0)/record.number_of_days_temp)*dias_mes
                    if record.tax_value>0:
                      line_obj.create(cr, uid, {'employee_id': record.employee_id.id,
                                      'value': tax_val_mes,
                                      'rule_id': conf.rule_vac_normal.id,
                                      'holidays_id': record.id,
                                      'date': fecha_inicial,
                                      'biweekly': False,
                                      'state': 'send',
                                      'label': str(dias_mes) + 'd',
                                      })
                    if record.tax_value_ajuste>0:
                      line_obj.create(cr, uid, {'employee_id': record.employee_id.id,
                                      'value': tax_val_mes_ajuste,
                                      'rule_id': conf.rule_vac_normal_ajuste.id,
                                      'holidays_id': record.id,
                                      'date': fecha_inicial,
                                      'biweekly': False,
                                      'state': 'send',
                                      'label': str(dias_mes) + 'd',
                                      })
                    fecha_inicial = datetime.datetime(year=fecha_inicial.year, month=fecha_inicial.month, day=ultimo_dia)
                    fecha_inicial = fecha_inicial + datetime.timedelta(days=1)
                dias_mes = 1 + fecha_final.day - fecha_inicial.day
                tax_val_mes = ((record.tax_value or 0.0)/record.number_of_days_temp)*dias_mes
                tax_val_mes_ajuste = ((record.tax_value_ajuste or 0.0)/record.number_of_days_temp)*dias_mes
                if record.tax_value>0:
                      line_obj.create(cr, uid, {'employee_id': record.employee_id.id,
                                      'value': tax_val_mes,
                                      'rule_id': conf.rule_vac_normal.id,
                                      'holidays_id': record.id,
                                      'date': fecha_inicial,
                                      'biweekly': False,
                                      'state': 'send',
                                      'label': str(dias_mes) + 'd',
                                      })
                if record.tax_value_ajuste>0:
                      line_obj.create(cr, uid, {'employee_id': record.employee_id.id,
                                      'value': tax_val_mes_ajuste,
                                      'rule_id': conf.rule_vac_normal_ajuste.id,
                                      'holidays_id': record.id,
                                      'date': fecha_inicial,
                                      'biweekly': False,
                                      'state': 'send',
                                      'label': str(dias_mes) + 'd',
                                      })
        return True

    def holidays_cancel(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            # Delete the meeting
            if record.meeting_id:
                record.meeting_id.unlink()

            # If a category that created several holidays, cancel all related
            self.signal_workflow(cr, uid, map(attrgetter('id'), record.linked_request_ids or []), 'refuse')

            # borrar los ingresos
            line_obj = self.pool.get('hr.io.line')
            line_ids = line_obj.search(cr, uid, [('holidays_id','=',record.id),('state','in',('draft','send'))], context=context)
            line_obj.write(cr, uid, line_ids, {'state':'draft'}, context=context)
            line_obj.unlink(cr, uid, line_ids, context=context)

        self._remove_resource_leave(cr, uid, ids, context=context)
        return True

    def _check_max_days(self, cr, uid, ids):
        #import pdb
        #pdb.set_trace()
        for reg in self.browse(cr, uid, ids):
            if reg.state == 'validate':
                if reg.employee_holidays:
                    if reg.number_of_days_temp > (reg.employee_holidays.days_normal_avai + reg.employee_holidays.days_extra_avai):
                        return False
        return True

    def _check_last_period(self, cr, uid, ids):
        #import pdb
        #pdb.set_trace()
        for reg in self.browse(cr, uid, ids):
            if reg.state == 'validate':
                if reg.employee_holidays:
                    for periodo in reg.employee_holidays.employee_id.employee_holiday_ids:
                        if periodo.id !=reg.employee_holidays.id:
                            if (periodo.date_end < reg.employee_holidays.date_end) and (periodo.days_normal_avai + periodo.days_extra_avai) > 0:
                                return False
        return True

    _constraints = [
        (_check_max_days, u'\nNo puede solicitar más días de los disponibles en el periodo', ['number_of_days_temp','employee_holidays','state']),
        (_check_last_period, u'\nNo puede solicitar vacaciones de este periodo, tiene disponible un periodo anterior', ['number_of_days_temp','employee_holidays','state']),
        ]


l10n_ec_hr_holidays()

class l10n_ec_employee_holidays(osv.osv):
    _name = 'hr.employee.holidays'
    _description = 'Detalle de vacaciones asignadas al empleado'

    def name_get(self, cr, uid, ids, context={}):
        if not ids:
            return []
        try:
            flag = len(ids)
        except:
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name + ' [' + str(record.date_start) + ' - ' + str(record.date_end) + '] (No.:' + str(record.days_normal_avai) + ' - Ad.:' + str(record.days_extra_avai) + ')'
            res.append((record.id, name))
        return res

    def _compute_holidays(self, cr, uid, ids, fields, args, context={}):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'days_normal_used': 0,
                           'days_extra_used': 0,
                           'days_normal_avai': (obj.days_normal - obj.days_s_normal_used),
                           'days_extra_avai': (obj.days_extra - obj.days_s_extra_used),}
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('employee_id','=',obj.employee_id.id), ('state','=','validate'),('employee_holidays','=',obj.id),('type','=','remove')], order='id asc')
            for holiday in self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context):
                dias = holiday.number_of_days_temp
                if dias > res[obj.id]['days_normal_avai'] and res[obj.id]['days_normal_avai']>0:
                    dias = dias - res[obj.id]['days_normal_avai']
                    res[obj.id]['days_normal_used'] += res[obj.id]['days_normal_avai']
                    res[obj.id]['days_normal_avai'] -= res[obj.id]['days_normal_avai']
                if dias <= res[obj.id]['days_normal_avai']:
                    res[obj.id]['days_normal_used'] += dias
                    res[obj.id]['days_normal_avai'] -= dias
                    dias = 0
                if dias > res[obj.id]['days_extra_avai'] and res[obj.id]['days_extra_avai']>0:
                    dias = dias - res[obj.id]['days_extra_avai']
                    res[obj.id]['days_extra_used'] += res[obj.id]['days_extra_avai']
                    res[obj.id]['days_extra_avai'] -= res[obj.id]['days_extra_avai']
                if dias <= res[obj.id]['days_extra_avai']:
                    res[obj.id]['days_extra_used'] += dias
                    res[obj.id]['days_extra_avai'] -= dias
                    dias = 0
                res[obj.id]['days_normal_used'] += dias
                res[obj.id]['days_normal_avai'] -= dias
            holiday_sold_ids = self.pool.get('hr.holidays.sold').search(cr, uid, [('name','=',obj.employee_id.id), ('state','in',('send','paid')),('employee_holidays','=',obj.id)], order='date asc')
            for holidays_sold in self.pool.get('hr.holidays.sold').browse(cr, uid, holiday_sold_ids, context=context):
                res[obj.id]['days_normal_used'] += holidays_sold.days
                res[obj.id]['days_normal_avai'] -= holidays_sold.days
                res[obj.id]['days_extra_used'] += holidays_sold.days_extra
                res[obj.id]['days_extra_avai'] -= holidays_sold.days_extra
        return res

    def _compute_holidays_value(self, cr, uid, ids, fields, args, context={}):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=',obj.employee_id.id),('date_to','>=',obj.date_start),('date_to','<=',obj.date_end),('payroll_type','=','monthly')], context=context)
            res[obj.id] = {'tax_calc_value': 0,
                           'notax_calc_value': 0,
                           'description_calc': ''}
            for payslip in self.pool.get('hr.payslip').browse(cr, uid, payslip_ids, context=context):
                res[obj.id]['description_calc'] = res[obj.id]['description_calc'] +  "\nRol mensual " + str(payslip.date_from) + " - " + str(payslip.date_to)
                for line in payslip.line_ids:
                  if line.category_id.code in ('BASIC','APT') and line.code[:4] not in ('AJUS') and line.code not in ('FRESERVA','BALIMENTACION'):
                    res[obj.id]['tax_calc_value'] += line.amount
                  #if line.category_id.code in ('ING') and line.code[:4] not in ('AJUS') and line.code[:8] not in ('FRESERVA'):
                  #if line.code == 'BALIMENTACION':
                  #  res[obj.id]['notax_calc_value'] += line.amount
        return res

    def _get_holidays(self, cr, uid, ids, context={}):
        result = {}
        for record in self.pool.get('hr.holidays').browse(cr, uid, ids, context=context):
            if record.state=='validate':
                result[record.employee_holidays.id] = True
        return result.keys()

    def _get_holidays_sold(self, cr, uid, ids, context={}):
        result = {}
        for record in self.pool.get('hr.holidays.sold').browse(cr, uid, ids, context=context):
            if record.state in ('send','paid'):
                result[record.employee_holidays.id] = True
        return result.keys()


    STORE_HOLIDAYS = {'hr.employee.holidays': (lambda self, cr, uid, ids, c={}: ids, ['days_normal', 'days_extra', 'days_s_normal_used', 'days_s_extra_used'], 10),
                      'hr.holidays': (_get_holidays, ['state', 'number_of_days_temp', 'employee_holidays'], 20),
                      'hr.holidays.sold': (_get_holidays_sold, ['state', 'days', 'days_extra', 'employee_holidays'], 20),}

    
    _columns = {
                'name': fields.char(u'Descripción', size=64, required=True),
                'employee_id': fields.many2one('hr.employee', u'Empleado', ondelete='cascade', required=True),
                'date_start': fields.date(u'Fecha inicial periodo', required=True),
                'date_end': fields.date(u'Fecha final periodo', required=True),
                'days_normal': fields.float(u'Vacaciones Asig.'),
                'days_extra': fields.float(u'Adicionales Asig.'),
                'days_s_normal_used': fields.float(u'Vac. Usadas (Saldo)'),
                'days_s_extra_used': fields.float(u'Ad. Usadas (Saldo)'),
                'days_normal_used': fields.function(_compute_holidays, string=u'Vac. Usadas', method=True, store=STORE_HOLIDAYS, multi='employee_holidays'),
                'days_extra_used': fields.function(_compute_holidays, string=u'Ad. Usadas', method=True, store=STORE_HOLIDAYS, multi='employee_holidays'),
                'days_normal_avai': fields.function(_compute_holidays, string=u'Vac. Disponibles', method=True, store=STORE_HOLIDAYS, multi='employee_holidays'),
                'days_extra_avai': fields.function(_compute_holidays, string=u'Ad. Disponibles', method=True, store=STORE_HOLIDAYS, multi='employee_holidays'),
                'tax_typed_value': fields.float(u'Aportable digitado'),
                #'notax_typed_value': fields.float(u'No Aportable digitado'),
                'tax_calc_value': fields.function(_compute_holidays_value, string=u'Aportable calculado', method=True, store=False, multi='employee_holidays_value'),
                #'notax_calc_value': fields.function(_compute_holidays_value, string=u'No Aportable calculado', method=True, store=False, multi='employee_holidays_value'),
                'description_calc': fields.function(_compute_holidays_value, string=u'Detalle del calculo', method=True, store=False, multi='employee_holidays_value', type='text'),
                #'assigned_holidays_id' : fields.many2one('hr.holidays', 'Asignación de Vacaciones normales', required=True, readonly=True),
                #'assigned_holidays_extra_id' : fields.many2one('hr.holidays', 'Asignación de Vacaciones adicionales', required=True, readonly=True),
                }
    
    _defaults = {
                 'days_normal': 0,
                 'days_extra': 0,
                 'days_s_normal_used': 0,
                 'days_s_extra_used': 0,
                 'tax_typed_value': 0,
                 #'notax_typed_value': 0,
                 }

    _order = 'date_end desc'


    def cron_compute_holidays(self, cr, uid, context=None):
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('hr.employee.holidays')
        time_actual = datetime.datetime.today()
        ids_contratos = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),
                                                      '|',
                                                      ('date_end','>=',str(time_actual)),
                                                      ('date_end','=',False)])
        #import pdb
        #pdb.set_trace()
        for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
          time_contrato = datetime.datetime.strptime(contrato.date_holidays and contrato.date_holidays or contrato.date_start, "%Y-%m-%d")
          if time_contrato.day==time_actual.day and time_contrato.month==time_actual.month and time_contrato.year!=time_actual.year:
            periodo_fin = datetime.datetime(year=time_actual.year, month=time_actual.month, day=time_actual.day)
            periodo_inicio = datetime.datetime(year=time_actual.year-1, month=time_actual.month, day=time_actual.day)
            periodo_fin = periodo_fin - datetime.timedelta(days=1)
            localdict = {'employee': contrato.employee_id, 'contract': contrato, 'easy_datetime': easy_datetime}
            dias_normales = 0
            dias_adicionales = 0
            try:
                eval(contrato.type_id.python_normal, localdict, mode='exec', nocopy=True)
                dias_normales = localdict['result']
                eval(contrato.type_id.python_extra, localdict, mode='exec', nocopy=True)
                dias_adicionales = localdict['result']
            except:
                raise osv.except_osv(u'Error de cómputo', u'Las expresiones python para el cómputo de vacaciones, es erroneo')
            nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
            ids_periodo = obj_periodo.search(cr, uid, [('date_start','=',periodo_inicio),
                                                       ('date_end','=',periodo_fin),
                                                       ('employee_id','=',contrato.employee_id.id)])
            if not ids_periodo:
                ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
                                                            'employee_id': contrato.employee_id.id,
                                                            'date_start': periodo_inicio,
                                                            'date_end': periodo_fin,})]
                obj_periodo.write(cr, uid, ids_periodo, {'days_normal':dias_normales,
                                                         'days_extra':dias_adicionales,
                                                         })
    
l10n_ec_employee_holidays()

class l10n_ec_hr_employee_holidays(osv.osv):
    _inherit = 'hr.employee'

    def _compute_holidays(self, cr, uid, ids, fields, args, context={}):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'days_normal': 0,'days_extra': 0,}
            for line in obj.employee_holiday_ids:
                res[obj.id]['days_normal'] += line.days_normal_avai
                res[obj.id]['days_extra'] += line.days_extra_avai
        return res
    
    _columns = {
                'employee_holiday_ids': fields.one2many('hr.employee.holidays', 'employee_id', u'Detalle de Asignación de Vacaciones'),
                'days_normal': fields.function(_compute_holidays, string=u'Vacaciones Disponibles', method=True, store=False, multi='employee_holidays'),
                'days_extra': fields.function(_compute_holidays, string=u'Adicionales Disponibles', method=True, store=False, multi='employee_holidays'),
                }

l10n_ec_hr_employee_holidays()

class l10n_ec_hr_contract_type_holidays(osv.osv):
    _inherit = 'hr.contract.type'
    _columns = {
        'python_normal': fields.text(u'Formula para dias normales'),
        'python_extra': fields.text(u'Formula para dias adicionales'),
    }
    _defaults = {
        'python_normal': '''# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# easy_datetime: date and time functions

# Note: returned value have to be set in the variable 'result'

result = 0''',
        'python_extra': '''# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# easy_datetime: date and time functions

# Note: returned value have to be set in the variable 'result'

result = 0''',
    }
l10n_ec_hr_contract_type_holidays()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
