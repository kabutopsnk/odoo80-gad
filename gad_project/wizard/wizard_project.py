# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
import exceptions

class wizard_task_avance(osv.osv_memory):
    _name = 'wizard.project_task_avance'

    _columns = {
		'task_id':fields.many2one('project.task','Actividad',required=True),
        'fecha': fields.date(u'Fecha', required=True),
        'name': fields.text(u'Descripción', required=True),
		'porcentaje': fields.float(u'Avance %', required=True),
		'documento': fields.binary(u'Documento Adjunto', required=False),
    }
		
    def _get_actividad(self, cr, uid, context=[]):
        return context.get('active_id',False)
	
    def registra_avance(self, cr, uid, ids, context=None):
        obj_actividad = self.pool.get('project.task')
        obj_historial = self.pool.get('project.task.historial_avance')
        for wizard in self.browse(cr, uid, ids, context=None):
            hist_id=obj_historial.create(cr,uid,{'task_id':wizard.task_id.id,'fecha':wizard.fecha,'name':wizard.name,'porcentaje':wizard.porcentaje,'documento':wizard.documento},context=context)
            obj_actividad.write(cr,uid,[wizard.task_id.id],{'avance':wizard.porcentaje})
        return {'type':'ir.actions.act_window_close'}

    _defaults = {'task_id':_get_actividad}
                     
wizard_task_avance()



class wizard_contrato_actualiza_administrador(osv.osv_memory):
    _name = 'wizard.contrato.actualiza_administrador'

    _columns = {
		'contrato_id':fields.many2one('project.contrato','Contrato',required=True, readonly=True),
        'administrador_id': fields.many2one('hr.employee', 'Nuevo Administrador', required=True),
        'fecha': fields.date(u'Fecha Fin Anterior', required=True),
        'observaciones': fields.text(u'Observaciones', required=False),
    }
		
    def _get_contrato(self, cr, uid, context=[]):
        return context.get('active_id',False)
	
    def actualiza_administrador(self, cr, uid, ids, context=None):
        obj_contrato = self.pool.get('project.contrato')
        obj_administrador = self.pool.get('project.contrato.hist_administrador')
        for wizard in self.browse(cr, uid, ids, context=None):
            for contrato in obj_contrato.browse(cr, uid, [wizard.contrato_id.id]):
                administrador_id=obj_administrador.create(cr,uid,
                {'contrato_id':wizard.contrato_id.id, 'fecha':wizard.fecha, 'administrador_id':contrato.administrador_id.id, 'observaciones':wizard.observaciones,}, context=context)
                obj_contrato.write(cr,uid,[wizard.contrato_id.id],{'administrador_id':wizard.administrador_id.id})
        return {'type':'ir.actions.act_window_close'}

    _defaults = {'contrato_id':_get_contrato}
                     
wizard_contrato_actualiza_administrador()



class wizard_contrato_actualiza_fiscalizador(osv.osv_memory):
    _name = 'wizard.contrato.actualiza_fiscalizador'

    _columns = {
		'contrato_id':fields.many2one('project.contrato','Contrato',required=True, readonly=True),
        'fiscalizador_id': fields.many2one('hr.employee', 'Nuevo Fiscalizador', required=True),
        'fecha': fields.date(u'Fecha Fin Anterior', required=True),
        'observaciones': fields.text(u'Observaciones', required=False),
    }
		
    def _get_contrato(self, cr, uid, context=[]):
        return context.get('active_id',False)
	
    def actualiza_fiscalizador(self, cr, uid, ids, context=None):
        obj_contrato = self.pool.get('project.contrato')
        obj_fiscalizador = self.pool.get('project.contrato.hist_fiscalizador')
        for wizard in self.browse(cr, uid, ids, context=None):
            for contrato in obj_contrato.browse(cr, uid, [wizard.contrato_id.id]):
                fiscalizador_id=obj_fiscalizador.create(cr,uid,
                {'contrato_id':wizard.contrato_id.id, 'fecha':wizard.fecha, 'fiscalizador_id':contrato.fiscalizador_id.id, 'observaciones':wizard.observaciones,}, context=context)
                obj_contrato.write(cr,uid,[wizard.contrato_id.id],{'fiscalizador_id':wizard.fiscalizador_id.id})
        return {'type':'ir.actions.act_window_close'}

    _defaults = {'contrato_id':_get_contrato}
                     
wizard_contrato_actualiza_fiscalizador()



