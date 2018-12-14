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


from openerp.osv import osv,fields
import base64
import xlrd

class wizard_modificar_salario(osv.osv_memory):

    _name='wizard.modificar.contract.wage'
    _description='Asistente para modificar Salarios'
    
    _columns={'archivo':fields.binary('Archivo', required=True),
              'date':fields.date('Fecha', required=True),}

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result = True
        emp_obj = self.pool.get('hr.employee')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
                emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                if emp_id:
                    j+=1
                else:
                    raise osv.except_osv(('Error de archivo!'),'La cedula %s, en la linea numero %d no corresponde a ningun empleado'%((str(sh.cell(r,1).value)),i+1))
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
        if j==sh.nrows:
            result = True
        return result

    def import_sheet(self, cr, uid, ids, context={}):
        emp_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
        self._bad_archivo(cr, uid, ids, data['archivo'], context=context)
        for data in self.browse(cr, uid, ids, context=context):
            arch = data.archivo
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if sh.cell(r,0).value and sh.cell(r,1).value:
                    emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                    if emp_id:
                        for emp in emp_id:
                            empleado = emp_obj.browse(cr, uid, emp, context=context)
                            context['fecha_actualizacion'] = data.date
                            if sh.cell(r,2).value:
                              if sh.cell(r,2).value:
                                self.pool.get('hr.contract').write(cr, uid, empleado.contract_id.id, {'wage':sh.cell(r,2).value}, context=context)
                            else:
                                raise osv.except_osv('Error!','No se puede modificar el salario de: ' + str(sh.cell(r,1).value))
        return {'type':'ir.actions.act_window_close' }

wizard_modificar_salario()
