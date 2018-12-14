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
from openerp.tools.translate import _
from openerp import tools
from time import strftime
import unicodedata
import exceptions

class l10n_ec_hr_marital_status(osv.osv):
    _name = 'hr.marital.status'
    _description = 'Tipo de estado civil de una persona'
    _order = 'name asc'

    _columns = {
        'name': fields.char(u'Estado Civil', size=30, required=True),
    }

l10n_ec_hr_marital_status()

class l10n_ec_hr_employee_disability(osv.osv):
    _name = 'hr.employee.disability'
    _description = 'Tipo de discapacidad de una persona'
    _order = 'name desc'

    _columns = {
        'name': fields.char(u'Tipo de discapacidad', size=50, required=True),
        'active': fields.boolean(u'Activo'),
    }

    _defaults = {
        'active': True,
    }
    


l10n_ec_hr_employee_disability()

class l10n_ec_hr_employee_reference(osv.osv):
    _name = 'hr.employee.reference'
    _description = 'Referencias personales de un Empleado'
    _order = 'name desc'

    _columns = {
        'employee_id':  fields.many2one('hr.employee', u'Empleado', required=True),
        'name': fields.char(u'Nombre', size=50, required=True),
        'phone': fields.char(u'Teléfono', size=30, required=True),
        'email': fields.char(u'Email', size=50),
    }

l10n_ec_hr_employee_reference()

class ec_hr_employee_experience_sector(osv.osv):
    _name = 'hr.employee.experience.sector'
    _description = 'Sector de la Experiencia Laboral de un empleado'
    _order = 'name asc'

    _columns = {
        'name': fields.char(u'Sector Laboral', size=50, required=True),
    }

ec_hr_employee_experience_sector()

class ec_hr_employee_experience_institution(osv.osv):
    _name = 'hr.employee.experience.institution'
    _description = 'Experiencia laboral en instituciones de tipo'
    _order = 'name asc'

    _columns = {
        'name': fields.char(u'Experiencia en instituciones de tipo', size=50, required=True),
    }

ec_hr_employee_experience_institution()

class ec_hr_employee_experience_job(osv.osv):
    _name = 'hr.employee.experience.job'
    _description = 'Experiencia laboral en cargos de tipo'
    _order = 'name asc'

    _columns = {
        'name': fields.char(u'Experiencia en cargos de tipo', size=50, required=True),
    }

ec_hr_employee_experience_job()

class ec_hr_employee_experience(osv.osv):
    _name = 'hr.employee.experience'
    _description = 'Experiencia Laboral de un Empleado'

    _columns = {
        'employee_id':  fields.many2one('hr.employee', u'Empleado', required=True),
        'institution': fields.char(u'Institución', size=100),
        'job': fields.char(u'Cargo', size=100),
        'sector_id': fields.many2one('hr.employee.experience.sector', u'Sector'),
        'date_start': fields.date(u'Fecha de ingreso'),
        'date_stop': fields.date(u'Fecha de salida'),
        'experience_institution_id': fields.many2one('hr.employee.experience.institution', u'Experiencia en instituciones de tipo'),
        'experience_job_id': fields.many2one('hr.employee.experience.job', u'Experiencia en cargos de tipo'),
        'description': fields.char(u'Descripción', size=200),
        'reference_name': fields.char(u'Nombre de la ref.', size=100),
        'reference_institution': fields.char(u'Institución de ref.', size=100),
        'reference_job': fields.char(u'Cargo de la ref.', size=100),
        'reference_phone': fields.char(u'Teléfono de la ref.', size=30),
    }


ec_hr_employee_experience()

class l10n_ec_hr_employee_family_type(osv.osv):
    _name = 'hr.employee.family.type'
    _description = 'Relacion familiar a un empleado'
    _order = 'name desc'

    _columns = {
        'name': fields.char(u'Relación Familiar', size=50, required=True),
    }

l10n_ec_hr_employee_family_type()

class l10n_ec_hr_employee_projection(osv.osv):
    _name = 'hr.employee.projection'
    _description='Proyeccion de gastos personales de un empleado'

    def _compute_all(self, cr, uid, id, name, args, context):
        result={}
        for anual in self.browse(cr, uid, id):
            sum=0
            for line in anual.line_ids:
                sum+=line.value
            result[anual.id]=sum
        return result

    _columns = {
        'name': fields.char(u'Descripción', size=64),
        'date_start': fields.date(u'Fecha de inicio'),
        'date_stop': fields.date(u'Fecha fin'),
        'line_ids': fields.one2many('hr.employee.projection.line','projection_id',u'Lineas Proyección'),
        'employee_id': fields.many2one('hr.employee',u'Empleado', ondelete='cascade'),
        'total': fields.function(_compute_all, method=True, string=u'Total', type='float', readonly=True),
    }

    _defaults = {
        'name': 'Proyeccion de gastos',
               }

