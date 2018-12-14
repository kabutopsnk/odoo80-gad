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
from openerp.report import report_sxw
from openerp.osv import osv
import pdb

class rol_general_pdf(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_general_pdf, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'generate_dict': self.generate_dict,
        })

    def generate_dict(self, obj):
        #diccionario.values() devuelve los valores del diccionario
        #diccionario.keys() devuelve las claves o cabeceras del diccionario
        #diccionario.items() devuelve el par (clave,valor) de cada registro del diccionario
        diccionario = {}
        diccionario_totales = {}
        #La estructura de diccionario es, por ejemplo:
        #diccionario = {
        #               'id_departamento': {
        #                                   'nombre_empleado': {
        #                                                       'cedula': cedula_empleado,
        #                                                       'id_rubro': valor,
        #                                                       },
        #                                   },
        #               }
        departamentos = []
        rubros = []
        #for registro in self.browse(self.cr, self.uid, ids, context):
        if obj:
            registro=obj
            for rol_individual in registro.slip_ids:
                for rubro in rol_individual.line_ids:
                    #rubro tiene la informacion (id,secuencia,name)
                    rubros.append([rubro.salary_rule_id.id,rubro.salary_rule_id.sequence,rubro.salary_rule_id.name])
                    #departamentos tiene el par (id,name)
                    departamentos.append([rol_individual.department_id.id,rol_individual.department_id.name])
                    if diccionario.has_key(rol_individual.department_id.id):
                        if diccionario[rol_individual.department_id.id].has_key(rol_individual.employee_id.name_related):
                            if diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related].has_key(rubro.salary_rule_id.id):
                                diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related][rubro.salary_rule_id.id] += rubro.total
                            else:
                                diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related][rubro.salary_rule_id.id] = rubro.total
                        else:
                            diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related] = {'cedula': rol_individual.employee_id.name, 'puesto de trabajo': rol_individual.job_id.name, rubro.salary_rule_id.id: rubro.total}
                    else:
                        diccionario[rol_individual.department_id.id] = {rol_individual.employee_id.name_related: {'cedula': rol_individual.employee_id.name, 'puesto de trabajo': rol_individual.job_id.name, rubro.salary_rule_id.id: rubro.total}}
                diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related]['dias laborados'] = 0
                for asistencia in rol_individual.worked_days_line_ids:
                    if asistencia.code=='WORK100' or asistencia.code=='VAC' or asistencia.code=='ENF' or asistencia.code=='MAT':
                        diccionario[rol_individual.department_id.id][rol_individual.employee_id.name_related]['dias laborados']+=asistencia.number_of_days
        departamentos_clean = []
        for key in departamentos:
            if key not in departamentos_clean:
                departamentos_clean.append(key)
        rubros_clean = []
        for key in rubros:
            if key not in rubros_clean:
                rubros_clean.append(key)
        #resultado = list(resultado.values())
        #resultado.sort()
        departamentos_clean.sort(key=lambda x: x[0])
        rubros_clean.sort(key=lambda x: x[1])
        
        #creamos la variable para la escritura en el archivo xls
        writer = []
        
        cabecera = ['CEDULA','EMPLEADO','DIAS LAB.']
        pie = {}
        for rubro in rubros_clean:
            cabecera.append(rubro[2])
        #writer.append(cabecera)

        total = {}
        for departamento in departamentos_clean:
            linea_departamento = ['' for i in cabecera]
            linea_departamento[0] = 'DEPARTAMENTO'
            linea_departamento[1] = '&nbsp<br/>&nbsp<br/>' + str(departamento[1])
            linea_departamento[2] = ''
            writer.append(linea_departamento)
            pie = {}
            writer.append(cabecera)
            for empleado in diccionario[departamento[0]].keys():
                linea = [diccionario[departamento[0]][empleado]['cedula'], empleado, diccionario[departamento[0]][empleado]['dias laborados']]
                for rubro in rubros_clean:
                    if not pie.has_key(rubro[0]):
                        pie.update({rubro[0]:0.00})
                    if not total.has_key(rubro[0]):
                        total.update({rubro[0]:0.00})
                    if diccionario[departamento[0]][empleado].has_key(rubro[0]):
                        linea.append(diccionario[departamento[0]][empleado][rubro[0]])
                        pie[rubro[0]] = pie[rubro[0]] + diccionario[departamento[0]][empleado][rubro[0]]
                        total[rubro[0]] = total[rubro[0]] + diccionario[departamento[0]][empleado][rubro[0]]
                    else:
                        linea.append(0.00)
                writer.append(linea)
            linea = ['TOTAL','','']
            for rubro in rubros_clean:
                linea.append(pie[rubro[0]])
            writer.append(linea)
        writer.append(['&nbsp<br/>&nbsp'])
        linea = ['TOTAL','','']
        cabecera_final = [i for i in cabecera]
        cabecera_final[0] = cabecera_final[1] = cabecera_final[2] = ''
        writer.append(cabecera_final)
        for rubro in rubros_clean:
            linea.append(total[rubro[0]])
        writer.append(linea)
        return writer
            
            
      
report_sxw.report_sxw('report.rol_general_pdf',
                       'hr.payslip.run', 
                       'addons/gad_payroll/report/rol_general_pdf.mako',
                       parser=rol_general_pdf,
                       header=False)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
