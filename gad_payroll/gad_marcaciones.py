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

from openerp.osv import osv, fields
#import time
from datetime import datetime
from datetime import timedelta

_STATE = [('draft','Borrador'),('send','Pendiente'),('done','Registrado'),('cancel','Cancelado')]


class ec_hr_he_config(osv.osv):
    _name = 'hr.mark.config'
    _description = u'Configuración de Horas Extra'

    _columns = {
        #'max_week_h50': fields.float(u'Máximo Semanal Horas Extra %50', required=True),
        #'date_start': fields.date(u'Desde', required=True),
        #'date_stop': fields.date(u'Hasta', required=True),
        'h100_start': fields.float(u'Horas 100% desde las', required=True),
        'h100_stop': fields.float(u'Horas 100% hasta las', required=True),
        'holiday_ids': fields.one2many('hr.mark.holidays', 'config_id', u'Feriados'),
        'period_ids': fields.one2many('hr.mark.period', 'config_id', u'Periodos'),
        'rule_h50': fields.many2one('hr.salary.rule', u'Rubro H50'),
        'rule_h100': fields.many2one('hr.salary.rule', u'Rubro H100'),
        'rule_falta': fields.many2one('hr.salary.rule', u'Rubro Falta'),
        }

ec_hr_he_config()

class ec_hr_mark_holidays(osv.osv):
    _name = 'hr.mark.holidays'
    _description = u'Días Feriados'

    _columns = {
        'day': fields.date(u'Día Feriado', required=True),
        'description': fields.char(u'Descripción', required=True, size=50),
        'config_id': fields.many2one('hr.mark.config', u'Cabecera de Configuración', ondelete='cascade'),
        }
    
    _order = "day desc"

ec_hr_mark_holidays()

