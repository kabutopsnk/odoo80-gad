# -*- coding: utf-8 -*-
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

from openerp.osv import osv, fields
import time
from openerp.tools.translate import _

class HistorialRequisition(osv.Model):
    _name = 'purchase.requisition.historial'

    _columns = dict(
        accion = fields.char(u'Acción',size=32),
        descripcion = fields.char(u'Detalle',size=128),
        requisition_id = fields.many2one('purchase.requisition','Solicitud'),
        )

    _order = 'create_date desc'

HistorialRequisition


class ParametrosRequisition(osv.Model):
    _name = 'purchase.requisition.parametros'
    _columns = dict(
        monto_max = fields.float(u'Monto Máximo', required=True),
        user_autoriza_id = fields.many2one('res.users','Usuario Autoriza monto mayor', required=True, help="Solo este usuario puede autorizar compras mayores al monto máximo permitido"),
	active=fields.boolean('Activo'),
        )

    _defaults=dict(
        monto_max = 0.00,
        user_autoriza_id = 1,
        active = True,
        )

    _sql_constraints = [
        ('unique_active', 'unique(active)', 'Los Parámetros solo puede tener un registro Activo...')
        ]

ParametrosRequisition


class PurchaseReqModified(osv.Model):
    
    _inherit='purchase.requisition'
    _description = 'GAD Solicitud de Compra'

    def _generate_historial(self, cr, uid, id, accion, descripcion, context=None ):
        log_obj = self.pool.get('purchase.requisition.historial')
        log_obj.create(cr, uid, {
                'accion':accion,
                'descripcion':descripcion,
                'requisition_id':id,
                })
        return True

    def in_progress(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            if len(obj.line_ids)<=0:
                raise osv.except_osv(_('Error!'), _('El Detalle de Productos no puede quedar vacío...'))
        self._generate_historial(cr, uid, ids[0], '1. En Proceso', '')
        return self.write(cr, uid, ids, {'state': 'in_progress'}, context=context)

    def approved(self, cr, uid, ids, context=None):
        self._generate_historial(cr, uid, ids[0], '2. Aprobado', '')
        return self.write(cr, uid, ids, {'state': 'approved'}, context=context)

    def certified(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            if obj.budget_doc_id.id==False:
                raise osv.except_osv(_('Error!'), _('Para CERTIFICAR debe seleccionar el Documento Presupuestario...'))
        self._generate_historial(cr, uid, ids[0], '3. Certificado', '')
        return self.write(cr, uid, ids, {'state': 'certified'}, context=context)

    def authorized(self, cr, uid, ids, context=None):
        cont=0
        total=0.00
        for obj in self.browse(cr, uid, ids):
            for cot in obj.purchase_ids:
                if cot.shipped:
                    cont+=1
                    total=cot.amount_total
            #No hay cotizaciones, no selecciona ninguna o selecciona más de una
            if cont!=1:
                raise osv.except_osv(_('Error!'), _('Para AUTORIZAR debe estar marcada una Cotización Seleccionada...'))
            #Supera el monto máximo y no es super usuario
            param_ids=[]
            param_ids = self.pool.get('purchase.requisition.parametros').search(cr, uid, [('active','=',True)])
            for param in self.pool.get('purchase.requisition.parametros').browse(cr, uid, param_ids):
                if total>param.monto_max and param.user_autoriza_id.id!=uid:
                    raise osv.except_osv(_('Error!'), _('El Usuario actual no puede AUTORIZAR compras mayores a $'+str(param.monto_max)+'...'))
                
        self._generate_historial(cr, uid, ids[0], '4. Autorizado', '')
        return self.write(cr, uid, ids, {'state': 'authorized'}, context=context)

    def done(self, cr, uid, ids, context=None):
        cont=0
        obj_order=self.pool.get('purchase.order')
        for obj in self.browse(cr, uid, ids):
            for cot in obj.purchase_ids:
                if cot.shipped:
                    cont+=1
                    obj_order.write(cr, uid, [cot.id], {'state':'done'}, context=context)
            #No hay cotizaciones, no selecciona ninguna o selecciona más de una
            if cont!=1:
                raise osv.except_osv(_('Error!'), _('Para FINALIZAR y Generar la Orden de Compra, debe estar marcada una Cotización Seleccionada...'))

        self._generate_historial(cr, uid, ids[0], '5. Finalizado', '')
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    _columns = dict(
        detalle = fields.text(u'Detalle del Requerimiento', required=True),
        #total_compra = fields.function(_compute_money,string='Total Aut. (Inc. IVA)$',type="float",store=False, help="Total en USD que suma cada uno de los items de las cotizaciones aprobadas"),
        #total_cotizaciones = fields.function(_compute_money_cot,string='Total Cotiz. Selec. (Inc. IVA) $',type="float", store=False, help="Es el total en USD que suma cada uno de los items de cada una de las cotizaciones recomendadas"),
        #usr_solicitant_id = fields.related('solicitant_id','user_id', type='many2one', relation='res.users',string='Usr. Solicitante', store=True),
        solicitant_id = fields.many2one('hr.employee','Solicitante',required=True),
        #anulant_id = fields.many2one('res.users','Anulado por'),
        #aprobador_id = fields.many2one('res.users','Aprobado por'),
        #recibe_id = fields.many2one('hr.employee','Recibe'),
        state = fields.selection([('draft','Borrador'),('in_progress','1.En Proceso'),('approved','2.Aprobado'),('certified','3.Certificado'),
				('authorized','4.Autorizado'),('done','5.Finalizado'),('cancel','Cancelado'),], 'Estado', required=True),
        department_id = fields.many2one('hr.department','Dpto./Unidad Operativa'),
        #purchase_id = fields.many2one('purchase.order','Order Compra Relacionada'),
        #active = fields.boolean('Agrupada'),
        #justifi = fields.char('Justificación',size=128),
        budget_doc_id = fields.many2one('crossovered.budget.doc','Doc. Presupuesto',help="Permite seleccionar los Documentos Presupuestarios Certificados y que no esten siendo utilizados en otra Solicitud"),
        #observation = fields.char('Comentario',size=256, help="Coloque aquí su comentario referente al proceso de la solicitud de compra"),
        #cotizar_all = fields.boolean('Cotizar todo',help="Si usted selecciona esta opción las cotizaciones a los diferentes proveedores se crearán con las cantidades requeridas, caso contrario se realizarán solamente con la diferencia o faltante en inventario"),
        #unidad_id = fields.many2one('stock.location','Bodega',required=True,readonly=True),
        #referencia_bodega = fields.char('Referencia',size=32),
        #picking_id = fields.many2one('stock.picking','Egreso',readonly=True),
        #criterio_rec = fields.text('Criterio Recomendación'),
        #criterio_sel = fields.text('Criterio Selección'),
        #tabla_id = fields.many2one('purchase.config.infima','Periodo Fiscal'),
        #revert = fields.boolean('Devuelto'),
        #total_items = fields.integer('Total Items'),
        #contract_object = fields.selection([('product','Bienes Consumibles'),('service','Servicios'),('asset','Activos'),
        #                                    ('pa','Bienes y Activos'),('ps','Bienes y Servicios')],
        #                                   'Objeto Compra',required="1"),
        #str_tipos = fields.char('Tipos',size=32),
        observaciones = fields.text('Observaciones'),
        #purchase_select_ids = fields.one2many('purchase.order','requisition_select_id','Cotizaciones',
        #                                      states={'done': [('readonly', True)]}),
        #code_po = fields.char('Codigo Interno', size=16),
        #objeto_id_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        #son_repuestos = fields.boolean('Son repuestos?'),
        historial_ids = fields.one2many('purchase.requisition.historial','requisition_id','Historial'),
        )

    def _check_doc_presup(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            if obj.budget_doc_id.id:
                obj_ids=[]
                obj_ids=self.search(cr, uid, [('budget_doc_id','=',obj.budget_doc_id.id),('state','not in',['draft','cancel'])])
                if len(obj_ids)>1:
                    return False
        return True

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        vals['name'] = obj_sequence.get(cr, uid, 'purchase.order.requisition')

        return super(PurchaseReqModified, self).create(cr, uid, vals, context=None)

    _defaults = dict(
        state = 'draft',
	name = '/',
        )

    _constraints = [
        (_check_doc_presup,'El Documento Presupuestario seleccionado ya se está utilizando otra Solicitud de Compra...',['state','budget_doc_id']),
        ] 

    _order = 'name desc'

PurchaseReqModified()



class purchaseRequisitionLine(osv.Model):
    _inherit = 'purchase.requisition.line'

    _columns = dict(
        name = fields.char(u'Descripción', size=128),
        #solicitant_id = fields.many2one('hr.employee','Solicitante',required=True),
        #state = fields.selection([('draft','Borrador'),('in_progress','1.En Proceso'),('approved','2.Aprobado'),('certified','3.Certificado'),
		#		('authorized','4.Autorizado'),('done','5.Finalizado'),('cancel','Cancelado'),], 'Estado', required=True),
        caracteristicas = fields.text(u'Características'),
        )

    def onchange_product_id2(self, cr, uid, ids, product_id, product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {'product_uom_id': prod.uom_id.id, 'product_qty': 1.0}
        return {'value': value}

    _defaults = dict(
        #state = 'draft',
        )

purchaseRequisitionLine()



class purchaseOrder(osv.osv):
    _inherit = "purchase.order"

    def unlink(self, cr, uid, ids, context=None):
        return super(purchaseOrder, self).unlink(cr, uid, ids, context=context)

    _columns = dict(
        state = fields.selection([('draft', 'Registrado'), ('cancel', 'Cancelado'), ('done', 'Genera O/C')], string="Estado", readonly=True, select=True, copy=False),
        )

    _sql_constraints = [
        ('unique_partner_req', 'unique(requisition_id,partner_id)', 'Solo puede crear una Cotización x Proveedor...')
        ]

    _order = 'name desc'

purchaseOrder()



class purchaseOrderLine(osv.Model):
    _inherit = 'purchase.order.line'

    _columns = dict(
        product_uom = fields.many2one('product.uom', 'Product Unit of Measure', required=False),
        caracteristicas = fields.text(u'Características'),
        )

purchaseOrderLine()

