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

class l10n_ec_import_employee_projection(osv.osv_memory):

    _name='wizard.import.employee.projection'
    _description='Asistente para importar las proyecciones personales'
    
    _columns={'archivo':fields.binary('Archivo', required=True),
              'date_start':fields.date('Fecha Inicio', required=True),
              'date_stop':fields.date('Fecha Fin', required=True)}

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
        proj_obj = self.pool.get('hr.employee.projection')
        line_obj = self.pool.get('hr.employee.projection.line')
        expenses_obj = self.pool.get('hr.expenses')
        data = self.read(cr, uid, ids)[0]
        #line_obj = self.pool.get('hr.io.line')
        self._bad_archivo(cr, uid, ids, data['archivo'], context=context)
        #obj = self.pool.get('hr.io.head')
        #id_activo = context.get('active_id')
        #parent = obj.browse(cr, uid, id_activo)
        #ids_unlink=[]
        #if parent.state != 'draft':
        #    raise osv.except_osv(('Error de usuario!'),'No puede importar un archivo cuando el documento ya esta procesado.')
        #for l in parent.line_ids:
        #    if l.state=='draft':
        #        ids_unlink.append(l.id)
        #line_obj.unlink(cr, uid, ids_unlink, context=context)
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
                            empleado=emp_obj.browse(cr, uid, emp, context=context)
                            proj_id = proj_obj.create(cr, uid, {
                                                      'employee_id':empleado.id,
                                                      'date_start':data.date_start,
                                                      'date_stop':data.date_stop,
                                                      'name': 'Periodo ' + data.date_start + " - " + data.date_stop,
                                                      })
                            salud_id = expenses_obj.search(cr, uid, [('name','=','SALUD')])
                            alimentacion_id = expenses_obj.search(cr, uid, [('name','=','ALIMENTACION')])
                            vestimenta_id = expenses_obj.search(cr, uid, [('name','=','VESTIMENTA')])
                            educacion_id = expenses_obj.search(cr, uid, [('name','=','EDUCACION')])
                            vivienda_id = expenses_obj.search(cr, uid, [('name','=','VIVIENDA')])
                            if salud_id and alimentacion_id and vestimenta_id and educacion_id and vivienda_id:
                                salud_id = salud_id[0]
                                alimentacion_id = alimentacion_id[0]
                                vestimenta_id = vestimenta_id[0]
                                educacion_id = educacion_id[0]
                                vivienda_id = vivienda_id[0]
                                line_obj.create(cr, uid, {'projection_id':proj_id,
                                                          'name':vivienda_id,
                                                          'value': (sh.cell(r,2).value and sh.cell(r,2).value or 0)}, context=context)
                                line_obj.create(cr, uid, {'projection_id':proj_id,
                                                          'name':educacion_id,
                                                          'value': (sh.cell(r,3).value and sh.cell(r,3).value or 0)}, context=context)
                                line_obj.create(cr, uid, {'projection_id':proj_id,
                                                          'name':salud_id,
                                                          'value': (sh.cell(r,4).value and sh.cell(r,4).value or 0)}, context=context)
                                line_obj.create(cr, uid, {'projection_id':proj_id,
                                                          'name':vestimenta_id,
                                                          'value': (sh.cell(r,5).value and sh.cell(r,5).value or 0)}, context=context)
                                line_obj.create(cr, uid, {'projection_id':proj_id,
                                                          'name':alimentacion_id,
                                                          'value': (sh.cell(r,6).value and sh.cell(r,6).value or 0)}, context=context)
                            else:
                                raise osv.except_osv('Error de configuración!','No se encuentran configurados los rubros VIVIENDA EDUCACION SALUD VESTIMENTA ALIMENTACION')
        return {'type':'ir.actions.act_window_close' }

l10n_ec_import_employee_projection()