class ec_hr_mark_period(osv.osv):
    _name = 'hr.mark.period'
    _description = u'Periodos de marcaciones'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        diccionario = {'draft':'Borrador', 'active':'Activo', 'cerrado':'Closed'}
        for this in self.browse(cr, uid, ids, context=context):
            name = diccionario[this.state] + ": " + str(this.date_start) + " a " + str(this.date_stop)
            res.append((this.id, name))
        return res

    _columns = {
        'date_start': fields.date(u'Desde?', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'date_stop': fields.date(u'Hasta?', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'date': fields.date(u'Aplica en?', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft','Borrador'),('active','Activo'),('closed','Cerrado')], u'Estado', required=True, readonly=True),
        'config_id': fields.many2one('hr.mark.config', u'Cabecera de Configuración', ondelete='cascade'),
        'day_ids': fields.one2many('hr.mark.day', 'period_id', u'Registros diarios'),
        'io_ids': fields.one2many('hr.io.line', 'mark_id', u'Rubros'),
        }
    
    _order = "date_stop desc, date_start desc"

    _defaults = {
        'state': 'draft',
        }
    
    def draft_to_active(self, cr, uid, ids, context={}):
        for this in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, this.id, {'state': 'active'}, context=context)
            
    def active_to_draft(self, cr, uid, ids, context={}):
        for this in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, this.id, {'state': 'draft'}, context=context)
            
    def active_to_closed(self, cr, uid, ids, context={}):
        res={}
        obj_lines = self.pool.get('hr.io.line')
        obj_days = self.pool.get('hr.mark.day')
        for this in self.browse(cr, uid, ids, context=context):
            if not this.config_id.rule_h50 or not this.config_id.rule_h100 or not this.config_id.rule_falta:
                raise osv.except_osv(u'Error de Configuración', u'Debe configurar las reglas para horas extra y faltas')
            line_ids = obj_lines.search(cr, uid, [('mark_id','=',this.id)])
            if line_ids:
                obj_lines.unlink(cr, uid, line_ids)
            for check in this.day_ids:
                if check.state=='send':
                    if res.has_key(check.employee_id.id):
                        pass
                    else:
                        res[check.employee_id.id] = {'h50':0.0, 'h100':0.0, 'faltas':0.0}
                    res[check.employee_id.id]['h50'] += check.val_h50
                    res[check.employee_id.id]['h100'] += check.val_h100
                    if check.marcaciones == 'FALTA':
                        res[check.employee_id.id]['faltas'] += 1
                obj_days.write(cr, uid, check.id, {'state':'done'})
            for key in res.keys():
                if res[key]['h50']>0:
                    obj_lines.create(cr, uid, {'employee_id': key,
                                               'value': res[key]['h50'],
                                               'rule_id': this.config_id.rule_h50.id,
                                               'mark_id': this.id,
                                               'date': this.date,
                                               'state': 'send',
                                               #'label': record.label,
                                               })
                if res[key]['h100']>0:
                    obj_lines.create(cr, uid, {'employee_id': key,
                                               'value': res[key]['h100'],
                                               'rule_id': this.config_id.rule_h100.id,
                                               'mark_id': this.id,
                                               'date': this.date,
                                               'state': 'send',
                                               #'label': record.label,
                                               })
                if res[key]['faltas']>0:
                    obj_lines.create(cr, uid, {'employee_id': key,
                                               'value': res[key]['faltas'],
                                               'rule_id': this.config_id.rule_falta.id,
                                               'mark_id': this.id,
                                               'date': this.date,
                                               'state': 'send',
                                               #'label': record.label,
                                               })
            self.write(cr, uid, this.id, {'state': 'closed'})

ec_hr_mark_period()


class hr_mark_check(osv.osv_memory):
    _name = 'hr.mark.check'
    _description = u'Buscar las marcaciones del jefe'
    
    _columns = {
                'period_id': fields.many2one('hr.mark.period', u'Periodo', required=True),
                'user_id': fields.many2one('res.users', u'Usuario', readonly=True, required=True),
                }
    
    _defaults = {
                 'user_id': lambda self, cr, uid, context={}: uid,
                 }
    
    def cargar_marcaciones(self, cr, uid, ids, context={}):
        #group_id = self.pool.get("hr.mark.group").search(cr, uid, [('user_id','=',uid)])
        
        mark_obj = self.pool.get('hr.mark')
        day_obj = self.pool.get('hr.mark.day')
        obj_contrato = self.pool.get("hr.contract")
        #if not group_id:
        #    raise osv.except_osv("Error!", "Su usuario no está asignado como jefe para aprobación de marcaciones.")
        #grupo = self.pool.get('hr.mark.group').browse(cr, uid, group_id[0])
        for this in self.browse(cr, uid, ids, context=context):
            if this.period_id.state=='active':
                day_from = datetime.strptime(this.period_id.date_start,"%Y-%m-%d")
                day_to = datetime.strptime(this.period_id.date_stop,"%Y-%m-%d")
                nb_of_days = (day_to - day_from).days + 1
                for day in range(0, nb_of_days):
                    dia = day_from + timedelta(days=day)
                    ids_contratos = obj_contrato.search(cr, uid, [('date_start','<=',str(dia)),
                                                      '|',
                                                      ('date_end','>=',str(dia)),
                                                      ('date_end','=',False)])
                    for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
                    #for empleado in grupo.employee_ids:
                        if contrato.working_hours:
                            #import pdb
                            #pdb.set_trace()
                            marcaciones_ids = mark_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),('state','=','draft'),('datetime_mark','>=', str(dia)),('datetime_mark','<=', str(dia + timedelta(days=1))),])
                            day_id = day_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),('state','=','draft'),('date','=',dia)])
                            if not day_id:
                                day_id = day_obj.create(cr, uid, {'employee_id': contrato.employee_id.id,
                                                                  'period_id': this.period_id.id,
                                                                  'calendar_id': contrato.working_hours.id,
                                                                  'date': dia})
                            else:
                                day_id = day_id[0]
                            if marcaciones_ids:
                                mark_obj.write(cr, uid, marcaciones_ids, {'day_id': day_id})
                            else:
                                #aqui en caso de no encontrar marcaciones
                                pass
                        else:
                            #aqui el caso que el empleado no tenga asignado un horario
                            pass
            else:
                #Aqui en caso que se use un periodo inactivo
                pass
            #context['search_default_group_employee'] = 1
            return {
                    'name':"Aprobación de Marcaciones",
                    #'view_id': False,
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'res_model': 'hr.mark.day',
                    #'res_id': sep_id,
                    'type': 'ir.actions.act_window',
                    #'nodestroy': True,
                    #'target': 'new',
                    'domain': "[('date','>=','" + str(this.period_id.date_start) + "'),('date','<=','" + str(this.period_id.date_stop) + "')]",
                    'context': context,
                    }