class wizard_garantia_renovacion(osv.osv_memory):
    _name = 'wizard.garantia_renovacion'

    _columns = {
		'garantia_id':fields.many2one('project.contrato.garantia','Garantía',required=True, readonly=True),
        'fecha_emision': fields.date(u'Fecha Emisión', required=True),
        'fecha_fin': fields.date(u'Fecha Vencimiento', required=True),
        'monto': fields.float(u'Nuevo Monto', required=True),
        'observaciones': fields.text(u'Observaciones', required=False),
    }
		
    def _get_garantia(self, cr, uid, context=[]):
        return context.get('active_id',False)
	
    def registra_renovacion(self, cr, uid, ids, context=None):
        obj_garantia = self.pool.get('project.contrato.garantia')
        obj_renovacion = self.pool.get('project.contrato.garantia.renovacion')
        for wizard in self.browse(cr, uid, ids, context=None):
            if wizard.monto<=0.00:
                raise osv.except_osv('Error', 'El Monto debe ser Mayor a 0.00...')
            for garantia in obj_garantia.browse(cr, uid, [wizard.garantia_id.id]):
                renovacion_id=obj_renovacion.create(cr,uid,
                {'garantia_id':wizard.garantia_id.id,'fecha_emision':garantia.fecha_emision,'fecha_fin':garantia.fecha_fin,'monto':garantia.monto,'observaciones':garantia.observaciones,}, context=context)
                obj_garantia.write(cr,uid,[wizard.garantia_id.id],{'fecha_emision':wizard.fecha_emision, 'fecha_fin':wizard.fecha_fin, 'monto':wizard.monto, 'observaciones':wizard.observaciones})
        return {'type':'ir.actions.act_window_close'}

    _defaults = {'garantia_id':_get_garantia, 'monto':0.00}
                     
wizard_garantia_renovacion()



#***REPORT GARANTÍAS OFICIO RENOVACIÓN***
class wizard_contrato_garantia_oficio_renovacion(osv.osv_memory):
    _name = 'wizard.contrato.garantia.oficio_renovacion'
    _columns = {
        'num_oficio': fields.char(u'Oficio Nro.', size=32, required=True),
        'fecha': fields.char(u'Ciudad/Fecha', size=32, required=True),
		'partner_id': fields.many2one('res.partner', u'Aseguradora', required=True),
        'ciudad_aseguradora': fields.char(u'Ciudad Aseguradora', size=32, required=True),        
        'garantias_ids': fields.many2many('project.contrato.garantia', 'wizard_contrato_garantia_oficio_renovacion_rel', 'renovacion_id', 'garantia_id', 'Detalle de Garantías', required=True),
		'responsable_id': fields.many2one('hr.employee', u'Responsable/Firma', required=True),
        'cargo_responsable': fields.char(u'Cargo Responsable', size=32, required=True),
		'elaborado_id': fields.many2one('hr.employee', u'Elaborado Por', required=True),
	}

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return self.pool['report'].get_action(cr, uid, [], 'gad_project.report_contrato_garantia_oficio_renovacion', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['num_oficio', 'fecha', 'partner_id', 'ciudad_aseguradora', 'garantias_ids', 'responsable_id', 'cargo_responsable', 'elaborado_id'], context=context)[0]
        for field in ['num_oficio', 'fecha', 'partner_id', 'ciudad_aseguradora', 'garantias_ids', 'responsable_id', 'cargo_responsable', 'elaborado_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    _defaults = {'cargo_responsable':'TESORERO MUNICIPAL'}

wizard_contrato_garantia_oficio_renovacion()



#***REPORT GARANTÍAS OFICIO EJECUCIÓN***
class wizard_contrato_garantia_oficio_ejecucion(osv.osv_memory):
    _name = 'wizard.contrato.garantia.oficio_ejecucion'
    _columns = {
        'num_oficio': fields.char(u'Oficio Nro.', size=32, required=True),
        'fecha': fields.char(u'Ciudad/Fecha', size=32, required=True),
		'partner_id': fields.many2one('res.partner', u'Aseguradora', required=True),
        'ciudad_aseguradora': fields.char(u'Ciudad Aseguradora', size=32, required=True),        
        'garantias_ids': fields.many2many('project.contrato.garantia', 'wizard_contrato_garantia_oficio_ejecucion_rel', 'ejecucion_id', 'garantia_id', 'Detalle de Garantías', required=True),
		'responsable_id': fields.many2one('hr.employee', u'Responsable/Firma', required=True),
        'cargo_responsable': fields.char(u'Cargo Responsable', size=32, required=True),
		'elaborado_id': fields.many2one('hr.employee', u'Elaborado Por', required=True),
	}

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return self.pool['report'].get_action(cr, uid, [], 'gad_project.report_contrato_garantia_oficio_ejecucion', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['num_oficio', 'fecha', 'partner_id', 'ciudad_aseguradora', 'garantias_ids', 'responsable_id', 'cargo_responsable', 'elaborado_id'], context=context)[0]
        for field in ['num_oficio', 'fecha', 'partner_id', 'ciudad_aseguradora', 'garantias_ids', 'responsable_id', 'cargo_responsable', 'elaborado_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    _defaults = {'cargo_responsable':'TESORERO MUNICIPAL'}

wizard_contrato_garantia_oficio_ejecucion()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
