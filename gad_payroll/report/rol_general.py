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

class hr_payroll_export(osv.osv_memory):
    _name='hr.payroll.export'
    _description='Exportar rol de pagos a XLS'

    _columns = {
                'datas':fields.binary('Archivo'),
                'datas_fname':fields.char('Nombre archivo', size=32),
                'payroll_id': fields.many2one('hr.payslip.run','Rol'),
                }
    
    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')
    
    _defaults = {
                 'payroll_id': rol_padre,
                 }

    def generar_archivo_rol(self, cr, uid, ids, context={}):
        #diccionario.values() devuelve los valores del diccionario
        #diccionario.keys() devuelve las claves o cabeceras del diccionario
        #diccionario.items() devuelve el par (clave,valor) de cada registro del diccionario
        diccionario = {}
        diccionario_totales = {}
        #La estructura de diccionario es, por ejemplo:
        #diccionario = {
        #               'nombre_empleado': {
        #                                   'cedula': cedula_empleado,
        #                                   'codigo': id de xpersoft y compers,
        #                                   'departamento': nombre_del_departamento,
        #                                   'puesto de trabajo': nombre_del_cargo,
        #                                   'centro de costo': nombre_del_centro_de_costo,
        #                                   'id_rubro': valor,
        #                                   },
        #               }
        rubros = []
        for registro in self.browse(cr, uid, ids, context):
            for rol_individual in registro.payroll_id.slip_ids:
                for rubro in rol_individual.line_ids:
                    #rubro tiene la informacion (id,secuencia,name)
                    rubros.append([rubro.salary_rule_id.id,rubro.salary_rule_id.sequence,rubro.salary_rule_id.name])
                    if diccionario.has_key(rol_individual.employee_id.name_related):
                            if diccionario[rol_individual.employee_id.name_related].has_key(rubro.salary_rule_id.id):
                                diccionario[rol_individual.employee_id.name_related][rubro.salary_rule_id.id] += rubro.total
                            else:
                                diccionario[rol_individual.employee_id.name_related][rubro.salary_rule_id.id] = rubro.total
                    else:
                            diccionario[rol_individual.employee_id.name_related] = {'cedula': rol_individual.employee_id.name, 'codigo': rol_individual.employee_id.id or 0, 'departamento': (rol_individual.contract_id and rol_individual.contract_id.department_id.name or '-'), 'centro de costo': (rol_individual.contract_id and (rol_individual.contract_id.budget_id.general_budget_id.code + ' ' + rol_individual.contract_id.budget_id.general_budget_id.name) or '-'), 'puesto de trabajo': (rol_individual.contract_id and rol_individual.job_id.name or '-'), rubro.salary_rule_id.id: rubro.total, 'company': (rol_individual.company_id and rol_individual.company_id.name or '-')}

                if diccionario.has_key(rol_individual.employee_id.name_related):
                    diccionario[rol_individual.employee_id.name_related]['dias laborados']=0
                else:
                    diccionario[rol_individual.employee_id.name_related] = {'cedula': rol_individual.employee_id.name, 'codigo': rol_individual.employee_id.id or 0, 'departamento': (rol_individual.contract_id and rol_individual.contract_id.department_id.name or '-'), 'centro de costo': (rol_individual.contract_id and (rol_individual.contract_id.budget_id.general_budget_id.code + ' ' + rol_individual.contract_id.budget_id.general_budget_id.name) or '-'), 'puesto de trabajo': (rol_individual.contract_id and rol_individual.job_id.name or '-'), 'dias laborados':0, 'company': (rol_individual.company_id and rol_individual.company_id.name or '-')}
                for asistencia in rol_individual.worked_days_line_ids:
                    if asistencia.code=='WORK100' or asistencia.code=='VAC' or asistencia.code=='ENF' or asistencia.code=='MAT' or asistencia.code=='PERM':
                        diccionario[rol_individual.employee_id.name_related]['dias laborados']+=asistencia.number_of_days
        #import pdb
        #pdb.set_trace()
        rubros_clean = []
        for key in rubros:
            if key not in rubros_clean:
                rubros_clean.append(key)
        #resultado = list(resultado.values())
        #resultado.sort()
        rubros_clean.sort(key=lambda x: x[1])
        
        #creamos la variable para la escritura en el archivo xls
        writer = XLSWriter.XLSWriter()
        
        cabecera = ['CEDULA','EMPLEADO','CARGO','DEPARTAMENTO','EMPRESA','PARTIDA PRESUPUESTARIA','DIAS LAB.']
        pie = {}
        for rubro in rubros_clean:
            cabecera.append(rubro[2])
        writer.append(cabecera)
        
        total = {}
        for empleado in diccionario.keys():
                linea = [diccionario[empleado]['cedula'], empleado, diccionario[empleado]['puesto de trabajo'], diccionario[empleado]['departamento'],  diccionario[empleado]['company'],  diccionario[empleado]['centro de costo'], diccionario[empleado]['dias laborados']]
                for rubro in rubros_clean:
                    if not total.has_key(rubro[0]):
                        total.update({rubro[0]:0.00})
                    if diccionario[empleado].has_key(rubro[0]):
                        linea.append(diccionario[empleado][rubro[0]])
                        if diccionario[empleado][rubro[0]]>0:
                            total[rubro[0]] = total[rubro[0]] + diccionario[empleado][rubro[0]]
                    else:
                        linea.append(0.00)
                writer.append(linea)
        linea = ['','','','','','','TOTAL']
        for rubro in rubros_clean:
            linea.append(total[rubro[0]])
        writer.append(linea)
        writer.save("resumen_rol.xls")
        out = open("resumen_rol.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'resumen_rol.xls'})
        return {
        'type': 'ir.actions.act_window',
        'name': 'Archivo Rol (XLS)',
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'hr.payroll.export',
        'res_id': registro.id,
        'nodestroy': True,
        'target': 'new',
        'context': context,
        }
            
            

hr_payroll_export()