hr_mark_check()

"""class ec_hr_head(osv.osv):
    _name = 'hr.mark.head'
    _description = u'Marcaciones por empleado para aprobar'

    _columns = {
        'user_id': fields.many2one('res.users', u'Usuario', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        #'date': fields.date(u'Día', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date(u'Aplica hasta?', required=True, readonly=True, states={'draft': [('readonly', False)]}, help=u'Esta fecha indicará el periodo de rol de pagos en el que se aplicarán los valores calculados'),
        'max_week_h50': fields.float(u'Máximo de Horas Extra %50', required=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection(_STATE, u'Estado', readonly=True),
        'day_ids': fields.one2many('hr.mark.day', 'head_id', u'Registros diarios'),
        #'description': fields.char(u'Descripción', size=200, readonly=True, states={'draft': [('readonly', False)]}, help=u'Debe indicar el motivo para aprobar las horas extras correspondientes a este día.'),
        }

    _order = "date desc, user_id asc"

    def _get_max_week_h50(self, cr, uid, context=None):
        obj_config = self.pool.get('hr.mark.config')
        config = obj_config.browse(cr, uid, 1, context=context)
        if config:
            return config.max_week_h50
        else:
            raise osv.except_osv("Error!", "No se encuentra la configuración de Horas Extra.")
        
    def _get_date(self, cr, uid, context=None):
        obj_config = self.pool.get('hr.mark.config')
        config = obj_config.browse(cr, uid, 1, context=context)
        if config:
            return config.date
        else:
            raise osv.except_osv("Error!", "No se encuentra la configuración de Horas Extra.")

    _defaults = {
                 'max_week_h50': _get_max_week_h50,
                 'date': _get_date,
                 'state': 'draft',
                 'user_id': lambda self, cr, uid, context={}: uid,
                 }

    def cargar_marcaciones(self, cr, uid, ids, context={}):
        group_id = self.pool.get("hr.mark.group").search(cr, uid, [('user_id','=',uid)])
        mark_obj = self.pool.get('hr.mark')
        day_obj = self.pool.get('hr.mark.day')
        if not group_id:
            raise osv.except_osv("Error!", "Su usuario está asignado como jefe para aprobación de marcaciones.")
        #print 'select employee_id from he_user_employee_group where group_id=' + str(group_id[0])
        cr.execute('select employee_id from he_user_employee_group where group_id=' + str(group_id[0]) )
        res = cr.fetchall()
        for this in self.browse(cr, uid, ids, context=context):
            empleados = {}
            for empleado_id in res:
                marcaciones_ids = mark_obj.search(cr, uid, [('employee_id','=',empleado_id[0]),('state','=','draft'),('datetime_start','<=', this.date),('datetime_stop','!=',False)])
                empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id, context=context)
                #print marcaciones_ids
                for marcacion in mark_obj.browse(cr, uid, marcaciones_ids):
                    dia = datetime.strptime(marcacion.datetime_start[:10], "%Y-%m-%d")
                    #print dia
                    day_id = day_obj.search(cr, uid, [('employee_id','=',empleado_id[0]),('state','=','draft'),('date','=',dia)])
                    if not day_id:
                        if empleado.contract_id.working_hours:
                            day_id = day_obj.create(cr, uid, {'employee_id': empleado_id[0],
                                                              'head_id': this.id,
                                                              'calendar_id': empleado.contract_id.working_hours.id,
                                                              'date': dia})
                        else:
                            continue
                    else:
                        day_id = day_id[0]
                    #print day_id
                    mark_obj.write(cr, uid, marcacion.id, {'day_id': day_id})

ec_hr_head()"""

