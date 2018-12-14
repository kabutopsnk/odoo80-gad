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
#from time import strftime
import time
import unicodedata
import exceptions
import openerp.addons.decimal_precision as dp



#***PARTIDAS PRESUPUESTARIAS***
class AccountBudgetPost(osv.Model):
    _inherit = 'account.budget.post'

    def _parent1(self, cr, uid, ids, fields, args, context):
        res={}
        for obj in self.browse(cr, uid, ids):
            parent1=''
            if obj.nivel=='3':
                parent1=' - '.join([obj.parent_id.parent_id.code or '', obj.parent_id.parent_id.name or ''])
            if obj.nivel=='4':
                parent1=' - '.join([obj.parent_id.parent_id.parent_id.code or '', obj.parent_id.parent_id.parent_id.name or ''])
            if obj.nivel=='5':
                parent1=' - '.join([obj.parent_id.parent_id.parent_id.parent_id.code or '', obj.parent_id.parent_id.parent_id.parent_id.name or ''])
            res[obj.id] = parent1
        return res

    def _parent2(self, cr, uid, ids, fields, args, context):
        res={}
        for obj in self.browse(cr, uid, ids):
            parent2=''
            if obj.nivel=='4':
                parent2=' - '.join([obj.parent_id.parent_id.code or '', obj.parent_id.parent_id.name or ''])
            if obj.nivel=='5':
                parent2=' - '.join([obj.parent_id.parent_id.parent_id.code or '', obj.parent_id.parent_id.parent_id.name or ''])
            res[obj.id] = parent2
        return res

    #def _parent3(self, cr, uid, ids, fields, args, context):
    #    res={}
    #    for obj in self.browse(cr, uid, ids):
    #        parent3=''
    #        if obj.nivel=='5':
    #            parent3=' - '.join([obj.parent_id.parent_id.code, obj.parent_id.parent_id.name])
    #        res[obj.id] = parent3
    #    return res

    _columns = {
    'budget_type': fields.selection([('G','Gasto'),('I','Ingreso')], u'Tipo Presupuestario', required=True),
    'nivel': fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], u'Nivel', required=True),
    'type': fields.selection([('view','Vista'),('normal','Normal')], u'Tipo', required=True),
    'parent_id': fields.many2one('account.budget.post', u'Partida Padre'),
    #'parent_id3': fields.function(_parent3, store=False, string='P. Nivel 3', type='text'),
    'parent_id2': fields.function(_parent2, store=False, string='P. Nivel 2', type='text'),
    'parent_id1': fields.function(_parent1, store=False, string='P. Nivel 1', type='text'),
    'child_ids' : fields.one2many('account.budget.post', 'parent_id', 'Detalle Partidas'),
    }

    _sql_constraints = [('unique_code','unique(code)',u'No se pueden registrar Partidas Duplicadas...')]

    _defaults = {
        'nivel': '5',
        'budget_type': 'G',
        'type': 'normal',
    }

    _order = 'code'

    def name_get(self, cr, uid, ids, context=None):
        '''
        Se muestra el codigo y el nombre de la partida
        CODE - NOMBRE
        '''
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            name = ' - '.join([r.code, r.name])
            res.append((r.id, name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid, ['|',('code',operator,name),('name',operator,name)] + args, context=context, limit=limit)
        return self.name_get(cr, uid, ids, context)

AccountBudgetPost()


#***ORIENTACIÓN DEL GASTO***
class crossovered_budget_expense(osv.osv):
    _name = 'crossovered.budget.expense'
    _description = u'Orientación del gasto'
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for this in self.browse(cr, uid, ids, context):
            text = '%s - %s' % (this.code, this.name)
            res.append((this.id, text))
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_nombre = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_nombre))
        if name:
            ids_code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_code))
        return self.name_get(cr, uid, ids, context=context)
    
    _columns = {
                'name': fields.char(u'Orientación de Gasto', size=200, required=True),
                'code': fields.char(u'Código', size=8, required=True),
                'type': fields.selection([('view','Vista'),('normal','Normal')], u'Tipo', required=True),
                'parent_id': fields.many2one('crossovered.budget.expense', u'Padre'),
                }
    
    _order = 'code asc'
    
crossovered_budget_expense()


