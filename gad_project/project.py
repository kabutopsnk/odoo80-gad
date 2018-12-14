# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>).
#    Application developed by: Rafael Patricio Argudo Cobos
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
import openerp.addons.decimal_precision as dp
from datetime import datetime, date
import time
#, timedelta
#import datetime
#from datetime import 



#***ANALYTIC_ACCOUNT - ONE2MANY DE LINEAS DE FACTURA***
class analytic_account_invoice_line_(osv.osv):
    '''
    Agregar  Relacion de Analytic_Account y Líneas de Factura
    '''
    _inherit = 'account.analytic.account'
    _columns = {
        'line_ids': fields.one2many('account.invoice.line', 'account_analytic_id', u'Líneas de Factura', readonly=True),
        }

analytic_account_invoice_line_()



#***EJE/COMPONENTE***
class ProjectAxis(osv.Model):

    _name = 'project.axis'
    _description = u'Ejes/Componentes Estratégicos'

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.sequence:
                new_name = ' - '.join([str(r.sequence), new_name])
            res.append((r.id, new_name))
        return res

    _columns = dict(
        name = fields.char(u'Componente', size=64, required=True),
        sequence = fields.char(u'Código', size=5, required=True),
        active = fields.boolean(u'Activo'),
        )

    _defaults = {
        'active': True,
        }

    _order = 'sequence'
    
ProjectAxis()


#***ESTRATEGIA/POLITICA***
class ProjectEstrategy(osv.Model):
    _name = 'project.estrategy'
    _description = u'Áreas'

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.sequence:
                new_name = ' - '.join([str(r.sequence), new_name])
            res.append((r.id, new_name))
        return res

    _columns = dict(
        name = fields.char(u'Área', size=128, required=True),
        axis_id = fields.many2one('project.axis', u'Componente', required=True),
        sequence = fields.char(u'Código', size=5, required=True),
        active = fields.boolean(u'Activo'),
        )

    _defaults = {
        'active': True,
        }

    _order = 'axis_id,sequence'

ProjectEstrategy()


#***PROGRAMA***
class ProjectProgram(osv.Model):

    _name = 'project.program'
    _description = 'Programas'

    def onchange_axis(self, cr, uid, ids, axis_id=False, context=None):
		return {'value': {'estrategy_id': False}}

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.sequence:
                new_name = ' - '.join([str(r.sequence), new_name])
            res.append((r.id, new_name))
        return res

    _columns = dict(
        name = fields.char('Programa', size=128, required=True),
        axis_id = fields.many2one('project.axis', u'Componente', required=True),
        estrategy_id = fields.many2one('project.estrategy', string=u'Área', required=True),
        sequence = fields.char(u'Código', size=5, required=True),
        active = fields.boolean(u'Activo'),
        )

    _defaults = {
        'active': True,
        }

    _order = 'axis_id,estrategy_id,sequence'

ProjectProgram()



#***MODALIDAD***
class ProjectModalidad(osv.Model):

    _name = 'project.modalidad'
    _description = u'Modalidad de Ejecución'

    _columns = dict(
        name = fields.char(u'Modalidad de Ejecución', size=128, required=True),
        sequence = fields.integer(u'Secuencia', required=True),
        )

    _defaults = {
        }

    _order = 'sequence'

ProjectModalidad()