l10n_ec_hr_employee_projection()

class l10n_ec_hr_employee_projection_line(osv.osv):
    
    _name='hr.employee.projection.line'
    _description='Detalle de proyeccion de gastos personales de un empleado'

    _columns = {
        'name': fields.many2one('hr.expenses',u'Tipo de gasto'),
        'value': fields.float(u'Valor'),
        'projection_id': fields.many2one('hr.employee.projection', u'Año', ondelete='cascade'),
        }

l10n_ec_hr_employee_projection_line()

class l10n_ec_hr_employee_profit(osv.osv):
    _name = 'hr.employee.profit'
    _description='Rentabilidad anual del empleado'


    _columns = {
        'name': fields.char(u'Descripción', size=64),
        'date_start': fields.date(u'Fecha de inicio'),
        'date_stop': fields.date(u'Fecha fin'),
        'line_ids': fields.one2many('hr.employee.profit.line','profit_id',u'Detalle'),
        'employee_id': fields.many2one('hr.employee',u'Empleado', ondelete='cascade'),
    }

    _defaults = {
        'name': 'Resumen ',
               }

l10n_ec_hr_employee_profit()

class l10n_ec_hr_employee_profit_line(osv.osv):
    
    _name='hr.employee.profit.line'
    _description='Detalle de rentabilidad anual de empleado'

    _columns = {
        'name': fields.selection([('mensual','Mensual'),('utilidades','Utilidades'),('decimotercero','Decimo Tercero'),('decimocuarto','Decimo Cuarto'),('otro','Otro')], u'Tipo', readonly=True),
        'date_start': fields.date(u'Fecha de inicio'),
        'date_stop': fields.date(u'Fecha fin'),
        'profit_id': fields.many2one('hr.employee.profit', u'Año', ondelete='cascade'),
        'proyectar_aportable':fields.float(u'Proyectable - Aportable'),
        'proyectar_no_aportable':fields.float(u'Proyectable - No aportable'),
        'no_proyectar_aportable':fields.float(u'No proyectable - Aportable'),
        'no_proyectar_no_aportable':fields.float(u'No proyectable - No aportable'),
        'retenido':fields.float(u'Valor retenido'),
        'otros_empleadores':fields.float(u'Otros empleadores'),
        'otros_empleadores_iess':fields.float(u'Aporte IESS otros empleadores'),
        'otros_empleadores_retenido':fields.float(u'Retenido por otros empleadores'),
        'otros_valores':fields.float(u'Otros'),
        }

    _defaults = {
        'name': 'otro',
        'proyectar_aportable':0,
        'proyectar_no_aportable':0,
        'no_proyectar_aportable':0,
        'no_proyectar_no_aportable':0,
        'otros_empleadores':0,
        'otros_empleadores_iess':0,
        'otros_empleadores_retenido':0,
        'otros_valores':0,
        }

l10n_ec_hr_employee_profit_line()

class l10n_ec_hr_employee_family(osv.osv):
    _name = 'hr.employee.family'
    _description = 'Familiares de empleado'
    _order = 'name desc'

    _BLOOD = [('on','O-'),('op','O+'),('an','A-'),('ap','A+'),
              ('bn','B-'),('bp','B+'),('abn','AB-'),('abp','AB+')]
            
    _columns = {
        'name': fields.char(u'Nombre completo', size=100, required=True),
        'relationship_id': fields.many2one('hr.employee.family.type', u'Parentesco', required=True),
        'identifier': fields.char(u'Cédula del familiar', size=15),
        'gender': fields.selection([('male', 'Hombre'),('female', 'Mujer')], u'Género'),
        'marital_id': fields.many2one('hr.marital.status',u'Estado Civil'),
        'blood_type':  fields.selection(_BLOOD,u'Tipo de sangre'),
        'birthday': fields.date(u'Fecha de Nacimiento'),
        'disabled': fields.boolean(u'Tiene discapacidad?', help=u"Marque este campo si la carga familiar tiene alguna limitación para llevar a cabo ciertas actividades provocadas por una deficiencia física o mental"),
        'student': fields.boolean(u'Es estudiante?'),
        'disability_id': fields.many2one('hr.employee.disability',u'Tipo de discapacidad'),
        'disability_percent': fields.float(u'Porcentaje de discapacidad'),
        'id_disability': fields.char(u'ID Carnet Discapacidad', size=15, help=u"Codigo de identificación de Discapacidad"),
        'employee_id':  fields.many2one('hr.employee', u'Empleado', required=True),
        #'recibe_pension': fields.selection([('pension_alimenticia',u'Pensión Alimenticia'),('funcion_judicial',u'Función Judicial')],u'Recibe pensión?', help=u'Activar este campo en caso que esta carga familiar reciba pensión alimenticia y elija el tipo de descuento'),
        #'valor_pension': fields.float(u'Valor del descuento', help=u'Valor a descontar al empleado por la pensión'),
        'address': fields.char(u'Dirección', size=100),
        'phone': fields.char(u'Teléfono', size=30),
        'occupation': fields.char(u'Ocupación Actual', size=30),
        'email': fields.char(u'Email', size=50),
        }


