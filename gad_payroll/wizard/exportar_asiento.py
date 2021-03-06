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
from openerp.addons.gad_tools import XLSWriter

class exportar_asiento(osv.osv_memory):
    _name='exportar.asiento'
    _description='Exportar asiento de rol de pagos a XLS'

    _columns = {
                'datas':fields.binary('Archivo'),
                'datas_fname':fields.char('Nombre archivo', size=32),
                'payroll_id': fields.many2one('hr.payslip.run','Rol'),
                'structure_id': fields.many2one('hr.payroll.structure','Estructura Salarial'),
                }
    
    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')
    
    _defaults = {
                 'payroll_id': rol_padre,
                 }

    def generar_archivo_rol(self, cr, uid, ids, context={}):
        obj_pinputs = self.pool.get('hr.payslip.line')
        #diccionario.values() devuelve los valores del diccionario
        #diccionario.keys() devuelve las claves o cabeceras del diccionario
        #diccionario.items() devuelve el par (clave,valor) de cada registro del diccionario
        diccionario = {}
        #La estructura de diccionario es, por ejemplo:
        #diccionario = {
        #               'centro_costo-codigo_cuenta': {
        #                                   'codigo_cuenta': 
        #                                   'nombre_cuenta': 
        #                                   'debito': 
        #                                   'credito': 
        #                                   'centro_costo': 
        #                                   'codigo_costo':
        #                                   'comentario': 
        #                                   },
        #               }
        for registro in self.browse(cr, uid, ids, context):
            for rol_individual in registro.payroll_id.slip_ids:
                #busco la regla de acumulacion de FR
                pinput = False
                pinputs_ids = obj_pinputs.search(cr, uid, [('salary_rule_id','=',445),('slip_id','=',rol_individual.id)])
                if pinputs_ids:
                    pinput = obj_pinputs.browse(cr, uid, pinputs_ids[0])
                if rol_individual.contract_id.company_id.id==1 and rol_individual.contract_id.struct_id.id==registro.structure_id.id:
                    for rubro in rol_individual.line_ids:
                        #evito no contabilizar el FR y el acumulacion FR
                        if rubro.salary_rule_id.id in [445,431] and pinput!=False:
                            continue
                        if rubro.category_id.code in ['BASIC','ING','APT','EGR','NET'] and (rubro.salary_rule_id.group_debit or rubro.salary_rule_id.group_credit):
                            #DEBITO DEBITO DEBITO DEBITO DEBITO DEBITO DEBITO DEBITO DEBITO DEBITO
                            if rubro.salary_rule_id.group_debit:
                                bandera = False
                                if rubro.total<0:
                                    if rubro.salary_rule_id.group_debit.cuenta_sobregiro:
                                        bandera = True
                                        if diccionario.has_key(rubro.salary_rule_id.group_debit.cuenta_sobregiro.code):
                                            diccionario[rubro.salary_rule_id.group_debit.cuenta_sobregiro.code]['credito'] += (rubro.total*(-1))
                                        else:
                                            diccionario[rubro.salary_rule_id.group_debit.cuenta_sobregiro.code] = {
                                                                                                                   'codigo_cuenta': rubro.salary_rule_id.group_debit.cuenta_sobregiro.code,
                                                                                                                   'nombre_cuenta': rubro.salary_rule_id.group_debit.cuenta_sobregiro.name,
                                                                                                                   'credito': (rubro.total*(-1)),
                                                                                                                   'debito': 0.0,
                                                                                                                   'codigo_costo': '',
                                                                                                                   'centro_costo': '',
                                                                                                                   'comentario': rol_individual.payslip_run_id.name,
                                                                                                                   }
                                    else:
                                        raise osv.except_osv(u'Error!',u'La regla salarial "' + rubro.name + u'" no tiene configuración para sobregiro.')
                                elif rubro.salary_rule_id.group_debit.cuenta:
                                    bandera = True
                                    if diccionario.has_key(rubro.salary_rule_id.group_debit.cuenta.code):
                                        diccionario[rubro.salary_rule_id.group_debit.cuenta.code]['debito'] += rubro.total
                                    else:
                                        diccionario[rubro.salary_rule_id.group_debit.cuenta.code] = {
                                                                                                     'codigo_cuenta': rubro.salary_rule_id.group_debit.cuenta.code,
                                                                                                     'nombre_cuenta': rubro.salary_rule_id.group_debit.cuenta.name,
                                                                                                     'debito': rubro.total,
                                                                                                     'credito': 0.0,
                                                                                                     'codigo_costo': '',
                                                                                                     'centro_costo': '',
                                                                                                     'comentario': rol_individual.payslip_run_id.name,
                                                                                                     }
                                else:
                                  for linea in rubro.salary_rule_id.group_debit.line_ids:
                                    if linea.centro_costo_id.id == rol_individual.contract_id.centro_costo_id.id:
                                        bandera = True
                                        if diccionario.has_key(rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code):
                                            diccionario[rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code]['debito'] += rubro.total
                                        else:
                                            diccionario[rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code] = {
                                                                                                                                  'codigo_cuenta': linea.cuenta.code,
                                                                                                                                  'nombre_cuenta': linea.cuenta.name,
                                                                                                                                  'debito': rubro.total,
                                                                                                                                  'credito': 0.0,
                                                                                                                                  'codigo_costo': rol_individual.contract_id.centro_costo_id.code,
                                                                                                                                  'centro_costo': rol_individual.contract_id.centro_costo_id.name,
                                                                                                                                  'comentario': rol_individual.payslip_run_id.name,
                                                                                                                                  }
                                if bandera==False:
                                    raise osv.except_osv(u'Error!',u'La regla salarial "' + rubro.name + u'" no tiene configuración de débito para el centro de costo "' + rol_individual.contract_id.centro_costo_id.name + '"')
                            #CREDITO CREDITO CREDITO CREDITO CREDITO CREDITO CREDITO CREDITO CREDITO CREDITO
                            if rubro.salary_rule_id.group_credit:
                                bandera = False
                                if rubro.total<0:
                                    if rubro.salary_rule_id.group_credit.cuenta_sobregiro:
                                        bandera = True
                                        if diccionario.has_key(rubro.salary_rule_id.group_credit.cuenta_sobregiro.code):
                                            diccionario[rubro.salary_rule_id.group_credit.cuenta_sobregiro.code]['debito'] += (rubro.total*(-1))
                                        else:
                                            diccionario[rubro.salary_rule_id.group_credit.cuenta_sobregiro.code] = {
                                                                                                                    'codigo_cuenta': rubro.salary_rule_id.group_credit.cuenta_sobregiro.code,
                                                                                                                    'nombre_cuenta': rubro.salary_rule_id.group_credit.cuenta_sobregiro.name,
                                                                                                                    'debito': (rubro.total*(-1)),
                                                                                                                    'credito': 0.0,
                                                                                                                    'codigo_costo': '',
                                                                                                                    'centro_costo': '',
                                                                                                                    'comentario': rol_individual.payslip_run_id.name,
                                                                                                                    }
                                    else:
                                        raise osv.except_osv(u'Error!',u'La regla salarial "' + rubro.name + u'" no tiene configuración para sobregiro.')
                                elif rubro.salary_rule_id.group_credit.cuenta:
                                    bandera = True
                                    if diccionario.has_key(rubro.salary_rule_id.group_credit.cuenta.code):
                                        diccionario[rubro.salary_rule_id.group_credit.cuenta.code]['credito'] += rubro.total
                                    else:
                                        diccionario[rubro.salary_rule_id.group_credit.cuenta.code] = {
                                                                                                      'codigo_cuenta': rubro.salary_rule_id.group_credit.cuenta.code,
                                                                                                      'nombre_cuenta': rubro.salary_rule_id.group_credit.cuenta.name,
                                                                                                      'credito': rubro.total,
                                                                                                      'debito': 0.0,
                                                                                                      'codigo_costo': '',
                                                                                                      'centro_costo': '',
                                                                                                      'comentario': rol_individual.payslip_run_id.name,
                                                                                                      }
                                else:
                                  for linea in rubro.salary_rule_id.group_credit.line_ids:
                                    if linea.centro_costo_id.id == rol_individual.contract_id.centro_costo_id.id:
                                        bandera = True
                                        if diccionario.has_key(rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code):
                                            diccionario[rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code]['credito'] += rubro.total
                                        else:
                                            diccionario[rol_individual.contract_id.centro_costo_id.code+"-"+linea.cuenta.code] = {
                                                                                                                                  'codigo_cuenta': linea.cuenta.code,
                                                                                                                                  'nombre_cuenta': linea.cuenta.name,
                                                                                                                                  'credito': rubro.total,
                                                                                                                                  'debito': 0.0,
                                                                                                                                  'codigo_costo': rol_individual.contract_id.centro_costo_id.code,
                                                                                                                                  'centro_costo': rol_individual.contract_id.centro_costo_id.name,
                                                                                                                                  'comentario': rol_individual.payslip_run_id.name,
                                                                                                                                  }
                                if bandera==False:
                                    raise osv.except_osv(u'Error!',u'La regla salarial "' + rubro.name + u'" no tiene configuración de crédito para el centro de costo "' + rol_individual.contract_id.centro_costo_id.name + '"')
                        elif rubro.category_id.code not in ['BASIC','ING','APT','EGR','NET']:
                            pass
                        else:
                            raise osv.except_osv(u'Error!',u'La regla salarial "' + rubro.name + u'" no tiene configuración contable.')
                        #if not rubro.salary_rule_id.group_credit and not rubro.salary_rule_id.group_debit:
                        #    print rubro.code + ": " + rubro.category_id.name
        #diccionario['20107040010101']['credito'] -= 0.02 #salario
        #diccionario['20107030010101']['credito'] -= 0.02 #iess
        #diccionario['20107080010101']['credito'] -= 0.01 #renta
        #creamos la variable para la escritura en el archivo xls
        writer = XLSWriter.XLSWriter()
        
        cabecera = ['CtaContable', 'Descripcion', 'Debe', 'Haber', 'CodCcosto', 'CentroCosto', 'Comentario', 'Referencia1', 'Referencia2', 'Referencia3']
        writer.append(cabecera)
        
        for cuenta in diccionario.keys():
                linea = [diccionario[cuenta]['codigo_cuenta'],
                         diccionario[cuenta]['nombre_cuenta'],
                         diccionario[cuenta]['debito'],
                         diccionario[cuenta]['credito'],
                         diccionario[cuenta]['codigo_costo'],
                         diccionario[cuenta]['centro_costo'],
                         diccionario[cuenta]['comentario']
                         ]
                writer.append(linea)
        writer.save("asiento_contable.xls")
        out = open("asiento_contable.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'asiento_contable.xls'})
        return {
        'type': 'ir.actions.act_window',
        'name': 'Archivo Asiento Contable (XLS)',
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'exportar.asiento',
        'res_id': registro.id,
        'nodestroy': True,
        'target': 'new',
        'context': context,
        }

exportar_asiento()
