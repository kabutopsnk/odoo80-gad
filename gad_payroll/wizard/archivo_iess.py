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
from openerp.osv import osv
from openerp.osv import fields
import base64
import StringIO
from time import strftime
from string import upper

class exportarIess(osv.osv_memory):
    _name = 'exportar.iess'
    _columns = {
        'datas1_fname':fields.char('Nombre Archivo ITALIMENTOS', size=32),
        'datas1':fields.binary('Archivo ITALIMENTOS',readonly=True),
        'datas2_fname':fields.char('Nombre Archivo ITALDELI', size=32),
        'datas2':fields.binary('Archivo ITALDELI',readonly=True),
        'payroll_id': fields.many2one('hr.payslip.run','Rol'),
    }

    
    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')
    
    _defaults = {
                 'payroll_id': rol_padre,
                 }

    def generar_archivo(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        buf1 = StringIO.StringIO()
        buf2 = StringIO.StringIO()
        for registro in self.browse(cr, uid, ids, context):
            #RUC = self.pool.get('res.company').browse(cr, uid, 1).ruc
            AUX = "0001"
            AUX1 = "INS"
            mes = registro.payroll_id.date_end[5:7]
            anio = registro.payroll_id.date_end[0:4]
            if registro.payroll_id.payroll_type!='monthly':
                raise osv.except_osv('Error!','El archivo del IESS solamente puede obtenerse de un rol mensual') 
            for rol in registro.payroll_id.slip_ids:
              if rol.contract_id.company_id.id==1:
                RUC = rol.contract_id.company_id.ruc
                cedula = rol.employee_id.name
                valor = 0
                valor_vacaciones=0
                remuneracion_basica=0
                for linea in rol.line_ids:
                    if linea.code=='C00065':
                        continue
                    if linea.category_id.code=='APT' and linea.code!='SUELDO_VACACIONES' and linea.code!='AJUSTESUELDO_VACACIONES':
                        valor += linea.total
                    if linea.code=='SUELDO_VACACIONES' or linea.code=='AJUSTESUELDO_VACACIONES':
                        valor_vacaciones+=linea.total
                    if linea.code=='C00003':
                        remuneracion_basica+=linea.total
                if valor_vacaciones>0:
                    if (valor_vacaciones+remuneracion_basica)<=rol.contract_id.wage:
                        valor_vacaciones=0
                    else:
                        valor_vacaciones=(valor_vacaciones+remuneracion_basica)-rol.contract_id.wage
                valor+=valor_vacaciones
                if valor>0:
                    CERO = "O" #O mayuscula por ahora
                    cadena = RUC + ';' + AUX + ';' + anio + ';' + mes + ';' + AUX1 + \
                        ';' + cedula + ';' + str(valor) + ';' + CERO + '\r\n'
                    buf1.write(upper(cadena))
              if rol.contract_id.company_id.id==3:
                RUC = rol.contract_id.company_id.ruc
                cedula = rol.employee_id.name
                valor = 0
                valor_vacaciones=0
                remuneracion_basica=0
                for linea in rol.line_ids:
                    if linea.category_id.code=='APT' and linea.code!='SUELDO_VACACIONES' and linea.code!='AJUSTESUELDO_VACACIONES':
                        valor += linea.total
                    if linea.code=='SUELDO_VACACIONES' or linea.code=='AJUSTESUELDO_VACACIONES':
                        valor_vacaciones+=linea.total
                    if linea.code=='C00003':
                        remuneracion_basica+=linea.total
                if valor_vacaciones>0:
                    if (valor_vacaciones+remuneracion_basica)<=rol.contract_id.wage:
                        valor_vacaciones=0
                    else:
                        valor_vacaciones=(valor_vacaciones+remuneracion_basica)-rol.contract_id.wage
                valor+=valor_vacaciones
                if valor>0:
                    CERO = "O" #O mayuscula por ahora
                    cadena = RUC + ';' + AUX + ';' + anio + ';' + mes + ';' + AUX1 + \
                        ';' + cedula + ';' + str(valor) + ';' + CERO + '\r\n'
                    buf2.write(upper(cadena))
            out1 = base64.encodestring(buf1.getvalue())
            buf1.close()
            name1 = "%s%s.TXT" % ("ITALIMENTOS - IESS", anio+"-"+mes)
            self.write(cr, uid, ids, {'datas1': out1, 'datas1_fname': name1})

            out2 = base64.encodestring(buf2.getvalue())
            buf2.close()
            name2 = "%s%s.TXT" % ("ITALDELI - IESS", anio+"-"+mes)
            self.write(cr, uid, ids, {'datas2': out2, 'datas2_fname': name2})

            return {
            'type': 'ir.actions.act_window',
            'name': 'Archivo IESS',
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'exportar.iess',
            'res_id': registro.id,
            'nodestroy': True,
            'target': 'new',
            'context': context,
            }

exportarIess()
