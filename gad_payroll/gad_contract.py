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
import unicodedata
from time import strftime

class hr_contract_log(osv.osv):
    _name = "hr.contract.log"
    _description = "Historial de contrato"
    
    _columns = {
        'name': fields.selection([
                                  ('wage','Salario'),
                                  ('department_id','Departamento'),
                                  ('job_id','Puesto de Trabajo'),
                                  ('project_id','Proyecto'),
                                  ('task_id','Actividad'),
                                  ('budget_id','Partida'),
                                  #('coach_id','Jefe'),
                                  #('company_id','Empresa')
                                  ], u'Campo Actualizado', required=True),
        'date': fields.date(u'Fecha de actualización', required=True),
        'previous_value': fields.char(u'Valor anterior', required=True),
        'new_value': fields.char(u'Valor nuevo', required=True),
        'contract_id': fields.many2one('hr.contract', u'Contrato', ondelete='cascade'),
    }
    
    _order = "date desc"
    
hr_contract_log()

class hr_contract_subtype(osv.osv):
    _name = "hr.contract.subtype"
    _description = "Subtipo de Contrato"
    
    _columns = {
        'name': fields.char(u'Subtipo de Contrato', required=True),
        'type_id': fields.many2one('hr.contract.type', u'Tipo de Contrato', required=True),
    }
    
    _order = "type_id, name"
    
hr_contract_subtype()

class l10n_ec_hr_contract(osv.osv):
    _inherit = "hr.contract"
    _description = "Contrato de empleado"
    
    _columns = {
        'log_ids': fields.one2many('hr.contract.log', 'contract_id', u'Historial'),
        'fondo_reserva': fields.boolean(u'Fondo reserva en rol', help="Marcar la casilla si el empleado recibirá los fondos de reserva en el rol (usar 'fondo_reserva' en las formulas)"),
        'extension_iess': fields.boolean(u'Extensión de cobertura IESS', help="Marcar la casilla si el empleado ha solicitado la extensión de cobertura familiar para el IESS (usar 'extension_iess' en las formulas)"),
        'department_id': fields.many2one('hr.department', u"Departmento"),
        'subtype_id': fields.many2one('hr.contract.subtype', u"Subtipo"),
        'previous_contract': fields.boolean(u'Posee contrato anterior?', help=u"Marcar la casilla si existen contratos anteriores del empleado en la empresa"),
        'previous_contract_id': fields.many2one('hr.contract', u'Contrato anterior', help=u"Seleccione el último contrato del empleado en la empresa"),
        'previous_days': fields.float(u'Dias adicionales en la empresa', help=u"Este valor puede ser utilizado como los días que el empleado ya ha laborado antes del presente contrato en la empresa (usar 'previous_days' en las formulas)"),
        'decimo_tercero': fields.boolean(u'Décimo Tercero en rol', help="Marcar la casilla si el empleado recibirá el valor correspondiente al Décimo Tercer en el rol (usar 'decimo_tercero' en las formulas)"),
        'decimo_cuarto': fields.boolean(u'Décimo Cuarto en rol', help="Marcar la casilla si el empleado recibirá el valor correspondiente al Décimo Cuarto en el rol (usar 'decimo_cuarto' en las formulas)"),
        'trial_date_start': fields.date(u'Fecha inicio de periodo de prueba'),
        'trial_date_end': fields.date(u'Fecha final de periodo de prueba'),
        'firstyear_date_start': fields.date(u'Fecha inicio de primer año'),
        'firstyear_date_end': fields.date(u'Fecha final de primer año'),
        'activo': fields.boolean(u'Incluye en último rol?', help="Desactivar el casillero si no se debe generar el rol del último mes laborado"),
        'project_id': fields.many2one('project.project', u'Proyecto'),
        'task_id': fields.many2one('project.task', u'Tarea/Actividad'),
        'budget_id': fields.many2one('crossovered.budget.lines', u'Partida Presupuestaria'),
        'valor_adicional1': fields.float(u'Valor Adicional 1'),
        'valor_adicional2': fields.float(u'Valor Adicional 2'),
        'valor_adicional3': fields.float(u'Valor Adicional 3'),
        'valor_adicional4': fields.float(u'Valor Adicional 4'),
        'valor_adicional5': fields.float(u'Valor Adicional 5'),
    }

    _defaults = {
        'fondo_reserva': True,
        'decimo_tercero': False,
        'decimo_cuarto': False,
        'activo': True,
        #'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.job', context=ctx),
    }

    def onchange_periodo_prueba(self, cr, uid, ids, fecha_prueba, context={}):
        res={}
        if fecha_prueba:
            fecha_prueba = datetime.datetime.strptime(fecha_prueba, "%Y-%m-%d")
            fecha_final = fecha_prueba + datetime.timedelta(days=89)
            res['value']={'trial_date_end':fecha_final}
        return res

    def onchange_empleado(self, cr, uid, ids, empleado, context={}):
        res={}
        if empleado:
            dato = self.pool.get("hr.employee").browse(cr, uid, empleado, context=context)
            res['value']={'name':dato.name}
        return res
    
    def limpiar_partida(self, cr, uid, ids, campo, context={}):
        res={}
        if campo=='project_id':
            res['value']={'task_id': False,
                          'budget_id': False,}
        if campo=='task_id':
            res['value']={'budget_id': False,}
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        for this in self.browse(cr, uid, ids, context=context):
            for valor in ['wage',
                          'department_id',
                          'job_id',
                          'project_id',
                          'task_id',
                          'budget_id']:
                if vals.has_key(valor):
                    obj_log = self.pool.get("hr.contract.log")
                    datos = self.pool.get("hr.contract").read(cr, uid, this.id, [valor])
                    diccionario = {'department_id': 'hr.department',
                                   'job_id': 'hr.job',
                                   #'coach_id': 'hr.employee',
                                   'project_id': 'project.project',
                                   'task_id': 'project.task',
                                   'budget_id': 'crossovered.budget.lines'}
                    if valor != 'wage':
                        if datos[valor]:
                            datos_obj = self.pool.get(diccionario[valor]).read(cr, uid, datos[valor][0], ['name'])
                    #import pdb
                    #pdb.set_trace()
                    #print datos
                    if datos[valor]: 
                        obj_log.create(cr, uid, {'contract_id':this.id,
                                                 'name': valor,
                                                 'date': context.has_key('fecha_actualizacion') and context['fecha_actualizacion'] or strftime("%Y-%m-%d"),
                                                 'previous_value': valor=='wage' and datos[valor] or datos_obj['name'],
                                                 'new_value': valor=='wage' and vals[valor] or self.pool.get(diccionario[valor]).read(cr, uid, vals[valor], ['name'])['name'],
                                                 })
        res = super(l10n_ec_hr_contract, self).write(cr, uid, ids, vals, context=context)
        return res


l10n_ec_hr_contract()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