class ec_hr_day(osv.osv):
    _name = 'hr.mark.day'
    _description = u'Marcaciones de empleado por día'
    
    def draft_to_send(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'send'})
        
    def send_to_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'draft'})
    
    def _calculo_dia(self, cr, uid, ids, fields, args, context={}):
        res = {}
        config = self.pool.get('hr.mark.config').browse(cr,uid,1,context=context)
        h100_inicio = config.h100_start*3600
        h100_fin = config.h100_stop*3600
        for this in self.browse(cr, uid, ids, context):
            dia = datetime.strptime(this.date, "%Y-%m-%d")
            res[this.id] = {'marcaciones': '',
                            'h25':0,
                            'h50':0,
                            'h100':0}
            if dia.weekday()==5 and not this.mark_ids:
                res[this.id]['marcaciones'] += 'Sábado\n'
            if dia.weekday()==6 and not this.mark_ids:
                res[this.id]['marcaciones'] += 'Domingo\n'
            bandera = False
            for linea in this.calendar_id.attendance_ids:
                if str(linea.dayofweek) == str(dia.weekday()):
                    bandera = True
            if bandera == True and not this.mark_ids:
                res[this.id]['marcaciones'] = 'FALTA'
            contador = 0
            for marcacion in this.mark_ids:
                contador += 1
                if contador/2.0 != contador//2.0:
                    marcacion_inicio = datetime.strptime(marcacion.datetime_mark, "%Y-%m-%d %H:%M:%S")
                    marcacion_inicio = marcacion_inicio + timedelta(hours=-5)
                    res[this.id]['marcaciones'] += 'EntradaR' + str(marcacion.reloj) + '[' + str(marcacion_inicio)[11:] + ']\n'
                else:
                    marcacion_fin = datetime.strptime(marcacion.datetime_mark, "%Y-%m-%d %H:%M:%S")
                    marcacion_fin = marcacion_fin + timedelta(hours=-5)
                    segundos_inicio = marcacion_inicio.hour*3600.0 + marcacion_inicio.minute*60.0 + marcacion_inicio.second 
                    segundos_fin = (24*3600*(marcacion_fin.day-marcacion_inicio.day)) + (marcacion_fin.hour*3600) + (marcacion_fin.minute*60) + marcacion_fin.second
                    diferencia = marcacion_fin - marcacion_inicio
                    diferencia = diferencia.seconds
                    #import pdb
                    #pdb.set_trace()
                    h100 = 0
                    for linea in this.calendar_id.attendance_ids:
                        #print 1
                        #print "Mark: " + str(linea.dayofweek) + " - Dia: " + str(dia.weekday())
                        if str(linea.dayofweek) == str(dia.weekday()):
                            #print 2
                            #import pdb
                            #pdb.set_trace()
                            horario_inicio = linea.hour_from*3600
                            horario_fin = linea.hour_to*3600
                            if horario_fin<horario_inicio:
                                horario_fin += 24*3600
                            if segundos_inicio < horario_inicio:
                                if segundos_fin < horario_inicio:
                                    pass # no pasa nada
                                else: #if segundos_fin >= horario_inicio:
                                    if segundos_fin <= horario_fin: # si hi sf hf
                                        diferencia -= (segundos_fin - horario_inicio)
                                    else: #segundos_fin > horario_fin: # si hi hf sf
                                        diferencia -= (horario_fin - horario_inicio)
                            else: #if segundos_inicio >= horario_inicio:
                                if segundos_inicio <= horario_fin:
                                    if segundos_fin <= horario_fin: # hi si sf hf
                                        diferencia -= (segundos_fin - segundos_inicio)
                                    else: #segundos_fin > horario_fin: # hi si hf sf
                                        diferencia -= (horario_fin - segundos_inicio)
                                else: #if segundos_inicio > horario_fin:
                                    pass # no pasa nada
                    #para cruzar con el horario, debo tabular
                    #import pdb
                    #pdb.set_trace()
                    hora100_inicio = config.h100_stop*3600.0# - 5*3600.0
                    hora100_fin = config.h100_start*3600.0# - 5*3600.0
                    if hora100_inicio>segundos_inicio:
                        h100 += hora100_inicio - segundos_inicio
                    if hora100_fin<segundos_fin:
                        h100 += segundos_fin - hora100_fin
                    diferencia -= h100
                    res[this.id]['h50'] += diferencia/3600.0
                    res[this.id]['h100'] += h100/3600.0
                    res[this.id]['marcaciones'] += 'SalidaR' + str(marcacion.reloj) + '[' + str(marcacion_fin)[11:] + ']\n'
        return res

    _columns = {
        'employee_id': fields.many2one('hr.employee', u'Empleado', readonly=True, required=True),
        #'head_id': fields.many2one('hr.mark.head', u'Cabecera de Aprobaciones', readonly=True, required=True),
        'period_id': fields.many2one('hr.mark.period', u'Periodo', required=True),
        'date': fields.date(u'Día', required=True, readonly=True),
        #'date_apply': fields.datetime(u'Aplica en?', readonly=True, states={'draft': [('readonly', False)]}, help=u'Esta fecha indicará el periódo de rol de pagos en el que se aplicarán los valores calculados'),
        'state': fields.selection(_STATE, u'Estado', readonly=True),
        'mark_ids': fields.one2many('hr.mark', 'day_id', u'Marcaciones', readonly=True),
        #'description': fields.char(u'Descripción', size=200, readonly=True, states={'draft': [('readonly', False)]}, help=u'Debe indicar el motivo para aprobar las horas extras correspondientes a este día.'),
        'marcaciones': fields.function(_calculo_dia, method=True, multi='day_calc', string=u'Marcaciones', type='char', store=False),
        'calendar_id': fields.many2one('resource.calendar', u'Horario', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'h25': fields.float(u'C H25', required=True, readonly=True),
        'h50': fields.function(_calculo_dia, method=True, multi='day_calc', string=u'C H50', type='float', store=False),
        'h100': fields.function(_calculo_dia, method=True, multi='day_calc', string=u'C H100', type='float', store=False),
        'val_h50': fields.float(u'A H50', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'val_h100': fields.float(u'A H100', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        }

    _order = "date desc, employee_id asc"

    _defaults = {
       'state': 'draft',
       'h25': 0.00,
       'h50': 0.00,
       'h100': 0.00,
       'val_h25': 0.00,
       'val_h50': 0.00,
       'val_h100': 0.00,
       #'user_id': lambda self, cr, uid, context={}: uid,
        }

    def write(self, cr, uid, ids, vals, context={}):
        pass
        if vals.has_key('description'):
            config = self.pool.get('hr.mark.config').browse(cr, uid, 1, context=context)
            for this in self.browse(cr, uid, ids, context=context):
                dia = datetime.strptime(this.date, "%Y-%m-%d")
                
        return super(ec_hr_day, self).write(cr, uid, ids, vals, context=context)

ec_hr_day()


class ec_hr_mark(osv.osv):
    _name = 'hr.mark'
    _description = u'Marcación de empleado'

    _columns = {
        'employee_id': fields.many2one('hr.employee', u'Empleado', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'day_id': fields.many2one('hr.mark.day', u'Día', readonly=True, states={'draft': [('readonly', False)]}),
        #'datetime_start': fields.datetime(u'Marcación entrada', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #'datetime_stop': fields.datetime(u'Marcación salida', readonly=True, states={'draft': [('readonly', False)]}),
        'datetime_mark': fields.datetime(u'Marcación', readonly=True, states={'draft': [('readonly', False)]}),
        #'type': fields.selection([('Entrada','Entrada'),('Salida','Salida')], u'Tipo', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'reloj': fields.char(u'Reloj', size=3, states={'draft': [('readonly', False)]}),
        'state': fields.selection(_STATE, u'Estado', readonly=True),
        }

    _order = "datetime_mark asc"

    _defaults = {
       'state': 'draft',
        }
    
    _sql_constraints = [('unique_mark', 'unique(employee_id,datetime_mark,reloj)', u'No puede registrar la misma marcacion mas de 1 vez')]

ec_hr_mark()