l10n_ec_hr_employee_family()

class l10n_ec_hr_academic_level(osv.osv):
    _name = 'hr.academic.level'
    _description = 'Niveles Academicos'
    _order = 'name asc'
    _columns = dict(
        active = fields.boolean(u'Activo'),
        name = fields.char(u'Nivel', size=100, required=True),
        description = fields.char(u'Descripción', size=100),
        #status = fields.char(u'Status', size=2),
        type = fields.selection([('NINGUNA','NINGUNA'),('BASICO','BASICO'),('PRIMER NIVEL','PRIMER NIVEL'),('FORMACION SUPERIOR','FORMACION SUPERIOR'),('POSTGRADO','POSTGRADO')], u'Tipo'),
        )

    _defaults = {
        'active': True,
    }
l10n_ec_hr_academic_level()

class l10n_ec_hr_academic_area(osv.osv):
    _name = 'hr.academic.area'
    _description = 'Area Academica'
    _order = 'name asc'
    _columns = dict(
        active = fields.boolean(u'Activo'),
        name = fields.char(u'Area de conocimiento', size=100, required=True),
        description = fields.char(u'Descripción', size=100),
        #status = fields.char(u'Status', size=2),
        )

    _defaults = {
        'active': True,
    }
l10n_ec_hr_academic_area()

class l10n_ec_hr_employee_courses(osv.osv):
    _name = 'hr.employee.courses'
    _description = 'Cursos Empleado'
    _MODALITY = [('v',u'Virtual'),('d',u'Distancia'),('p',u'Presencial'),
                 ('s',u'Semipresencial'),('o',u'Otros')]
    _columns = dict(
        employee_id = fields.many2one('hr.employee', u'Empleado'),
        name = fields.char(u'Tema',size=128,required=True),
        date = fields.date(u'Fecha Inicio'),
        date_end = fields.date(u'Fecha Fin'),
        institute = fields.char(u'Institución',size=100),
        country_id = fields.many2one('res.country', u'País'),
        #city_id = fields.many2one('res.country.state.city', u'Ciudad'),
        city = fields.char(u'Ciudad', size=50),
        duration =  fields.integer(u'Duración'),
        type = fields.selection([(u'Certificación',u'Certificación'),(u'Curso',u'Curso'),(u'Seminario',u'Seminario')], u'Tipo de Curso'),
        area_id = fields.many2one('hr.academic.area', u'Area de conocimiento'),
        )

l10n_ec_hr_employee_courses()

class l10n_ec_hr_employee_academic(osv.osv):   
    _name= 'hr.employee.academic'
    _description = 'Titulos Empleado'

    _columns = dict(
        employee_id = fields.many2one('hr.employee', u'Empleado'),
        name = fields.char(u'Título',size=100, required=True),
        institute = fields.char(u'Institución', size=100),
        country_id = fields.many2one('res.country', u'País'),
        date_start = fields.date(u'Fecha Inicio'),
        date_stop = fields.date(u'Fecha Finalización'),
        level_id = fields.many2one('hr.academic.level', u'Nivel'),
        area_id = fields.many2one('hr.academic.area', u'Area de conocimiento'),
        code = fields.char(u'Codigo SENESCYT', size=50),
        honores = fields.selection([('Si','Si'),('No','No')],u'Honores'),
        )
    
l10n_ec_hr_employee_academic()

class hr_employee_ethnicity(osv.osv):   
    _name= 'hr.employee.ethnicity'
    _description = u'Etnia de un Empleado'

    _columns = dict(
        name = fields.char(u'Etnia', size=100, required=True),
        )
    
hr_employee_ethnicity()