#***PRESUPUESTOS***
class CrossoveredBudget(osv.osv):
    _inherit = 'crossovered.budget'

    _columns = {
    'fy_id': fields.many2one('account.fiscalyear', u'Ejercicio Fiscal', required=True),
    'budget_type': fields.selection([('G','Gasto'),('I','Ingreso')], u'Tipo Presupuestario', required=True),
    'name': fields.char(u'Descripción', size=32, required=True),
    }

    _defaults = {
    }

    _sql_constraints = [('unique_fy','unique(fy_id,budget_type,state)',u'Sólo se permite una definición por cada Ejercicio Fiscal')]

    _order = 'fy_id DESC, budget_type, state'

CrossoveredBudget()


#***LINEAS DE PRESUPUESTO***
class CrossoveredBudgetLines(osv.osv):
    _inherit = 'crossovered.budget.lines'

    def onchange_project(self, cr, uid, ids, project_id=False, context=None):
        return {'value': {'task_id_ing': False,'budget_line_id_ing': False}}

    def onchange_task(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget_line_id_ing': False}}

    def _get_docs(self, cr, uid, ids, context):
        result = {}
        for budget in self.pool.get('crossovered.budget.doc.line').browse(cr, uid, ids, context=context):
            result[budget.budget_line_id.id] = True
        return result.keys()

    def _get_reforms(self, cr, uid, ids, context):
        result = {}
        for budget in self.pool.get('crossovered.budget.reform.line').browse(cr, uid, ids, context):
            result[budget.budget1_id.id] = True
            result[budget.budget2_id.id] = True
        return result.keys()

    def _calcular_valores(self, cr, uid, ids, fields, arg, context):
        """
        Metodo que calcula los montos de las Líneas de Presupuesto
        """
        res = {}
        line_obj = self.pool.get('crossovered.budget.doc.line')
        reform_obj = self.pool.get('crossovered.budget.reform.line')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'transfer_amount': 0.00, 'coded_amount': 0.00, 'used_amount': 0.00, 'available_amount': 0.00, 'certified_amount': 0.00, 'commited_amount': 0.00}
            #TRANSFER
            sumar = 0.00
            restar = 0.00
                #Reformas de ampliacion o disminucion
            for reforma in obj.reform_line1_ids:
                if reforma.state == 'done' and reforma.type_transaction == 'ampliacion':
                    sumar += reforma.amount
                elif reforma.state == 'done' and reforma.type_transaction in ['disminucion', 'transferencia']:
                    restar += reforma.amount
                #Reforma de transferencias para restar
            for reforma in obj.reform_line2_ids:
                if reforma.state == 'done' and reforma.type_transaction == 'transferencia':
                    sumar += reforma.amount
            res[obj.id]['transfer_amount'] = sumar - restar
            #TOTAL
            res[obj.id]['coded_amount'] = obj.planned_amount + res[obj.id]['transfer_amount']
            #UTILIZADO, CERTIFICADO Y COMPROMETIDO
            line_ids = line_obj.search(cr, uid, [('budget_line_id','=', obj.id),('state','in',['certified','commited'])])
            utilizado=0.00
            certificado=0.00
            comprometido=0.00
            for line in line_obj.browse(cr, uid, line_ids, context):
                if line.state=='certified':
                    certificado+=line.certified_amount
                    utilizado+=line.certified_amount
                if line.state=='commited':
                    comprometido+=line.commited_amount
                    utilizado+=line.commited_amount
            res[obj.id]['used_amount'] = utilizado
            res[obj.id]['certified_amount'] = certificado
            res[obj.id]['commited_amount'] = comprometido
            #DISPONIBLE
            res[obj.id]['available_amount'] = res[obj.id]['coded_amount'] - utilizado
        return res

    STORE_VAR = {'crossovered.budget.reform.line': (_get_reforms, ['amount','type_transaction','state'], 10),
                'crossovered.budget.doc.line': (_get_docs, ['certified_amount','commited_amount','budget_line_id','state'], 10),
                'crossovered.budget.lines': (lambda self, cr, uid, ids, c={}: ids, ['reform_line1_ids','reform_line2_ids','doc_line_ids','planned_amount','transfer_amount','coded_amount','used_amount','available_amount'], 10)
                }

    _columns = {
        'task_id': fields.many2one('project.task', u'Actividad', required=True),
        'project_id': fields.related('task_id', 'project_id', type='many2one', relation="project.project", string=u'Proyecto', store=True, readonly=True),
        'estrategy_id': fields.related('project_id', 'estrategy_id', type='many2one', relation="project.estrategy", string=u'Área', store=False, readonly=True),
        'program_id': fields.related('project_id', 'program_id', type='many2one', relation="project.program", string=u'Programa', store=False, readonly=True),
        'name': fields.text(u'Descripción', required=True),
        'budget_expense_id': fields.many2one('crossovered.budget.expense', u'Orientación de Gasto', required=True),
        'planned_amount':fields.float('INICIAL', required=True, digits_compute=dp.get_precision('Account')),
        'transfer_amount':fields.function(_calcular_valores, string='Reformas', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        'coded_amount':fields.function(_calcular_valores, string='CODIFICADO', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        'used_amount':fields.function(_calcular_valores, string='Utilizado', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        'available_amount':fields.function(_calcular_valores, string='DISPONIBLE', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        'certified_amount':fields.function(_calcular_valores, string='Certificado', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        'commited_amount':fields.function(_calcular_valores, string='Comprometido', store=STORE_VAR, method=True, multi='budget_lines', digits_compute=dp.get_precision('Account')),
        #'budget_type': fields.selection([('G','Gasto'),('I','Ingreso')], u'Tipo Presupuestario', required=False),
        'budget_type': fields.related('general_budget_id', 'budget_type', type='selection', selection=[('G','Gasto'),('I','Ingreso')], string=u'Tipo Presupuestario', store=True),
        'doc_line_ids' : fields.one2many('crossovered.budget.doc.line', 'budget_line_id', 'Documentos Presupuestarios'),
        'reform_line1_ids' : fields.one2many('crossovered.budget.reform.line', 'budget1_id', 'Reformas Origen'),
        'reform_line2_ids' : fields.one2many('crossovered.budget.reform.line', 'budget2_id', 'Reformas Destino'),
        #Relación con Ingresos
        'project_id_ing': fields.many2one('project.project', u'Proyecto', required=False),
        'task_id_ing': fields.many2one('project.task', u'Actividad', required=False),
        'budget_line_id_ing': fields.many2one('crossovered.budget.lines', u'Partida', required=False),
        #Otros / No van
        'date_from': fields.date('Start Date', required=False),
        'date_to': fields.date('End Date', required=False),
        'practical_amount':fields.float(u'Practical Amount'),
        'theoritical_amount':fields.float(u'Theoretical Amount'),
        'percentage':fields.float(u'Percentage'),
    }

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
            #Ingresos
            if r.project_id.budget_type=='I':
                new_name = '%s.%s.%s - %s (%s) -> [%s]' % (r.project_id.code, r.task_id.code, r.general_budget_id.code, r.general_budget_id.name, r.name, r.available_amount)
            #Gastos
            if r.project_id.budget_type=='G':
                area=str(r.project_id.estrategy_id.sequence)
                programa=str(r.project_id.program_id.sequence)
                new_name = '%s.%s.%s%s.%s - %s (%s) -> [%s]' % (r.project_id.code, r.task_id.code, area, programa, r.general_budget_id.code, r.general_budget_id.name, r.name, r.available_amount)
            res.append((r.id, new_name))
        return res

    _defaults = {
        'name': '-',
        'planned_amount': 0.00,
        'transfer_amount': 0.00,
        'coded_amount': 0.00,
        'used_amount': 0.00,
        'available_amount': 0.00,
        'certified_amount': 0.00,
        'commited_amount': 0.00,
    }

    _constraints = []

    ##Validación para que no admita Negativos en Partidas
    #_sql_constraints = [('available_gt_cero', 'CHECK (available_amount>=0)', 'El Valor Disponible no puede ser menor a $0.00...')]
    _sql_constraints = [('available_gt_cero', "CHECK (budget_type='I' OR (budget_type='G' AND available_amount>=0))", 'El Valor Disponible no puede ser menor a $0.00 en Gasto...')]
    #_sql_constraints = [('available_gt_cero', "CHECK (1=1)", 'El Valor Disponible no puede ser menor a $0.00 en Gasto...')]

    _order='project_id,task_id,general_budget_id'

CrossoveredBudgetLines()



#***DOCUMENTOS PRESUPUESTARIOS - CABECERA***
class CrossoveredBudgetDoc(osv.Model):
    
    _name = 'crossovered.budget.doc'
    _description = 'Documentos Presupuestarios'

    def estado_draft(self,cr,uid,ids,context={}):
        line_obj = self.pool.get('crossovered.budget.doc.line')
        if context is None:
            context = {}        
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'draft', 'commited_amount': 0.00})
        return self.write(cr,uid,ids,{'state':'draft'},context=context)

    def estado_certified(self,cr,uid,ids,context={}):
        if context is None:
            context = {}        
        line_obj = self.pool.get('crossovered.budget.doc.line')
        for obj in self.browse(cr, uid, ids, context):
            if not obj.date_certified:
                raise osv.except_osv('Error', 'Para Certificar debe ingresar la Fecha...')
            #Validación Certificado
            if obj.line_ids:
                #fecha = time.strftime('%Y-%m-%d %H:%M:%S')
                line_ids = [line.id for line in obj.line_ids]
                for l in line_obj.browse(cr, uid, line_ids, context):
                    #if l.certified_amount <= 0.00:
                    #    raise osv.except_osv('Error', 'Los valores Certificados deben ser mayores a $0.00...')
                    if l.certified_amount == 0.00:
                        raise osv.except_osv('Error', 'Los valores Certificados deben ser diferentes a $0.00...')
                    if l.certified_amount>l.budget_line_id.available_amount and l.state=='draft' and l.project_id.budget_type=='G':
                        raise osv.except_osv('Error', 'El valor Certificado no puede ser mayor al disponible de la Partida...')
                line_obj.write(cr, uid, line_ids, {'state': 'certified'})
            else:
                raise osv.except_osv('Error', 'El Detalle Presupuestario no puede quedar vacío...')
        #return self.write(cr,uid,ids,{'state':'certified', 'date_certified': fecha}, context=context)
        return self.write(cr,uid,ids,{'state':'certified'}, context=context)

    def estado_commited(self,cr,uid,ids,context={}):
        line_obj = self.pool.get('crossovered.budget.doc.line')
        if context is None:
            context = {}        
        for obj in self.browse(cr, uid, ids, context):
            #Verifica Proveedor y Fecha
            if not obj.partner_id:
                raise osv.except_osv('Error', 'Para Comprometer debe ingresar el Proveedor...')
            if not obj.date_commited:
                raise osv.except_osv('Error', 'Para Comprometer debe ingresar la Fecha...')
            line_ids = [line.id for line in obj.line_ids]
            for l in line_obj.browse(cr, uid, line_ids, context):
                #if l.commited_amount>l.certified_amount:
                #    raise osv.except_osv('Error', 'El valor Comprometido no puede ser mayor al valor Certificado...')
                #if l.commited_amount<=0.00:
                #    raise osv.except_osv('Error', 'El valor Comprometido debe ser mayor a $0.00...')
                if l.commited_amount == 0.00:
                    raise osv.except_osv('Error', 'El valor Comprometido debe ser diferente a $0.00...')
            line_obj.write(cr, uid, line_ids, {'state': 'commited'})
        return self.write(cr,uid,ids,{'state':'commited'},context=context)

    def estado_cancelled(self,cr,uid,ids,context={}):
        line_obj = self.pool.get('crossovered.budget.doc.line')
        if context is None:
            context = {}        
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'cancelled'})
        return self.write(cr,uid,ids,{'state':'cancelled'},context=context)


    _columns = dict(
        #Crea
        user_id = fields.many2one('res.users', string='Creado Por', readonly=True, required=True),
        date_create = fields.datetime(u'Fecha Creación', required=True, readonly=True),
        #Datos
        name = fields.char(u'Código', size=32, required=True, readonly=True),
        description = fields.text(u'Descripción', required=True),
        employee_id = fields.many2one('hr.employee', string='Solicitado Por', required=True),
        observaciones = fields.text('Observaciones'),
        line_ids = fields.one2many('crossovered.budget.doc.line', 'budget_doc_id', 'Detalle'),
        period_id = fields.many2one('account.period', 'Periodo', required=True, readonly=True),
        partner_id = fields.many2one('res.partner', 'Proveedor'),
        date_certified = fields.date('Fecha Certificado'),
        date_commited = fields.date('Fecha Compromiso'),
        state = fields.selection([('draft', 'Borrador'),('certified', 'Certificado'),('commited', 'Comprometido'),('cancelled', 'Cancelado')],string='Estado',required=True),
        )

    _order = 'name DESC'

    _constraints = []

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            texto = r.name + ' - ' + r.description
            texto = texto[:100]
            res.append((r.id, texto))
        return res

    def unlink(self, cr, uid, ids, context):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state not in ['draft']:
                raise osv.except_osv('Error', 'No se permite eliminar registros en este Estado...')
        return super(CrossoveredBudgetDoc, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        """
        Redefinición de metodo create de objeto para asignar una secuencia al documento
        """
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        seq_num = seq_obj.get(cr, uid, 'crossovered.budget.doc')
        if not seq_num:
            raise osv.except_osv('Error', 'No ha configurado la secuencia para este documento.')
        vals['name'] = seq_num
        res_id = super(CrossoveredBudgetDoc, self).create(cr, uid, vals, context)
        return res_id

    def get_period(self, cr, uid, context=None):
        res = self.pool.get('account.period').find(cr, uid)[0]
        return res

    _defaults = dict(
        user_id = lambda self, cr, uid, context: uid,
        date_create = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        date_certified = lambda *a: time.strftime('%Y-%m-%d'),
        name = '/',
        period_id = get_period,
        state = 'draft',
        )

CrossoveredBudgetDoc()



#***DOCUMENTOS PRESUPUESTARIOS - DETALLE***
class CrossoveredBudgetDocLine(osv.Model):
    _name = 'crossovered.budget.doc.line'
    _description = 'Documentos Presupuestarios Detalle'

    DP = dp.get_precision('Presupuestos')

    def _calcular_valores_contables(self, cr, uid, ids, fields, arg, context):
        res = {}
        obj_invbudget = self.pool.get('account.invoice.budget')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                           'accrued_amount': 0.00,
                           'paid_amount': 0.00,
                           }
            invbudget_ids = obj_invbudget.search(cr, uid, [('budget_line_id','=',obj.id)])
            for linea in obj_invbudget.browse(cr, uid, invbudget_ids, context=context):
                if linea.state in ('open','paid'):
                    res[obj.id]['accrued_amount'] += linea.amount
                if linea.state == 'paid':
                    res[obj.id]['paid_amount'] += linea.amount
        return res

    _columns = dict(
        name = fields.text(u'Descripción', required=True),
        budget_doc_id = fields.many2one('crossovered.budget.doc', 'Documento Presupuestario', required=True, ondelete='cascade'),
        project_id = fields.many2one('project.project', 'Proyecto', required=True),
        task_id = fields.many2one('project.task', 'Actividad', required=True),
        budget_line_id = fields.many2one('crossovered.budget.lines', 'Partida Presupuestaria', required=True),
        general_budget_id = fields.related('budget_line_id', 'general_budget_id', type='many2one', relation='account.budget.post', store=True, string='Partida'),
        available_amount = fields.related('budget_line_id', 'available_amount', string='Disponible Partida', type='float', digits_compute=DP),
        #Valores
        certified_amount = fields.float('Valor Certificado', digits_compute=DP, required=True),
        commited_amount = fields.float('Valor Comprometido', digits_compute=DP, required=True),
        accrued_amount = fields.function(_calcular_valores_contables, string=u'Valor Devengado', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
        paid_amount = fields.function(_calcular_valores_contables, string=u'Valor Pagado', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
        state = fields.selection([('draft', 'Borrador'), ('certified', 'Certificado'), ('commited', 'Comprometido'), ('cancelled', 'Cancelado')], string='Estado', required=True, readonly=True),
        )

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
            if r.project_id.code:
                #new_name = ' - '.join([r.crossovered_budget_id.code, r.code, new_name])
                new_name = '%s.%s.%s - %s (%s)' % (r.project_id.code, r.task_id.code, r.general_budget_id.code, r.general_budget_id.name, r.name)
            res.append((r.id, new_name))
        return res

    def create(self, cr, uid ,vals, context=None):
        budget_doc_id = vals['budget_doc_id']
        budget_doc = self.pool.get('crossovered.budget.doc').browse(cr, uid, budget_doc_id, context=context)
        vals['state'] = budget_doc.state
        res_id = super(CrossoveredBudgetDocLine, self).create(cr, uid, vals, context)
        return res_id

    def write_respaldo(self, cr, uid, ids, vals, context=None):
        """
        Redefinición de método write para evitar inconsistencias
        """
        for obj in self.browse(cr, uid, ids, context):
            if vals.has_key('certified_amount'):
                if obj.state == 'certified' and vals['certified_amount'] <= 0.00:
                    raise osv.except_osv('Error', _('El valor Certificado debe ser mayor a $0.00...'))
            if vals.has_key('commited_amount'):
                if obj.state == 'commited' and vals['commited_amount']<=0.00:
                    raise osv.except_osv('Error', _('El valor Comprometido debe ser mayor a $0.00...'))
            if vals.has_key('commited_amount') and not vals.has_key('certified_amount'):
                if vals['commited_amount'] > obj.certified_amount:
                    raise osv.except_osv('Error', _('El valor Comprometido no puede ser mayor al valor Certificado...'))
            if not vals.has_key('commited_amount') and vals.has_key('certified_amount'):
                if obj.commited_amount > vals['certified_amount']:
                    raise osv.except_osv('Error', _('El valor Comprometido no puede ser mayor al valor Certificado...'))
            if vals.has_key('commited_amount') and vals.has_key('certified_amount'):
                if vals['commited_amount'] > vals['certified_amount']:
                    raise osv.except_osv('Error', _('El valor Comprometido no puede ser mayor al valor Certificado...'))
        return super(CrossoveredBudgetDocLine, self).write(cr, uid, ids, vals, context)

    def igual_valor(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        comprometido=0.00
        for obj in self.browse(cr, uid, ids, context):
            if obj.certified_amount:
                comprometido=obj.certified_amount
        return self.write(cr,uid,ids,{'commited_amount':comprometido},context=context) 

    def _check_budget_available(self, cr, uid, ids):
        """
        Validacion de disponible de la partida
        CHECK: default TRUE, *pargudo* solicita
        """
        ##return True
        for obj in self.browse(cr, uid, ids):
            #if obj.certified_amount > 0:
            if obj.project_id.budget_type == 'G':
              if obj.certified_amount > obj.budget_line_id.available_amount:
                return False
        return True

    def _check_values(self, cr, uid, ids):
        """
        """
        for obj in self.browse(cr, uid, ids):
            if (obj.state == 'commited' and obj.amount_compromised != 0): #obj.amount_compromised <= 0):
                return False
            return True

    def _check_budgets(self, cr, uid, ids):
        for obj in self.browse(cr, uid, ids):
            line_ids = self.search(cr, uid, [('budget_doc_id','=',obj.budget_doc_id.id),('budget_line_id','=',obj.budget_line_id.id)])
            if len(line_ids)>1:
                return False
            return True

    def onchange_project(self, cr, uid, ids, project_id=False, context=None):
        return {'value': {'task_id': False,'budget_line_id': False}}

    def onchange_task(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget_line_id': False}}

    def onchange_partida(self, cr, uid, ids, budget_line_id=False, context=None):
        valor=0.00
        for obj in self.browse(cr, uid, ids):
            valor = obj.budget_line_id.available_amount
        return {'value': {'available_amount': valor}}

    def onchange_amount(self, cr, uid, ids, budget_id, amount, state):
        """
        Metodo que implementa una validacion entre
        el disponible y el monto solicitado
        """
        res = {'value': {}}
        if not budget_id or not amount:
            return res
        avai_amount = self.onchange_budget(cr, uid, ids, budget_id)['value']['available_amount']
        if amount > avai_amount:
            res = {'warning': {'title': 'Error de Datos', 'message': 'No puede superar el valor disponible...'},
                   'value': {'certified_amount': 0}}
        return res

    def onchange_budget(self, cr, uid, ids, budget_id):
        res = {'value': {'available_amount': 0}}
        if not budget_id:
            return res
        budget = self.pool.get('crossovered.budget.lines').browse(cr, uid, budget_id)
        res['value']['available_amount'] = budget['available_amount']
        return res

    def change_state(self, cr, uid, ids, state):
        self.write(cr, uid, ids, {'state': state})
        return True

    def unlink(self, cr, uid, ids, context):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state not in ['draft']:
                raise osv.except_osv('Error', 'No se permite eliminar registros en este Estado...')
        return super(CrossoveredBudgetDocLine, self).unlink(cr, uid, ids, context)


    _constraints = [(_check_budget_available, 'No puede superar el valor Disponible de la Partida...', ['Disponibilidad presupuestaria:']),
                    (_check_budgets,'Una actividad/partida en el detalle no puede estar más de una vez...',[]),
                    (_check_values, 'No se puede Comprometer un valor igual Cero...', ['PRESUPUESTOS']),
                    ]

    _defaults = dict(
        name='-',
        certified_amount=0.00,
        commited_amount=0.00,
        accrued_amount=0.00,
        paid_amount=0.00,
        igual_valor=False,
        state='draft',
        )

    _sql_constraints = [('amount_gt_cero', 'CHECK (certified_amount<>0)', 'El Valor Certificado no puede ser igual a $0.00...')
    ]

    _order = 'budget_doc_id DESC, budget_line_id'

CrossoveredBudgetDocLine()



#***REFORMAS PRESUPUESTARIAS - CABECERA***
class CrossoveredBudgetReform(osv.Model):
    
    _name = 'crossovered.budget.reform'
    _description = 'Reformas Presupuestarias'

    DP = dp.get_precision('Presupuestos')

    _columns = dict(
        #Crea
        user_id = fields.many2one('res.users', string='Creado Por', readonly=True, required=True),
        date_create = fields.datetime(u'Fecha Creación', required=True, readonly=True),
        #Datos
        type_transaction = fields.selection([('transferencia', 'TRASPASO'),('ampliacion', 'SUPLEMENTO DE CREDITO'),('disminucion', 'DISMINUCION')], string='Tipo de Reforma', required=True),
        name = fields.char(u'Código', size=32, required=True, readonly=True),
        description = fields.text(u'Descripción', required=True),
        observaciones = fields.text('Observaciones'),
        line_ids = fields.one2many('crossovered.budget.reform.line', 'budget_reform_id', 'Detalle'),
        fecha = fields.date(u'Fecha'),
        state = fields.selection([('draft', 'Borrador'),('done', 'Realizado'),('cancelled', 'Cancelado')],string='Estado',required=True),
        )

    _order = 'name DESC'

    _constraints = []

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            texto = r.name + ' - ' + r.description
            texto = texto[:100]
            res.append((r.id, texto))
        return res

    def unlink(self, cr, uid, ids, context):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state not in ['draft']:
                raise osv.except_osv('Error', 'No se permite eliminar registros en este Estado...')
        return super(CrossoveredBudgetReform, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        """
        Redefinición de metodo create de objeto para asignar una secuencia al documento
        """
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        seq_num = seq_obj.get(cr, uid, 'crossovered.budget.reform')
        if not seq_num:
            raise osv.except_osv('Error', 'No ha configurado la secuencia para este documento.')
        vals['name'] = seq_num
        res_id = super(CrossoveredBudgetReform, self).create(cr, uid, vals, context)
        return res_id

    def estado_draft(self,cr,uid,ids,context={}):
        line_obj = self.pool.get('crossovered.budget.reform.line')
        if context is None:
            context = {}        
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'draft'})
        return self.write(cr,uid,ids,{'state':'draft'},context=context)

    def estado_done(self,cr,uid,ids,context={}):
        if context is None:
            context = {}        
        line_obj = self.pool.get('crossovered.budget.reform.line')
        for obj in self.browse(cr, uid, ids, context):
            #Validación Detalle
            if obj.line_ids:
                line_ids = [line.id for line in obj.line_ids]
                for line in line_obj.browse(cr, uid, line_ids, context):
                    if line.amount<=0.00:
                        raise osv.except_osv('Error', 'El Valor debe ser mayor a $0.00...')
                line_obj.write(cr, uid, line_ids, {'state': 'done'})
            else:
                raise osv.except_osv('Error', 'El Detalle no puede quedar vacío...')
        return self.write(cr,uid,ids,{'state':'done'}, context=context)

    def estado_cancelled(self,cr,uid,ids,context={}):
        line_obj = self.pool.get('crossovered.budget.reform.line')
        if context is None:
            context = {}        
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'cancelled'})
        return self.write(cr,uid,ids,{'state':'cancelled'},context=context)

    def onchange_tipotran(self, cr, uid, ids, type_transaction=False, context=None):
        return {'value': {'line_ids': False}}

    _defaults = dict(
        user_id = lambda self, cr, uid, context: uid,
        date_create = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        fecha = lambda *a: time.strftime('%Y-%m-%d'),
        name = '/',
        type_transaction = 'transferencia',
        state = 'draft',
        )

CrossoveredBudgetReform()



#*** REFORMAS PRESUPUESTARIAS - DETALLE***
class CrossoveredBudgetReformLine(osv.Model):

    _name = 'crossovered.budget.reform.line'
    _description = 'Reformas Presupuestarias Detalle'
    
    DP = dp.get_precision('Presupuestos')

    _columns = dict(
        budget_reform_id = fields.many2one('crossovered.budget.reform', 'Reforma Presupuestaria', required=True, ondelete='cascade'),
        type_transaction = fields.selection([('transferencia', 'TRANSFERENCIA'),('ampliacion', 'AMPLIACION'),('disminucion', 'DISMINUCION')], string='Tipo de Reforma', required=True),
        name = fields.text(u'Descripción', required=True),
        #Origen
        project1_id = fields.many2one('project.project', required=True, string='Proyecto'),
        task1_id = fields.many2one('project.task', required=True, string='Actividad'),
        budget1_id = fields.many2one('crossovered.budget.lines', required=True, string='Partida'),        
        amount_b1 = fields.float(string='Disponible', digits_compute=DP),
        #Destino
        project2_id = fields.many2one('project.project', string='Proyecto'),
        task2_id = fields.many2one('project.task', string='Actividad'),
        budget2_id = fields.many2one('crossovered.budget.lines', string='Partida'),
        amount_b2 = fields.float(string='Disponible', digits_compute=DP),
        #Valor
        amount = fields.float('Valor', required=True, digits_compute=DP),
        state = fields.selection([('draft', 'Borrador'), ('done', 'Realizado'), ('cancelled', 'Cancelado')], string='Estado', required=True),
        )
    
    _order = 'budget_reform_id desc'

    _defaults = dict(
        name='-',
        state='draft',
        )

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for record in self.read(cr, uid, ids, ['state']):
            if record['state'] != 'draft':
                raise osv.except_osv('Error', 'No se permite eliminar en este Estado...')
        return super(CrossoveredBudgetReformLine, self).unlink(cr, uid, ids, context)

    def onchange_project1(self, cr, uid, ids, project_id=False, context=None):
        return {'value': {'task1_id': False,'budget1_id': False}}

    def onchange_task1(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget1_id': False}}

    def onchange_partida1(self, cr, uid, ids, budget1_id, context=None):
        budget = self.pool.get('crossovered.budget.lines')
        res = {'value': {'amount_b1': 0}}
        if budget1_id:
            res['value']['amount_b1'] = budget.browse(cr, uid, budget1_id).available_amount
        return res 

    def onchange_project2(self, cr, uid, ids, project_id=False, context=None):
        return {'value': {'task2_id': False,'budget2_id': False}}

    def onchange_task2(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget2_id': False}}

    def onchange_partida2(self, cr, uid, ids, budget2_id, context=None):
        budget = self.pool.get('crossovered.budget.lines')
        res = {'value': {'amount_b2': 0}}
        if budget2_id:
            res['value']['amount_b2'] = budget.browse(cr, uid, budget2_id).available_amount
        return res 

    def onchange_amount(self, cr, uid, ids, amount, budget_amount, type_transaction):
        '''
        Verificación de monto disponible en partida presupuestaria
        '''
        res = {}
        if type_transaction in ['ampliacion']:
            return res
        if amount and budget_amount:
            if amount > budget_amount:
                res = {'warning': {'title': 'Error', 'message': 'No puede superar el Monto Disponible'}, 'value': {'amount': 0.00}}
        return res

CrossoveredBudgetReformLine()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
