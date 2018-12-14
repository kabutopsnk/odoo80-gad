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
from time import strftime
import datetime

_STATE = [('draft','Borrador'),('send','Pendiente'),('paid','Pagado'),('cancel','Cancelado')]

class l10n_ec_hr_io_head(osv.osv):
    _name = 'hr.io.head'
    _description = 'Cabecera de ingresos/egresos para el rol de pagos'

    def _get_summary(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        obj_contract = self.pool.get('hr.contract')
        for reg in self.browse(cr, uid, ids, context=context):
            res[reg.id] = ''
            for line in reg.line_ids:
                contract_ids = obj_contract.search(cr, uid, [('employee_id','=',line.employee_id.id),('date_start','<=',str(line.date)),'|',('date_end','>=',str(line.date)),('date_end','=',False)])
                if not contract_ids:
                    res[reg.id] += "\n" + line.employee_id.name_related + ": NO tiene contrato activo el " + str(line.date)
        return res
    
    def modificar_etiquetas(self, cr, uid, ids, context={}):
        if uid==1:
            obj_linea = self.pool.get('hr.io.line')
            obj_plinea = self.pool.get('hr.payslip.input')
            for this in self.browse(cr, uid, ids, context=context):
                for linea in this.line_ids:
                    obj_linea.write(cr, uid, linea.id, {'label':str(linea.value)+'h'}, context=context)
                    ids_plineas = obj_plinea.search(cr, uid, [('io_id','=',linea.id)], context=context)
                    if ids_plineas:
                        obj_plinea.write(cr, uid, ids_plineas, {'label':str(linea.value)+'h'}, context=context)
        else:
            raise osv.except_osv(('Operación no permitida !'), ('Esta acción solamente puede realizarla el administrador del sistema'))
    

    _columns = {
        'rule_id': fields.many2one('hr.salary.rule',u'Regla Salarial', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'date':  fields.date(u'Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', u'Departamento', readonly=True, states={'draft': [('readonly', False)]}),
        'value': fields.float(u'Valor', help=u"En caso de usar 'Cargar Empleados', este valor se aplicará para todos", readonly=True, states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('hr.io.line', 'head_id',u'Detalle', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection(_STATE, u'Estado', readonly=True),
        'label': fields.char(u'Etiqueta', size=50, readonly=True, states={'draft': [('readonly', False)]}),
        #'biweekly': fields.boolean(u'Anticipo Quincenal?', help=u'Marcar el casillero en el caso que el rubro pertenezca al anticipo', readonly=True, states={'draft': [('readonly', False)]}),
        'summary': fields.function(_get_summary, store=False, string='Resumen', type='text', readonly=True),
        }

    _order = "date desc, rule_id, department_id, state"

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state != 'draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operación en estado Borrador'))
            for linea in this.line_ids:
                if linea.state!='draft':
                    raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operación si todas las líneas se encuentran en estado borrador'))
        return super(l10n_ec_hr_io_head, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.rule_id.name + " - " + str(record.date)
            res.append((record.id, name))
        return res
    
    def load_employees(self, cr, uid, ids, context=None):
        con_obj=self.pool.get('hr.contract')
        line_pool=self.pool.get('hr.io.line')
        for reg in self.browse(cr, uid, ids, context=context):
            old_line_ids = line_pool.search(cr, uid, [('head_id','=',reg.id)], context=context)
            self.unlink(cr, uid, old_line_ids, context=context)
            co_ids = []
            if reg.department_id:
                    co_ids = con_obj.search(cr, uid,[('department_id','=',reg.department_id.id),
                                                     ('date_start','<=',reg.date),
                                                     '|',
                                                     ('date_end','>=',reg.date),
                                                     ('date_end','=',False)])
            else:
                    co_ids = con_obj.search(cr, uid,[('date_start','<=',reg.date),
                                                     '|',
                                                     ('date_end','>=',reg.date),
                                                     ('date_end','=',False)])
            if co_ids:
                    for con in con_obj.browse(cr, uid, co_ids, context=context):
                            val={}
                            val['head_id'] = reg.id
                            val['employee_id'] = con.employee_id.id
                            val['value'] = reg.value
                            val['rule_id'] = reg.rule_id.id
                            val['date'] = reg.date
                            val['label'] = reg.label
                            line_pool.create(cr, uid, val,context=context)
            else:
                    raise osv.except_osv(('Advertencia!'), ('No existen empleados activos en esta fecha'))

    def load_wizard_xls(self, cr, uid, ids, context=None):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Importar XLS',
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'wizard.import.hr.io.head',
        'nodestroy': True,
        'target': 'new',
        'context': context,
        }

    def send_to_draft(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
            for line in this.line_ids:
                if line.state=='send':
                    line_obj.write(cr, uid, line.id, {'state':'draft'})

    def draft_to_send(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'send'})
            for line in this.line_ids:
                if line.state=='draft':
                    etiqueta = line.label and line.label or ''
                    if this.label:
                        etiqueta = this.label
                    line_obj.write(cr, uid, line.id,{'state':'send', 'label':etiqueta, 'rule_id': this.rule_id.id, 'date':this.date})

    _defaults = {
       'state': 'draft',
       #'biweekly': False,
       'date': lambda self, cr, uid, context={}: strftime("%Y-%m-%d"),
        }

l10n_ec_hr_io_head()

class l10n_ec_hr_io_amortize(osv.osv):
    _name = 'hr.io.amortize'
    _description = 'Cabecera de amortizacion de ingreso/egreso para rol de pagos'

    _columns = {
        'rule_id': fields.many2one('hr.salary.rule',u'Regla Salarial', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'employee_id': fields.many2one('hr.employee',u'Empleado', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'date':  fields.date(u'Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'value': fields.float(u'Valor', help="En caso de usar 'Cargar Empleados', este valor se aplicará para todos", readonly=True, states={'draft': [('readonly', False)]}),
        'num_payments': fields.integer(u'Número de pagos', help=u"Indicar la cantidad de pagos en los cuales se dividirá el valor", readonly=True, states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('hr.io.line', 'amortize_id',u'Detalle', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft','Borrador'),('send','Pendiente'),('paid','Pagado'),('refinance','Refinanciado'),('cancel','Cancelado')], u'Estado', readonly=True),
        #'biweekly': fields.boolean(u'Anticipo Quincenal?', help=u'Marcar el casillero en el caso que el rubro pertenezca al anticipo', readonly=True, states={'draft': [('readonly', False)]}),
        }

    _order = "date desc, rule_id, state"

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(u'Operación no permitida !', u'No puede eliminar, solo puede realizar esta operación en estado Borrador')
            for linea in this.line_ids:
                if linea.state!='draft':
                    raise osv.except_osv(u'Operación no permitida !', u'No puede eliminar, solo puede realizar esta operación si todas las líneas se encuentran en estado borrador')
        return super(l10n_ec_hr_io_amortize, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.employee_id.name_related + " - " + record.rule_id.name + " - " + str(record.date)
            res.append((record.id, name))
        return res
    
    def calculate_lines(self, cr, uid, ids, context={}):
        line_obj = self.pool.get('hr.io.line')
        for obj in self.browse(cr, uid, ids, context=context):
            ids_unlink = []
            for linea in obj.line_ids:
                if linea.state=='draft':
                    ids_unlink.append(linea.id)
            line_obj.unlink(cr, uid, ids_unlink, context=context)
            if obj.num_payments > 1:
                value = obj.value/(obj.num_payments*1.00)
                value = float("%.2f" % value)
                date_from = datetime.datetime.strptime(obj.date, "%Y-%m-%d")
                next_date = date_from
                for number in range(obj.num_payments):
                    if number == (obj.num_payments - 1):
                        value = obj.value - (value*number)
                        #print "asdasdasd"
                    line_obj.create(cr, uid, {
                                              'employee_id': obj.employee_id.id,
                                              'value': value,
                                              'rule_id': obj.rule_id.id,
                                              'amortize_id': obj.id,
                                              'date': date_from,
                                              #'biweekly': False,
                                              'label': 'Pago '+str(number+1)+'/'+str(obj.num_payments),
                                              })
                    dia = date_from.day > 28 and 28 or date_from.day
                    mes = (date_from.month < 12) and date_from.month+1 or 1
                    anio = (date_from.month < 12) and date_from.year or date_from.year+1
                    date_from = datetime.datetime(year=anio, month=mes, day=dia)
            else:
                raise osv.except_osv(u'Operación no permitida!', u'No se puede realizar una tabla de amortización si la cantidad de pagos es menor a 2')

    def send_to_draft(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
            for line in this.line_ids:
                if line.state=='send':
                    line_obj.write(cr, uid, line.id, {'state':'draft'})


    def draft_to_send(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'send'})
            for line in this.line_ids:
                if line.state=='draft':
                    line_obj.write(cr, uid, line.id,{'state':'send'})

    def send_to_cancel(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'cancel'})
            for line in this.line_ids:
                if line.state=='send':
                    line_obj.write(cr, uid, line.id,{'state':'cancel'})

    def send_to_paid(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'paid'})
            for line in this.line_ids:
                if line.state=='send':
                    line_obj.write(cr, uid, line.id,{'state':'paid'})

    def send_to_refinance(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        subtotal = 0
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'refinance'})
            for line in this.line_ids:
                if line.state=='send':
                    subtotal += line.value
                    line_obj.write(cr, uid, line.id, {'state':'cancel'})
            refinance_id = self.create(cr, uid, {
                                                 'rule_id': this.rule_id.id,
                                                 'value': subtotal,
                                                 'date': strftime("%Y-%m-%d"),
                                                 'employee_id': this.employee_id.id,
                                                 'state':'draft',
                                                 #'biweekly': this.biweekly,
                                                 })
            return {
                    'type': 'ir.actions.act_window',
                    'name': 'Ingresos/Egresos Amortizados',
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'hr.io.amortize',
                    'res_id': refinance_id,
                    'context': context,
                    }


    _defaults = {
       'state': 'draft',
       #'biweekly': False,
       'date': lambda self, cr, uid, context={}: strftime("%Y-%m-%d"),
        }

l10n_ec_hr_io_amortize()

class l10n_ec_hr_holidays_sold(osv.osv):
    _name = "hr.holidays.sold"
    _STATE = [('draft','Borrador'),('send','Pendiente'),('paid','Pagado'),('cancel','Cancelado')]
    _columns = {
        'name': fields.many2one('hr.employee', u'Empleado', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date(u'Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'days': fields.integer(u'Cantidad dias normales', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'days_extra': fields.integer(u'Cantidad dias adicionales', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection(_STATE, 'Estado', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #'vacation_type': fields.selection([('normal','Normales'),('extra','Adicionales')], 'Descontar de?', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'employee_holidays': fields.many2one('hr.employee.holidays', u'Descontar de?', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'tax_value': fields.float(u'Valor normal Aportable', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'notax_value': fields.float(u'Valor normal No Aportable', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'tax_value_extra': fields.float(u'Valor extra Aportable', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'notax_value_extra': fields.float(u'Valor extra No Aportable', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #'calc_type': fields.selection([('calc','Calculados'),('digit','Digitados')], 'Valor a utilizar?', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('hr.io.line', 'holidays_sold_id', u'Detalle', readonly=True),
        'label': fields.char(u'Etiqueta', size=50, readonly=True, states={'draft': [('readonly', False)]}),
    }

    _order = "date desc, name"

    _defaults = {
       'state': 'draft',
       'date': lambda self, cr, uid, context={}: strftime("%Y-%m-%d"),
       'days': 0,
       'days_extra': 0,
       }

    def draft_to_send(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'send'})
            for line in this.line_ids:
                if line.state=='draft':
                    line_obj.write(cr, uid, line.id,{'state':'send'})

    def send_to_draft(self, cr, uid, ids, context=None):
        line_obj=self.pool.get('hr.io.line')
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, this.id,{'state':'draft'})
            for line in this.line_ids:
                if line.state=='send':
                    line_obj.write(cr, uid, line.id, {'state':'draft'})

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(u'Operación no permitida !', u'No puede eliminar, solo puede realizar esta operación en estado Borrador')
            for linea in this.line_ids:
                if linea.state!='draft':
                    raise osv.except_osv(u'Operación no permitida !', u'No puede eliminar, solo puede realizar esta operación si todas las líneas se encuentran en estado borrador')
        return super(l10n_ec_hr_holidays_sold, self).unlink(cr, uid, ids, *args, **kwargs)

    def onchange_employee_holidays(self, cr, uid, ids, days, days_extra, employee_id, context={}):
        if not employee_id:
            return {}
        #emp_holidays = self.pool.get('hr.employee.holidays').browse(cr, uid, employee_holidays, context=context)
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        return {'value': {'tax_value': (days*employee.contract_id.wage)/(30.0),
                          'notax_value': (days*employee.contract_id.bono_alimentacion)/(30.0),
                          'tax_value_extra': (days_extra*employee.contract_id.wage)/(30.0),
                          'notax_value_extra': (days_extra*employee.contract_id.bono_alimentacion)/(30.0)}}

    def onchange_employee(self, cr, uid, ids, context={}):
        return {'value': {'employee_holidays':False, 'tax_value':0, 'notax_value':0, 'tax_value_extra':0, 'notax_value_extra':0}}

    def recalculate(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.io.line')
        conf_obj = self.pool.get('hr.holidays.configuration')
        conf_ids = conf_obj.search(cr, uid, [], context=context)
        if not conf_ids:
            raise osv.except_osv(('Operación no permitida!'), ('No existe tabla de configuración de las reglas de vacaciones'))
        conf = conf_obj.browse(cr, uid, conf_ids[0], context=context)
        for record in self.browse(cr, uid, ids, context=context):
          line_ids = line_obj.search(cr, uid, [('holidays_sold_id','=',record.id),('state','in',('draft','send'))], context=context)
          line_obj.unlink(cr, uid, line_ids, context=context)
          if record.tax_value>0:
            line_obj.create(cr, uid, {'employee_id': record.name.id,
                                      'value': record.tax_value or 0.0,
                                      'rule_id': conf.rule_novac_normal.id,
                                      'holidays_sold_id': record.id,
                                      'date': record.date,
                                      #'biweekly': False,
                                      'state': record.state,
                                      'label': record.label,
                                      })
          if record.notax_value>0:
            line_obj.create(cr, uid, {'employee_id': record.name.id,
                                      'value': record.notax_value or 0.0,
                                      'rule_id': conf.rule_bono_novac_normal.id,
                                      'holidays_sold_id': record.id,
                                      'date': record.date,
                                      #'biweekly': False,
                                      'state': record.state,
                                      'label': record.label,
                                      })
          if record.tax_value_extra>0:
            line_obj.create(cr, uid, {'employee_id': record.name.id,
                                      'value': record.tax_value_extra or 0.0,
                                      'rule_id': conf.rule_novac_extra.id,
                                      'holidays_sold_id': record.id,
                                      'date': record.date,
                                      #'biweekly': False,
                                      'state': record.state,
                                      'label': record.label,
                                      })
          if record.notax_value_extra>0:
            line_obj.create(cr, uid, {'employee_id': record.name.id,
                                      'value': record.notax_value_extra or 0.0,
                                      'rule_id': conf.rule_bono_novac_extra.id,
                                      'holidays_sold_id': record.id,
                                      'date': record.date,
                                      #'biweekly': False,
                                      'state': record.state,
                                      'label': record.label,
                                      })
        return True

l10n_ec_hr_holidays_sold()


class l10n_ec_hr_io_line(osv.osv):
   _name = 'hr.io.line'
   _description = 'Lineas de ingresos/egresos para el rol de pagos'

   def send_to_draft(self, cr, uid, ids, context=None):
       for this in self.browse(cr, uid, ids):
           self.write(cr, uid, this.id,{'state':'draft'})
           
   def draft_to_send(self, cr, uid, ids, context=None):
       for this in self.browse(cr, uid, ids):
           self.write(cr, uid, this.id,{'state':'send'})

   def create(self, cr, uid, values, context=None):
       if values.has_key('head_id'):
               obj_head = self.pool.get('hr.io.head')
               head = obj_head.browse(cr, uid, values['head_id'], context)
               values['date'] = head.date
               values['rule_id'] = head.rule_id.id
       return super(l10n_ec_hr_io_line, self).create(cr, uid, values, context=context)

   def write_resp(self, cr, uid, ids, values, context=None):
       if values.has_key('head_id'):
               obj_head = self.pool.get('hr.io.head')
               head = obj_head.browse(cr, uid, values['head_id'], context)
               values['date'] = head.date
               values['rule_id'] = head.rule_id.id
       return super(l10n_ec_hr_io_line, self).create(cr, uid, values, context=context)
   
   def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state!='draft':
                raise osv.except_osv(u'Operación no permitida !', u'No puede eliminar, solo puede realizar esta operación en estado Borrador')
        return super(l10n_ec_hr_io_line, self).unlink(cr, uid, ids, *args, **kwargs)

   def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.employee_id.name_related + " - " + record.rule_id.name + " - " + str(record.date)
            res.append((record.id, name))
        return res

   def _get_summary(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        obj_contract = self.pool.get('hr.contract')
        for line in self.browse(cr, uid, ids, context=context):
                res[line.id] = ''
                contract_ids = obj_contract.search(cr, uid, [('employee_id','=',line.employee_id.id),('date_start','<=',str(line.date)),'|',('date_end','>=',str(line.date)),('date_end','=',False)])
                if not contract_ids:
                    res[line.id] += "\n" + line.employee_id.name_related + ": NO tiene contrato activo el " + str(line.date)
        return res

           
   _columns = {
       'employee_id': fields.many2one('hr.employee',u'Empleado', required=True, readonly=True, states={'draft': [('readonly', False)]}),
       'date': fields.date(u'Fecha', readonly=True, states={'draft': [('readonly', False)]}),
       'value': fields.float(u'Valor', required=True, readonly=True, states={'draft': [('readonly', False)]}),
       'rule_id': fields.many2one('hr.salary.rule', u'Regla Salarial', required=True, readonly=True, states={'draft': [('readonly', False)]}),
       'head_id': fields.many2one('hr.io.head', u'Cabecera masivo', ondelete='cascade', readonly=True),
       'amortize_id': fields.many2one('hr.io.amortize', u'Cabecera amortización', ondelete='cascade', readonly=True),
       'holidays_sold_id': fields.many2one('hr.holidays.sold', u'Venta de vacaciones', ondelete='cascade', readonly=True),
       'holidays_id': fields.many2one('hr.holidays', u'Vacaciones', ondelete='cascade', readonly=True),
       'mark_id': fields.many2one('hr.mark.period', u'Marcaciones', ondelete='cascade', readonly=True),
       #'biweekly_payslip_id': fields.many2one('hr.payslip', u'Rol quincenal', ondelete='cascade', readonly=True),
       #'biweekly': fields.boolean(u'Anticipo Quincenal?', help=u'Marcar el casillero en el caso que el rubro pertenezca al anticipo', readonly=True, states={'draft': [('readonly', False)]}),
       'state': fields.selection(_STATE, u'Estado', readonly=True),
       'label': fields.char(u'Etiqueta', size=50, readonly=True, states={'draft': [('readonly', False)]}),
       'summary': fields.function(_get_summary, store=False, string='Resumen', type='text', readonly=True),
       }

   _order = "date desc, head_id, amortize_id, rule_id, employee_id, state"

   _defaults = {
       'state': 'draft',
       #'biweekly': False,
       'date': lambda self, cr, uid, context={}: strftime("%Y-%m-%d"),
       }

   def _greater_than_cero(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.value < 0:
            return False
        return True
   
   _constraints = [
                    (_greater_than_cero, 'No puede ingresar valores negativos', ['value']),
                    ]
   
l10n_ec_hr_io_line()