class l10n_ec_hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def name_get(self, cr, uid, ids, context={}):
        if not ids:
            return []
        try:
            flag = len(ids)
        except:
            ids = [ids]
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record.name_related:
                name = record.name_related
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        if name:
            ids_name = self.search(cr, uid, [('name_related', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)


    def _complete_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for employee in self.browse(cr, uid, ids):
            name = ""
            if employee.employee_lastname:
                name = name + employee.employee_lastname
            if employee.employee_name:
                name = name + " " + employee.employee_name
            res[employee.id] = name
        return res

    _BLOOD = [('on','O-'),('op','O+'),('an','A-'),('ap','A+'),
              ('bn','B-'),('bp','B+'),('abn','AB-'),('abp','AB+')]
    
    _columns = {
        #we need a related field in order to be able to sort the employee by name
        'name_related': fields.function(_complete_name, method=True, string=u"Nombre Completo", store=True, type="char", size=100),
        'employee_name': fields.char(u'Nombres', size=50, required=True),
        'employee_lastname': fields.char(u'Apellidos', size=50, required=True),
        'marital': fields.many2one('hr.marital.status',u'Estado Civil'),
        #'city_of_birth_id': fields.many2one('res.country.state.city',u'Ciudad de Nacimiento'),
        'state_id': fields.many2one('res.country.state',u'Provincia'),
        'canton_id': fields.many2one('res.country.state.canton',u'Cantón'),
        'parish_id': fields.many2one('res.country.state.parish',u'Parroquia'),
        'id_type': fields.selection([('c','Cedula'),('p','Pasaporte')], u"Tipo identificador", help=u"Tipo de identificador personal"),
        'blood_type':  fields.selection(_BLOOD,u'Tipo de sangre'),
        'disabled': fields.boolean(u'Es discapacitado?', help=u"Marque este campo si el empleado tiene alguna limitación para llevar a cabo ciertas actividades provocadas por una deficiencia física o mental"),
        'disability_id': fields.many2one('hr.employee.disability',u'Tipo de discapacidad'),
        'disability_percent': fields.float(u'Porcentaje de discapacidad'),
        'id_disability': fields.char(u'ID Carnet Discapacidad', size=15, help=u"Codigo de identificación de Discapacidad"),
        'emergency_contact': fields.char(u'Nombre del contacto', size=100, help=u"Indique el nombre y la relación del empleado con el contacto de emergencia"),
        'emergency_phone': fields.char(u'Telefono de contacto', size=30),
        'family_lines': fields.one2many('hr.employee.family', 'employee_id', u'Familares'),
        'projection_lines': fields.one2many('hr.employee.projection','employee_id',u'Proyección de Gastos personales'),
        'profit_lines': fields.one2many('hr.employee.profit','employee_id',u'Detalle rentabilidad'),
        'reference_lines': fields.one2many('hr.employee.reference','employee_id',u'Referencias Personales'),
        #'department_id': fields.related('job_id','department_id', type='many2one', relation='hr.department', string=u"Departmento", readonly=True, store=True),
        'academic_ids': fields.one2many('hr.employee.academic','employee_id',u'Formación Académica'),
        'courses_ids': fields.one2many('hr.employee.courses','employee_id',u'Cursos y Capacitaciones'),
        'personal_email': fields.char(u'E-mail Personal', size=240),
        'military_card': fields.char(u'Libreta Militar', size=30),
        #'occupational_code': fields.char(u'Código Ocupacional', size=30),
        'medic_exam': fields.boolean(u'Exámen Médico'),
        'medic_exam_notes': fields.text(u'Observaciones de Exámen'),
        'retencion_judicial': fields.float(u'Retenciones Judiciales'),
        'experience_lines': fields.one2many('hr.employee.experience','employee_id',u'Experiencia Laboral'),
        'work_extension': fields.char(u'Extensión del Trabajo', size=10),
        'address_home_id': fields.char(u'Dirección Domicilio', size=200),
        'address_home_n': fields.char(u'Número Domicilio', size=10),
        'home_phone': fields.char(u'Teléfono Domicilio', size=10),
        'personal_mobile': fields.char(u'Celular', size=10),
        'bank_id': fields.many2one('res.bank', u'Banco'),
        'bank_account_type': fields.many2one('res.partner.bank.type', u'Tipo de Cuenta'),
        'bank_account_id': fields.char(u'Número de Cuenta', size=15),
        'ethnicity_id': fields.many2one('hr.employee.ethnicity', u'Autodefinición Étnica'),
        'firma': fields.binary(u"Firma"),
    }

    _order='name_related'

    _defaults = {
        'retencion_judicial': 0.00,
        'company_id': False,
        'active': True,
    }


    def _check_identificador(self, cr, uid, ids):
        from openerp.addons.gad_tools import functions
        for employee in self.browse(cr, uid, ids):
            if employee.id_type=='c':
                return functions._check_cedula(employee.name)
            else:
                return True

    def _check_duplication(self, cr, uid, ids):
        for employee in self.browse(cr, uid, ids):
            empleados = self.search(cr, uid, [('id_type','=',employee.id_type),('name','=',employee.name)])
            if len(empleados)>1:
                return False
            else:
                return True

    _constraints = [
        (_check_identificador, u'El identificador es inválido, por favor verifique', ['name']),
        (_check_duplication, u'El registro es inválido, no se puede repetir empleados con el mismo identificador', ['id_type','name']),
        ]


l10n_ec_hr_employee()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