#***DECLARACION DE PROYECTOS***
class ProjectObject(osv.Model):
    """
    Declaración de Proyectos para luego instanciar x Periodo y Presupuesto
    """
    _name = 'project.object'
    _description = 'Declaración de Proyectos'

    _columns = dict(
        code = fields.char(u'Código', size=10, required=True),
        name = fields.char(u'Descripción', size=128, required=True),
        contrato_ids = fields.one2many('project.contrato', 'project_object_id', string=u'Contratos Relacionados'),
        active = fields.boolean(u'Activo'),
        )

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context=None, limit=100):
	    ids = []
	    ids = self.search(cr, uid, [('name',operator,name)] + args, context=context, limit=limit)
	    if not ids:
		    ids = set()
		    ids.update(self.search(cr, uid, args + [('code',operator,name)], limit=limit, context=context))
		    if len(ids) < limit:
			    ids.update(self.search(cr, uid, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
		    ids = list(ids)
	    return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.code:
                new_name = ' - '.join([r.code, new_name])
            res.append((r.id, new_name))
        return res

    _defaults = dict(
        active = True,
        )

    _sql_constraints = [('unique_code', 'unique(code)', u'El código debe ser único...')]

    _order = 'code'

ProjectObject()


#***PROYECTOS***
class ProjectProject(osv.Model):
    """
    Proyectos Principal
    """
    _inherit = 'project.project'

    STATES = {'open':[('readonly',False)]}

    def onchange_axis_project(self, cr, uid, ids, axis_id=False, context=None):
        return {'value': {'estrategy_id': False,'program_id': False}}

    def onchange_estrategy_project(self, cr, uid, ids, estrategy_id=False, context=None):
        return {'value': {'program_id': False}}

    def onchange_project(self, cr, uid, ids, project_object_id=False, context=None):
        codigo = ''
        nombre = ''
        for obj in self.pool.get('project.object').browse(cr, uid, project_object_id):
            codigo = obj.code
            nombre = obj.name
        return {'value': {'code': codigo, 'name': nombre}}

    def estado_open(self,cr,uid,ids,context={}):
        for p in self.browse(cr, uid, ids, context):
            for a in p.tasks:
                self.pool.get('project.task').write(cr,uid,[a.id],{'state':'open'},context=context)
        return self.write(cr,uid,ids,{'state':'open'},context=context)

    def estado_exec(self,cr,uid,ids,context={}):
        for obj in self.browse(cr, uid, ids, context):
            if obj.weight != 100:
                raise osv.except_osv('Error', 'Los pesos de las Actividades son Incorrectos...')
            else:
                for a in obj.tasks:
                    self.pool.get('project.task').write(cr,uid,[a.id],{'state':'exec'},context=context)
                return self.write(cr,uid,ids,{'state':'exec'},context=context)

    def estado_done(self,cr,uid,ids,context={}):
        for p in self.browse(cr, uid, ids, context):
            for a in p.tasks:
                self.pool.get('project.task').write(cr,uid,[a.id],{'state':'done'},context=context)
        return self.write(cr,uid,ids,{'state':'done'},context=context)

    def estado_cancelled(self,cr,uid,ids,context={}):
        for p in self.browse(cr, uid, ids, context):
            for a in p.tasks:
                self.pool.get('project.task').write(cr,uid,[a.id],{'state':'cancelled'},context=context)
        return self.write(cr,uid,ids,{'state':'cancelled'},context=context)

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context=None, limit=100):
	    ids = []
	    ids = self.search(cr, uid, [('name',operator,name)] + args, context=context, limit=limit)
	    if not ids:
		    ids = set()
		    ids.update(self.search(cr, uid, args + [('code',operator,name)], limit=limit, context=context))
		    if len(ids) < limit:
			    ids.update(self.search(cr, uid, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
		    ids = list(ids)
	    return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.code:
                #new_name = ' - '.join([r.crossovered_budget_id.code, r.code, new_name])
                new_name = '%s / %s - %s' % (r.crossovered_budget_id.code, r.code, new_name)
            res.append((r.id, new_name))
        return res

    def _weight_sum(self, cr, uid, ids, names, arg, context=None):
        """
        Suma Pesos de las Actividades
        """
        if context is None:
            context = {}
        res={}
        for project in self.browse(cr, uid, ids, context):
            total = 0
            total = sum([task.weight for task in project.tasks])
            res[project.id]=total
        return res

    def _avance_sum(self, cr, uid, ids, names, arg, context=None):
        """
        Obtiene Avance de Proyecto en base a los Avances de las Actividades
        """
        if context is None:
            context = {}
        res={}
        for project in self.browse(cr, uid, ids, context):
            #res[project.id] = {'avance': 0.00}
            total = 0.00
            total = sum([task.weight*task.avance for task in project.tasks]) / 100.00
            res[project.id]=total
        return res

    def calcular_avance(self,cr,uid,ids,context={}):
        return False

    _columns = dict(
        #Presupuesto
        #, readonly=True, states=STATES
        crossovered_budget_id = fields.many2one('crossovered.budget', string=u'Presupuesto', required=True),
        fy_id = fields.related('crossovered_budget_id', 'fy_id', relation='account.fiscalyear', type='many2one', string=u"Ejercicio Fiscal", store=True, readonly=True),
        budget_type = fields.related('crossovered_budget_id', 'budget_type', type='selection', selection=[('G','Gasto'),('I','Ingreso')], string=u"Tipo Presupuestario", store=True, readonly=True),
        #Proyecto
        project_object_id = fields.many2one('project.object', string=u'Proyecto', required=True),
        code_project = fields.related('project_object_id', 'code', type='char', size=20, string=u'Código', store=True, readonly=True),
        #Información General
        axis_id = fields.many2one('project.axis', string=u'Componente', required=True),
        estrategy_id = fields.many2one('project.estrategy', string=u'Área', required=True),
        program_id = fields.many2one('project.program', string=u'Programa', required=True),
        description = fields.text(u'Descripción', required=True),
        modalidad_id = fields.many2one('project.modalidad', string=u'Modalidad Ejecución', required=True),
        #Valores
        planned_amount = fields.float('INICIAL', required=True, digits_compute=dp.get_precision('Account')),
        transfer_amount = fields.float('Reformas', required=True, digits_compute=dp.get_precision('Account')),
        coded_amount = fields.float('CODIFICADO', required=True, digits_compute=dp.get_precision('Account')),
        used_amount = fields.float('Utilizado', required=True, digits_compute=dp.get_precision('Account')),
        available_amount = fields.float('DISPONIBLE', required=True, digits_compute=dp.get_precision('Account')),
        #DEPARTAMENTO
        department_id = fields.many2one('hr.department', string=u'Departamento/Unidad', required=True),
        #AVANCE
        weight = fields.function(_weight_sum, string=u'Peso Total', method=True, store=False),
        avance = fields.function(_avance_sum, string=u'Avance Proyecto %', method=True, store=False, digits_compute=dp.get_precision('Account')),
        #Estado
        state = fields.selection([('open', 'Planificación'),('exec', 'En Ejecución'),('done', 'Finalizado'),('cancelled', 'Cancelado')], string='Estado', readonly=True),
        indicadores_desempeno = fields.text(u'Indicadores de Desempeño', required=True),
        contrato_ids = fields.one2many('project.contrato', 'project_id', string=u'Contratos Relacionados'),
        seguimiento_senplades = fields.boolean(u'Seguimiento SENPLADES?'),
        )

    _defaults = dict(
        planned_amount = 0.00,
        transfer_amount = 0.00,
        coded_amount = 0.00,
        used_amount = 0.00,
        available_amount = 0.00,
        weight = 0,
        avance = 0.00,
        department_id = 1,
        description = '-',
        indicadores_desempeno = '-',
        )

    _sql_constraints = [('unique_code', 'unique(crossovered_budget_id,project_object_id)', u'Este Proyecto ya está cargado dentro de este Presupuesto...')]

    _order = 'crossovered_budget_id,code_project'

ProjectProject()



#***ACTIVIDADES***
class ProjectTask(osv.Model):
    """
    Actividades
    """
    _inherit = 'project.task'

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context=None, limit=100):
	    ids = []
	    ids = self.search(cr, uid, [('name',operator,name)] + args, context=context, limit=limit)
	    if not ids:
		    ids = set()
		    ids.update(self.search(cr, uid, args + [('code',operator,name)], limit=limit, context=context))
		    if len(ids) < limit:
			    ids.update(self.search(cr, uid, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
		    ids = list(ids)
	    return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.code:
                new_name = ' - '.join([r.code, new_name])
            res.append((r.id, new_name))
        return res

    def _get_budget_lines(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('crossovered.budget.lines').browse(cr, uid, ids, context=context):
            result[line.task_id.id] = True
        return result.keys()

    def _calcular_totales(self, cr, uid, ids, fields, arg, context):
        """
        Metodo que calcula los totales según budget_lines relacionados
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'planned_amount': 0.00, 'transfer_amount': 0.00, 'coded_amount': 0.00, 'used_amount': 0.00, 'available_amount': 0.00}
            for line in obj.budget_lines_ids:
                res[obj.id]['planned_amount'] += line.planned_amount
                res[obj.id]['transfer_amount'] += line.transfer_amount
                res[obj.id]['coded_amount'] += line.coded_amount
                res[obj.id]['used_amount'] += line.used_amount
                res[obj.id]['available_amount'] += line.available_amount
        return res

    _columns = dict(
        code = fields.char(u'Código', size=6, readonly=False, required=True),
        name = fields.char(u'Actividad', size=128, required=True),
        date_start = fields.date(u'Fecha Inicio', required=True),
        date_end = fields.date(u'Fecha Fin', required=True),
        #VALORES
        planned_amount = fields.function(_calcular_totales, string='INICIAL', store=False, method=True, multi='task', digits_compute=dp.get_precision('Account')),
        transfer_amount = fields.function(_calcular_totales, string='Reformas', store=False, method=True, multi='task', digits_compute=dp.get_precision('Account')),
        coded_amount = fields.function(_calcular_totales, string='CODIFICADO', store=False, method=True, multi='task', digits_compute=dp.get_precision('Account')),
        used_amount = fields.function(_calcular_totales, string='Utilizado', store=False, method=True, multi='task', digits_compute=dp.get_precision('Account')),
        available_amount = fields.function(_calcular_totales, string='DISPONIBLE', store=False, method=True, multi='task', digits_compute=dp.get_precision('Account')),
        #AVANCE
        weight = fields.integer(u'Peso', required=True),
        avance = fields.float(u'Avance %', required=True),
        #PRESUPUESTO
        budget_lines_ids = fields.one2many('crossovered.budget.lines', 'task_id', string=u'Líneas Presupuestarias'),
        doc_line_ids = fields.one2many('crossovered.budget.doc.line', 'task_id', string=u'Documentos Presupuestarios', order='budget_doc_id DESC, budget_line_id'),
        reform_line1_ids = fields.one2many('crossovered.budget.reform.line', 'task1_id', string=u'Reformas Disminución', order='budget_reform_id DESC, budget1_id'),
        reform_line2_ids = fields.one2many('crossovered.budget.reform.line', 'task2_id', string=u'Reformas Aumento', order='budget_reform_id DESC, budget2_id'),
        historial_avance_ids = fields.one2many('project.task.historial_avance', 'task_id', string=u'Historial de Avance', order='create_date DESC'),
        state = fields.selection([('open', 'Planificación'),('exec', 'En Ejecución'),('done', 'Finalizado'),('cancelled', 'Cancelado')], string='Estado', readonly=True),
        )

    _defaults = dict(
        planned_amount = 0.00,
        transfer_amount = 0.00,
        coded_amount = 0.00,
        used_amount = 0.00,
        available_amount = 0.00,
        weight = 100,
        avance = 0.00,
        state = 'open',
        )

    _sql_constraints = [('unique_code', 'unique(project_id,code)', u'El código debe ser único...'),
                        ('weight_gt_cero', 'CHECK (weight>0)', 'El Peso debe ser mayor a 0...'),
                        ('weight_lt_cien', 'CHECK (weight<=100)', 'El Peso debe ser menor o igual a 100...'),
                        ('avance_gt_cero', 'CHECK (avance>=0)', 'El Avance debe ser mayor o igual a 0...'),
                        ('avance_lt_cien', 'CHECK (avance<=100)', 'El Avance debe ser menor o igual a 100...')
                        ]

    _order = 'project_id,code'

ProjectTask()



#***HISTORIAL AVANCE ACTIVIDADES***
class ProjectTaskHistorialAvance(osv.osv):
    '''
    Historial de Avances en Actividades
    '''
    _description = 'Historial de Avance de Actividades' 
    _name = 'project.task.historial_avance'  
    _columns = {
        'task_id': fields.many2one('project.task', 'Actividad', readonly=True, required=True, ondelete='cascade'),
        'fecha': fields.date(u'Fecha', required=True),
        'name': fields.text(u'Descripción', required=True),
        'porcentaje': fields.float(u'Avance %', required=True),
        'documento': fields.binary(u'Documento Adjunto', required=False),
        }

    _defaults = {
        'fecha': lambda *a: time.strftime("%Y-%m-%d"),
    }

    _order = 'create_date desc'
             
ProjectTaskHistorialAvance()



#class ProjectCrossoveredBudgetLines(osv.osv):
#    _inherit = 'crossovered.budget.lines'
#
#    _columns = {
#        'estrategy_id': fields.related('project_id', 'estrategy_id', type='many2one', relation="project.estrategy", string=u'Área', store=True, readonly=True),
#        'program_id': fields.related('project_id', 'program_id', type='many2one', relation="project.program", string=u'Programa', store=True, readonly=True),
#    }
#
#ProjectCrossoveredBudgetLines()



#***OBJETO CONTRATACION***
class ProjectContratoObjeto(osv.Model):

    _name = 'project.contrato.objeto'
    _description = u'Objetos de Contratación'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name + ' [' + r.fy_id.name + ']'
            res.append((r.id, new_name))
        return res

    _columns = dict(
        fy_id = fields.many2one('account.fiscalyear', string=u'Ejercicio Fiscal', required=True),
        name = fields.char(u'Objeto Contratación', size=64, required=True),
        sequence = fields.integer(u'Secuencia', required=True),
        active = fields.boolean('Activo'),
        )

    _defaults = {
        'active': True,
        }

    _order = 'sequence'
    
ProjectContratoObjeto()



#***PROCEDIMIENTO CONTRATACION***
class ProjectContratoProcedimiento(osv.Model):
    _name = 'project.contrato.procedimiento'
    _description = u'Procedimientos de Contratación'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name + ' ($' + str(round(r.valor_min,2)) + ' - $' + str(round(r.valor_max,2)) + ')'
            res.append((r.id, new_name))
        return res

    _columns = dict(
        name = fields.char(u'Procedimiento de Contratación', size=64, required=True),
        objeto_id = fields.many2one('project.contrato.objeto', u'Objeto de Contratación', required=True),
        sequence = fields.integer(u'Secuencia', required=True),
        valor_min = fields.float(u'Valor Mínimo', required=True, digits_compute=dp.get_precision('Account')),
        valor_max = fields.float(u'Valor Máximo', required=True, digits_compute=dp.get_precision('Account')),
        active = fields.boolean('Activo'),
        )

    _sql_constraints = [('min_gt_cero', 'CHECK (valor_min>=0)', u'El Valor Mínimo debe ser mayor o igual a 0...'),
                        ('max_gt_cero', 'CHECK (valor_max>=0)', u'El Valor Máximo debe ser mayor o igual a 0...')
                        ]

    _defaults = {
        'valor_min': 0.00,
        'valor_max': 0.00,
        'active': True,
        }

    _order = 'objeto_id,sequence'

ProjectContratoProcedimiento()



#***HISTÓRICO DE ADMINISTRADOR***
class ProjectContratoHistAdministrador(osv.Model):

    _name = 'project.contrato.hist_administrador'
    _description = u'Histórico de Administrador de Contrato'

    _columns = dict(
        contrato_id = fields.many2one('project.contrato', u'Contrato', required=True),
        administrador_id = fields.many2one('hr.employee', 'Administrador', required=True),
        fecha = fields.date(u'Fecha Fin', required=True),
        observaciones = fields.text(u'Observaciones', required=False),
        )

    _order = 'fecha desc'

ProjectContratoHistAdministrador()



#***HISTÓRICO DE FISCALIZADOR***
class ProjectContratoHistFiscalizador(osv.Model):

    _name = 'project.contrato.hist_fiscalizador'
    _description = u'Histórico de Fiscalizador de Contrato'

    _columns = dict(
        contrato_id = fields.many2one('project.contrato', u'Contrato', required=True),
        fiscalizador_id = fields.many2one('hr.employee', 'Fiscalizador', required=True),
        fecha = fields.date(u'Fecha Fin', required=True),
        observaciones = fields.text(u'Observaciones', required=False),
        )

    _order = 'fecha desc'

ProjectContratoHistFiscalizador()



#***CONTRATOS***
class ProjectContract(osv.osv):
    '''
    Contratos de Proyectos
    '''
    _description = 'Contratos' 
    _name = 'project.contrato'

    def estado_draft(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'draft'},context=context)

    def estado_exec(self,cr,uid,ids,context={}):
        
        return self.write(cr,uid,ids,{'state':'exec'},context=context)

    def estado_done(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'done'},context=context)

    def estado_cancelled(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'cancelled'},context=context)

    def onchange_objeto(self, cr, uid, ids, objeto_id=False, context=None):
        return {'value': {'procedimiento_id': False}}

    def _check_monto(self, cr, uid, ids):
        for obj in self.browse(cr, uid, ids):
            if obj.monto < obj.procedimiento_id.valor_min:
                return False
            if obj.monto > obj.procedimiento_id.valor_max:
                return False
        return True

    def create(self, cr, uid, vals, context=None):
        res=[]
        obj_account_analytic_account=self.pool.get('account.analytic.account')
        obj_res_company=self.pool.get('res.company')
        for com in obj_res_company.browse(cr, uid, [1]):
            currency=com.currency_id.id
        analytic = obj_account_analytic_account.create(cr, uid, {'code':vals["code"], 'currency_id':currency, 'user_id':uid, 'date_start':vals['fecha'], 'company_id':1, 'state':'open', 'type':'template', 'description':vals['name'], 'partner_id':vals['partner_id'], 'name':'CONTRATO #'+vals['code'], 'use_tasks':False})
        #Asigna Analytic
        vals['analytic_account_id']=analytic
        #CREA CONTRATO
        res=super(ProjectContract, self).create(cr, uid, vals, context=context)

        return res


    def write(self, cr, uid, ids, vals, context=None):
        #    """
        #    Redefinición de método write
        #    """
        for contrato in self.browse(cr, uid, ids):
            obj_account_analytic_account=self.pool.get('account.analytic.account')
            if vals.has_key('code'):
                obj_account_analytic_account.write(cr, uid, [contrato.analytic_account_id.id], {'code':vals['code'], 'name':'CONTRATO #'+vals['code']})
            if vals.has_key('fecha'):
                obj_account_analytic_account.write(cr, uid, [contrato.analytic_account_id.id], {'date_start':vals['fecha']})
            if vals.has_key('name'):
                obj_account_analytic_account.write(cr, uid, [contrato.analytic_account_id.id], {'description':vals['name']})
            if vals.has_key('partner_id'):
                obj_account_analytic_account.write(cr, uid, [contrato.analytic_account_id.id], {'partner_id':vals['partner_id']})

        return super(ProjectContract, self).write(cr, uid, ids, vals, context)


    _defaults = {
        'code': '/',
        'state': 'draft',
    }

    _columns = {
        'code': fields.char(u'Código', size=32, required=True),
        'name': fields.text(u'Objeto del Contrato', required=True),
        'analytic_account_id': fields.many2one('account.analytic.account', u'Cuenta Analítica de Costos', ondelete="cascade", required=False),
        'partner_id': fields.many2one('res.partner', 'Contratista/Proveedor', required=True),
        'fecha': fields.date(u'Fecha', required=True),
        'plazo': fields.char(u'Plazo', size=64, required=True),
        'monto': fields.float(u'Monto (sin IVA)', digits_compute=dp.get_precision('Account'), required=True),
        'forma_pago': fields.char(u'Forma de Pago', size=64, required=True),
        'porcentaje_anticipo': fields.float(u'Anticipo %', digits_compute=dp.get_precision('Account'), required=True),
        'objeto_id': fields.many2one('project.contrato.objeto', 'Objeto de Contratación', required=False),
        'procedimiento_id': fields.many2one('project.contrato.procedimiento', 'Procedimiento de Contratación', required=False),
        'administrador_id': fields.many2one('hr.employee', 'Administrador', required=False),
        'fiscalizador_id': fields.many2one('hr.employee', 'Fiscalizador', required=False),
        'delegado_id': fields.many2one('hr.employee', 'Delegado Máxima Autoridad', required=False),
        'project_id': fields.many2one('project.project', 'Proyecto Relacionado', required=False),
        'project_object_id' : fields.related('project_id', 'project_object_id', relation='project.object', type='many2one', string=u"Proyecto Objeto", store=True, readonly=True),
        'ubicacion_archivo': fields.char(u'Ubicación Archivo', size=32, required=False),
        'codigo_cp': fields.char(u'Código Compras Públicas', size=32, required=False),
        'garantia_ids': fields.one2many('project.contrato.garantia', 'contrato_id', string=u'Garantías'),
        'administrador_ids': fields.one2many('project.contrato.hist_administrador', 'contrato_id', string=u'Histórico Administrador', readonly=True),
        'fiscalizador_ids': fields.one2many('project.contrato.hist_fiscalizador', 'contrato_id', string=u'Histórico Fiscalizador', readonly=True),
        'state' : fields.selection([('draft', 'Borrador'),('exec', 'En Ejecución'),('done', 'Finalizado'),('cancelled', 'Cancelado')], string='Estado'),
        'observaciones': fields.text(u'Observaciones', required=False),
        'invoice_line_ids': fields.related('analytic_account_id', 'line_ids', type='one2many', relation='account.invoice.line', string=u'Líneas de Factura', readonly=True),
        }

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context=None, limit=100):
	    ids = []
	    ids = self.search(cr, uid, [('name',operator,name)] + args, context=context, limit=limit)
	    if not ids:
		    ids = set()
		    ids.update(self.search(cr, uid, args + [('code',operator,name)], limit=limit, context=context))
		    if len(ids) < limit:
			    ids.update(self.search(cr, uid, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
		    ids = list(ids)
	    return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se reprenta
        en un campo many2one
        """        
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            new_name = r.name
            if r.code:
                new_name = ' - '.join([r.code, new_name])
            res.append((r.id, new_name))
        return res

    _constraints = [(_check_monto, 'El MONTO no coincide con el Procedimiento de Contratación...', ['monto','procedimiento_id']),
                    ]

    _sql_constraints = [('unique_code', 'unique(code)', u'El código debe ser único...'),
                        ('anticipo_gt_cero', 'CHECK (porcentaje_anticipo>=0)', 'El Anticipo debe ser mayor o igual a 0%...'),
                        ('anticipo_lt_cien', 'CHECK (porcentaje_anticipo<=100)', 'El Anticipo debe ser menor o igual a 100%...'),
                        ('monto_gt_cero', 'CHECK (monto>0)', 'El Monto debe ser mayor a $0,00...')
                        ]

    _defaults = {
        'state': 'draft',
        'monto': 0.00,
        'porcentaje_anticipo': 0.00,
        'codigo_cp': '/',
    }

    _order = 'fecha desc'
             
ProjectContract()



#***TIPO GARANTIA***
class ProjectContratoTipoGarantia(osv.Model):

    _name = 'project.contrato.tipo.garantia'
    _description = u'Tipo de Garantía'

    _columns = dict(
        name = fields.char(u'Tipo de Garantía', size=32, required=True),
        sequence = fields.integer(u'Secuencia', required=True),
        )

    _defaults = {
        'sequence':0,
        }

    _order = 'sequence'

ProjectContratoTipoGarantia()



#***HISTÓRICO DE RENOVACIONES GARANTIAS***
class ProjectContratoGarantiaRenovacion(osv.Model):

    _name = 'project.contrato.garantia.renovacion'
    _description = u'Histórico de Renovaciones de Garantías'

    _columns = dict(
        garantia_id = fields.many2one('project.contrato.garantia', u'Garantía', required=True),
        fecha_emision = fields.date(u'Fecha Emisión', required=True),
        fecha_fin = fields.date(u'Fecha Vencimiento', required=True),
        monto = fields.float(u'Monto', digits_compute=dp.get_precision('Account'), required=True),
        observaciones = fields.text(u'Observaciones', required=False),
        )

    _defaults = {
        'monto': 0.00,
    }

    _order = 'fecha_emision'

ProjectContratoGarantiaRenovacion()



#***GARANTIAS***
class ProjectContratoGarantia(osv.osv):
    '''
    Garantias de Contratos
    '''
    _description = 'Contratos' 
    _name = 'project.contrato.garantia'  

    def estado_draft(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'draft'},context=context)

    def estado_exec(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'exec'},context=context)

    def estado_done(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'done'},context=context)

    def estado_cancelled(self,cr,uid,ids,context={}):
        return self.write(cr,uid,ids,{'state':'cancelled'},context=context)

    def _amarillo(self, cr, uid, ids, fields, args, context):
        res={}
        hoy=date.today()
        fecha_ini=datetime(hoy.year,hoy.month,hoy.day,0,0,0)
        dias = 30
        for obj in self.browse(cr, uid, ids):
            fecha=datetime.strptime(obj.fecha_fin,'%Y-%m-%d')
            fecha_fin=datetime(fecha.year,fecha.month,fecha.day,0,0,0)
            amarillo=False
            if fecha_fin<=fecha_ini:
                amarillo=True
            else:
                diferencia=fecha_fin-fecha_ini
                if diferencia.days<=dias:
                    amarillo=True
            res[obj.id] = amarillo
        return res

    def _rojo(self, cr, uid, ids, fields, args, context):
        res={}
        hoy=date.today()
        fecha_ini=datetime(hoy.year,hoy.month,hoy.day,0,0,0)
        dias = 5
        for obj in self.browse(cr, uid, ids):
            fecha=datetime.strptime(obj.fecha_fin,'%Y-%m-%d')
            fecha_fin=datetime(fecha.year,fecha.month,fecha.day,0,0,0)
            rojo=False
            if fecha_fin<=fecha_ini:
                rojo=True
            else:
                diferencia=fecha_fin-fecha_ini
                if diferencia.days<=dias:
                    rojo=True
            res[obj.id] = rojo
        return res


    _columns = {
        'name': fields.char(u'Número de Póliza', size=32, required=True),
        'contrato_id': fields.many2one('project.contrato', 'Contrato', required=True),
        'partner_id': fields.many2one('res.partner', 'Aseguradora', required=True),
        'tipo_id': fields.many2one('project.contrato.tipo.garantia', u'Tipo de Garantía', required=True),
        'fecha_emision': fields.date(u'Fecha Emisión', required=True),
        'fecha_fin': fields.date(u'Fecha Vencimiento', required=True),
        'monto': fields.float(u'Monto', digits_compute=dp.get_precision('Account'), required=True),
        'state' : fields.selection([('draft', 'Borrador'),('exec', 'En Ejecución'),('done', 'Finalizado'),('cancelled', 'Cancelado')], string='Estado'),
        'amarillo': fields.function(_amarillo, store=False, string='X Vencer Preventiva'),
        'rojo': fields.function(_rojo, store=False, string='X Vencer / Vencida'),
        'renovaciones_ids': fields.one2many('project.contrato.garantia.renovacion', 'garantia_id', u'Histórico de Renovaciones', readonly=True),
        'observaciones': fields.text(u'Observaciones', required=False),
        }

    _sql_constraints = [('monto_gt_cero', 'CHECK (monto>0)', 'El Monto debe ser mayor a $0,00...')
                        ]

    _defaults = {
        'state': 'draft',
        'monto': 0.00,
    }

    _order = 'fecha_fin'
             
ProjectContratoGarantia()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
