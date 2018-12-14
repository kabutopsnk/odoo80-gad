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

import time
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
from datetime import timedelta
import unicodedata



#***DUPLICAR***
class wizard_account_asset_duplicar(osv.osv_memory):
    _name = 'wizard.account.asset.duplicar'
	
    _columns = {
		'asset_id':fields.many2one('account.asset.asset',u'Activo Fijo a Duplicar', required=True, domain=[('state','=','open')]),
		'cantidad': fields.integer(u'Cantidad', required=True),
		'propiedades': fields.boolean(u'Valores de Propiedades?'),
		'componentes': fields.boolean(u'Valores de Componentes?'),
	}
		
    def duplicar(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=None):
			#Verifica Cantidad
            if wizard.cantidad<=0 or wizard.cantidad>100:
                raise osv.except_osv('Mensaje de Error !', 'Cantidad Incorrecta (De 1 a 100)...')

            #Activo
            for i in range(0,int(wizard.cantidad)): 
                vals = {
                        'clasificador': wizard.asset_id.clasificador,
                        'category_id': wizard.asset_id.category_id.id,
                        'code': '/',
                        'name': wizard.asset_id.name,
                        'employee_id':wizard.asset_id.employee_id.id,
                        'department_id': wizard.asset_id.department_id.id,
                        'partner_id': wizard.asset_id.partner_id.id,
                        'estado': wizard.asset_id.estado,
                        'purchase_value': wizard.asset_id.purchase_value,
                        'purchase_date': wizard.asset_id.purchase_date,
                        'tipo_gasto': wizard.asset_id.tipo_gasto,
                        'salvage_value': wizard.asset_id.salvage_value,
                        'tipo_ingreso':wizard.asset_id.tipo_ingreso,                       
                        'doc_ref': wizard.asset_id.doc_ref,   
                        'numero_ingreso': wizard.asset_id.numero_ingreso,
                        'method_number': wizard.asset_id.method_number,
                        'prorata': wizard.asset_id.prorata,
                        'tiene_iva': wizard.asset_id.tiene_iva,
                        'porcentaje_iva': wizard.asset_id.porcentaje_iva,
                        'invoice_state': wizard.asset_id.invoice_state,
                        'state': 'draft',
                        }
                #GENERA ACTIVO
                asset_id = self.pool.get('account.asset.asset').create(cr, uid, vals, context=context)
                #PROPIEDADES
                if wizard.asset_id.propiedades_ids and wizard.propiedades:
                    for obj_propiedad in wizard.asset_id.propiedades_ids:
                        nuevo_ids=[]
                        nuevo_ids = self.pool.get('account.asset.propiedades').search(cr, uid, [('asset_id','=',asset_id),('category_propiedades_id','=',obj_propiedad.category_propiedades_id.id)])
                        self.pool.get('account.asset.propiedades').write(cr, uid, nuevo_ids, {'valor':obj_propiedad.valor})
                        #self.pool.get('account.asset.propiedades').write(cr, uid, [obj_propiedad.id], {'category_propiedades_id':obj_propiedad.category_propiedades_id.id, 'valor':obj_propiedad.valor, 'asset_id':asset_id}, context=context)                            
                #else:
                #    for obj_propiedad in wizard.asset_id.propiedades_ids:               
                #        self.pool.get('account.asset.propiedades').write(cr, uid, obj_propiedad.id, {'category_propiedades_id':obj_propiedad.category_propiedades_id.id, 'valor':'', 'asset_id':asset_id}, context=context)  
                #COMPONENTES
                if wizard.asset_id.componentes_ids:
                    if wizard.componentes:
                        for obj_componente in wizard.asset_id.componentes_ids:               
                            self.pool.get('account.asset.componentes').copy(cr, uid, obj_componente.id, {'name':obj_componente.name, 'cantidad':obj_componente.cantidad, 'descripcion':obj_componente.descripcion, 'asset_id':asset_id}, context=context)                            
                    else:
                        for obj_componente in wizard.asset_id.componentes_ids:               
                            self.pool.get('account.asset.componentes').copy(cr, uid, obj_componente.id, {'name':obj_componente.name, 'cantidad':obj_componente.cantidad, 'descripcion':'', 'asset_id':asset_id}, context=context)  
                    #if move_id==False:
                    #    move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'asset_id': asset_id,'type':'ingreso','cause':'Registrado en sistema'}, context=None)
                    #if move_id!='':
                    #    self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': asset_id,'move_id':move_id}, context=None)



        return {'type':'ir.actions.act_window_close'}
    
    _defaults = {
        'propiedades':False,
        'componentes':False,
        'cantidad':1,
    }
		
wizard_account_asset_duplicar()



#***DAR DE BAJA 1 Activo - No se usa***
class wizard_account_asset_baja(osv.osv_memory):
    _name = 'wizard.account.asset.baja'
	
    _columns = {
		'asset_id':fields.many2one('account.asset.asset',u'Activo a Dar de Baja', required=True, domain=[('state','=','open')]),
		'fecha': fields.date(u'Fecha de Baja', required=True),
		'motivo': fields.selection([('Fin Vida',u'Fin Vida Útil'),('Deterioro','Deterioro'),('Siniestro','Siniestro'),('Robo','Robo'),(u'Pérdida',u'Pérdida'),('Otro','Otro')], u'Motivo', required=True),
		'detalle': fields.char(u'Detalle de la Baja', size=64, required=True),
	}

    def _get_af(self, cr, uid, context=[]):
        return context.get('active_id',False)

    def baja(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=None):
            #Baja Activo
            self.pool.get('account.asset.asset').write(cr,uid,[wizard.asset_id.id],{'baja_date':wizard.fecha, 'state':'close', 'motivo_baja':wizard.motivo, 'detalle_baja':wizard.detalle})
            #Historial
            vals = {
                    'asset_id': wizard.asset_id.id,
                    'user_id': uid,
                    'name': 'Cambio de Estado',
                    'state': 'close',
                    'descripcion': 'Motivo: ' + wizard.motivo + ' / Detalle: ' + wizard.detalle,
                    }
            historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)

        return {'type':'ir.actions.act_window_close'}
    
    _defaults = {'asset_id':_get_af}
		
wizard_account_asset_baja()



#***CAMBIAR ESTADO DEL BIEN***
class wizard_account_asset_estado_bien(osv.osv_memory):
    _name = 'wizard.account.asset.estado_bien'
	
    _columns = {
		'asset_id':fields.many2one('account.asset.asset',u'Activo Fijo', required=True, domain=[('state','=','open')]),
		'estado': fields.selection([('bueno', 'Bueno'),('regular', 'Regular'),('malo', 'Malo')], u'Estado del Bien', required=True),
	}

    def _get_af(self, cr, uid, context=[]):
        return context.get('active_id',False)

    def estado_bien(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=None):
            #Cambiar Estado del Bien
            self.pool.get('account.asset.asset').write(cr,uid,[wizard.asset_id.id],{'estado':wizard.estado})
            #Historial
            vals = {
                    'asset_id': wizard.asset_id.id,
                    'user_id': uid,
                    'name': 'Cambio Estado del Bien',
                    'estado': wizard.estado,
                    }
            historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)

        return {'type':'ir.actions.act_window_close'}
    
    _defaults = {'asset_id':_get_af}
		
wizard_account_asset_estado_bien()



#***GENERAR FACTURA***
class wizard_account_asset_generar_factura(osv.osv_memory):
    _name = 'wizard.account.asset.generar_factura'
	
    _columns = {
        'partner_id': fields.many2one('res.partner', u'Proveedor', required=True),   
        'journal_id': fields.many2one('account.journal', 'Diario Destino', required=True),
        'account_xpagar_id': fields.many2one('account.account', 'Cta x Pagar', required=True),
        #'journal_type': fields.selection([('purchase_refund', 'Refund Purchase'), ('purchase', 'Create Supplier Invoice'), 
        #                                  ('sale_refund', 'Refund Sale'), ('sale', 'Create Customer Invoice')], 'Journal Type', readonly=True),    
        'activos_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_generar_factura_rel', 'generar_factura_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
	}

    def genera_factura(self, cr, uid, ids, context=None):
        total=0.00
        fecha=None
        doc_ref=None
        company=0
        currency=0
        ingreso=0
        tipo_gasto=''
        valor=0.00
        porc_iva=0.00
        subtotal=0.00
        cantidad=0
        complemento=False
        valor_complemento=0.00
        detalle=[]
        ids_product=[]
        obj_account_asset_asset=self.pool.get('account.asset.asset')
        obj_product_product=self.pool.get('product.product')
        obj_account_invoice=self.pool.get('account.invoice')
        obj_account_invoice_line=self.pool.get('account.invoice.line')
        obj_account_tax=self.pool.get('account.tax')
        #Bucle Principal
        for wiz in self.browse(cr, uid, ids):
            ids = []
            for aux in wiz.activos_ids:
                ids.append(aux.id)
            ids_asset=obj_account_asset_asset.search(cr, uid, [('id','in',ids)], order='numero_ingreso, category_id, tipo_gasto, purchase_value')
            for act in obj_account_asset_asset.browse(cr, uid, ids_asset):
            #for act in wiz.activos_ids:
                if act.clasificador=='bsc':
                    complemento=True
                    valor_complemento+=act.purchase_value
                    if not act.category_id.account_complemento_deb_id.id or not act.category_id.account_complemento_acc_id.id:
                        raise osv.except_osv(_('Error!'), _(u'No están definidas las Cuentas Complementarias en la Categoría '+act.category_id.code+'/'+act.category_id.name))
                    cuenta_d=act.category_id.account_complemento_deb_id.id
                    cuenta_c=act.category_id.account_complemento_acc_id.id
                #Cuentas
                if act.tipo_gasto=='corriente':
                    cuenta=act.category_id.account_asset_id.id
                if act.tipo_gasto=='invobras':
                    cuenta=act.category_id.account_asset_io_id.id
                if act.tipo_gasto=='invprogramas':
                    cuenta=act.category_id.account_asset_ip_id.id
                #Quiebre de Ingreso
                if ingreso!=act.numero_ingreso:
                    cantidad=1
                    #valor=act.purchase_value
                    #subtotal=act.purchase_value
                    valor=act.valor_subtotal
                    porc_iva=act.porcentaje_iva
                    subtotal=act.valor_subtotal
                    #Producto
                    ids_product=obj_product_product.search(cr, uid, [('default_code','=','ACTIVOS-'+act.category_id.code)])
                    if not ids_product:
                        raise osv.except_osv(_('Error!'), _('Producto ' + 'ACTIVOS-'+act.category_id.code + ' No Existe...'))
                    for pro in obj_product_product.browse(cr, uid, ids_product):
                        producto=pro.id
                        uos=pro.uom_id.id
                    #Genera Detalle previo para Factura
                    detalle.append({'ingreso':act.numero_ingreso, 'uos':uos, 'account':cuenta, 'price_unit':valor, 'porc_iva':porc_iva, 'price_subtotal':subtotal, 'producto':producto, 'cantidad':cantidad, 'name':act.name, 'category':act.category_id.id})
                    ###print detalle
                    ingreso=act.numero_ingreso
                    tipo_gasto=act.tipo_gasto
                    #valor=act.purchase_value
                    valor=act.valor_subtotal
                else:
                    #Quiebre de Tipo de Gasto
                    if tipo_gasto!=act.tipo_gasto:
                        cantidad=1
                        #valor=act.purchase_value
                        #subtotal=act.purchase_value
                        valor=act.valor_subtotal
                        porc_iva=act.porcentaje_iva
                        subtotal=act.valor_subtotal
                        detalle.append({'ingreso':act.numero_ingreso, 'uos':uos, 'account':cuenta, 'price_unit':valor, 'porc_iva':porc_iva, 'price_subtotal':subtotal, 'producto':producto, 'cantidad':cantidad, 'name':act.name, 'category':act.category_id.id})
                        tipo_gasto=act.tipo_gasto
                        #valor=act.purchase_value
                        valor=act.valor_subtotal
                    else:
                        #Quiebre de Valor
                        #if valor!=act.purchase_value:
                        if valor!=act.valor_subtotal:
                            cantidad=1
                            #valor=act.purchase_value
                            #subtotal=act.purchase_value
                            valor=act.valor_subtotal
                            porc_iva=act.porcentaje_iva
                            subtotal=act.valor_subtotal
                            detalle.append({'ingreso':act.numero_ingreso, 'uos':uos, 'account':cuenta, 'price_unit':valor, 'porc_iva':porc_iva, 'price_subtotal':subtotal, 'producto':producto, 'cantidad':cantidad, 'name':act.name, 'category':act.category_id.id})
                            #valor=act.purchase_value
                            valor=act.valor_subtotal
                        else:
                            #Acumula items iguales
                            cantidad+=1
                            #subtotal+=act.purchase_value
                            subtotal+=act.valor_subtotal
                            detalle[len(detalle)-1]={'ingreso':act.numero_ingreso, 'uos':uos, 'account':cuenta, 'price_unit':valor, 'porc_iva':porc_iva, 'price_subtotal':subtotal, 'producto':producto, 'cantidad':cantidad, 'name':act.name, 'category':act.category_id.id}
                if fecha:
                    if fecha!=act.purchase_date:
                        raise osv.except_osv(_('Error!'), _('Activos tienen Fecha de Compra diferente...'))
                if doc_ref:
                    if doc_ref!=act.doc_ref:
                        raise osv.except_osv(_('Error!'), _('Activos tienen Doc. Referencia diferente...'))
                fecha=act.purchase_date
                doc_ref=act.doc_ref
                #total=total+act.purchase_value
                total=total+act.valor_subtotal
                company=act.company_id.id
                currency=act.currency_id.id

                #Actualiza estado a Contabilizado
                obj_account_asset_asset.write(cr, uid, act.id, {'invoice_state':'invoiced'})

            #CREA CABECERA
            invoice=obj_account_invoice.create(cr, uid, {'check_total':total, 'company_id':company, 'currency':currency, 'amount_untaxed':total, 'partner_id':wiz.partner_id.id, 'reference_type':'none', 'journal_id':wiz.journal_id.id, 'amount_tax':0.00, 'state':'draft', 'type':'in_invoice', 'account_id':wiz.account_xpagar_id.id, #wiz.partner_id.property_account_payable.id, 
'reconciled':False, 'residual':0.00, 'date_invoice':fecha, 'user_id':uid, 'origin':'AF/'+doc_ref, 'amount_total':total, 'sent':False, 'commercial_partner_id':wiz.partner_id.id})
            #CREA DETALLE
            for det in detalle:
                invoice_det=obj_account_invoice_line.create(cr, uid, {'origin':'IN/AF #'+str(det['ingreso']), 'uos_id':det['uos'], 'account_id':det['account'], 'sequence':10, 'invoice_id':invoice, 'price_unit':det['price_unit'], 'price_subtotal':det['price_subtotal'], 'company_id':company, 'discount':0.00, 'product_id':det['producto'], 'partner_id':wiz.partner_id.id, 'quantity':det['cantidad'], 'name':det['name']+' (Ingreso #'+str(det['ingreso'])+')'})
                tax_ids=[]
                #Impuesto, si no existe no Carga
                tax_ids=obj_account_tax.search(cr, uid, [('amount','=',det['porc_iva']/100),('type_tax_use','=','purchase'),('name','like','%IVA%')], limit=1)
                if tax_ids:
                    cr.execute('INSERT INTO account_invoice_line_tax (invoice_line_id, tax_id) SELECT '+str(invoice_det)+', '+str(tax_ids[0]))
            #CALCULA TOTALES
            obj_account_invoice.button_compute(cr, uid, invoice, context=context, set_total=True)

            #COMPLEMENTO
            if complemento==True:
                #Obtiene Periodo
                obj_account_period=self.pool.get('account.period')
                obj_account_move=self.pool.get('account.move')
                obj_account_move_line=self.pool.get('account.move.line')
                ids_period=[]
                ids_period=obj_account_period.search(cr, uid, [('date_start','<=',fecha),('date_stop','>=',fecha)])
                if not ids_period:
                    raise osv.except_osv(_('Error!'), _('No está definido el Período...'))
                for per in obj_account_period.browse(cr, uid, ids_period):
                    periodo=per.id
                #CREA CABECERA
                move=obj_account_move.create(cr, uid, {'partner_id':wiz.partner_id.id, 'name':'ACTIVOS FIJOS/Complemento '+doc_ref, 'company_id':company, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':fecha, 'ref':'Complemento Doc ' + doc_ref})
                #CREA DETALLE
                move_det1=obj_account_move_line.create(cr, uid, {'company_id':company, 'partner_id':wiz.partner_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':valor_complemento, 'ref':'Complemento Doc ' + doc_ref, 'account_id':cuenta_d, 'period_id':periodo, 'date_created':fecha, 'date':fecha, 'move_id':move, 'name':'ACTIVOS FIJOS Complemento Doc '+doc_ref, 'amount_currency':0.00})
                move_det2=obj_account_move_line.create(cr, uid, {'company_id':company, 'partner_id':wiz.partner_id.id, 'blocked':False, 'credit':valor_complemento, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':'Complemento Doc ' + doc_ref, 'account_id':cuenta_c, 'period_id':periodo, 'date_created':fecha, 'date':fecha, 'move_id':move, 'name':'ACTIVOS FIJOS Complemento Doc '+doc_ref, 'amount_currency':0.00})
        
        return True

    def onchange_proveedor(self, cr, uid, ids, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {},
                        }      
        return res

    _defaults = {
    }
		
wizard_account_asset_generar_factura()



#***GENERAR ASIENTO***
class wizard_account_asset_generar_asiento(osv.osv_memory):
    _name = 'wizard.account.asset.generar_asiento'
	
    _columns = {
        'tipo_ingreso': fields.selection([('tomafisica',u'Toma Física'),('donacion',u'Donación'),('comodato','Comodato'),('inicial','Carga Inicial')], 'Tipo de Ingreso', required=True),
        'partner_id': fields.many2one('res.partner', u'Proveedor', required=False),   
        'journal_id': fields.many2one('account.journal', 'Diario Destino', required=True),
        'date': fields.date(u'Fecha', required=True),
        'activos_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_generar_asiento_rel', 'generar_asiento_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
	}

    def genera_asiento(self, cr, uid, ids, context=None):
        obj_account_period=self.pool.get('account.period')
        obj_account_asset_asset=self.pool.get('account.asset.asset')
        obj_account_move=self.pool.get('account.move')
        obj_account_move_line=self.pool.get('account.move.line')
        #Bucle Principal
        for wiz in self.browse(cr, uid, ids):
            #Obtiene Periodo
            ids_period=[]
            ids_period=obj_account_period.search(cr, uid, [('date_start','<=',wiz.date),('date_stop','>=',wiz.date)])
            if not ids_period:
                raise osv.except_osv(_('Error!'), _('No está definido el Período...'))
            for per in obj_account_period.browse(cr, uid, ids_period):
                periodo=per.id

            ids = []
            for aux in wiz.activos_ids:
                ids.append(aux.id)
            ids_asset=obj_account_asset_asset.search(cr, uid, [('id','in',ids)], order='numero_ingreso, category_id, tipo_gasto')
            for act in obj_account_asset_asset.browse(cr, uid, ids_asset):
            #for act in wiz.activos_ids:
                #Cuentas
                if act.tipo_gasto=='corriente':
                    cuenta=act.category_id.account_asset_id.id
                if act.tipo_gasto=='invobras':
                    cuenta=act.category_id.account_asset_io_id.id
                if act.tipo_gasto=='invprogramas':
                    cuenta=act.category_id.account_asset_ip_id.id
                #Tipos
                if act.tipo_ingreso in ['tomafisica','inicial','donacion']:
                    if not act.category_id.account_donaciones_acc_id.id:
                        raise osv.except_osv(_('Error!'), _(u'No están definidas las Cuentas de Donaciones en la Categoría '+act.category_id.code+'/'+act.category_id.name))
                    cuenta2=act.category_id.account_donaciones_acc_id.id
                if act.tipo_ingreso=='comodato':
                    if not act.category_id.account_comodato_deb_id.id or not act.category_id.account_comodato_acc_id.id:
                        raise osv.except_osv(_('Error!'), _(u'No están definidas las Cuentas de Comodato en la Categoría '+act.category_id.code+'/'+act.category_id.name))
                    cuenta=act.category_id.account_comodato_deb_id.id
                    cuenta2=act.category_id.account_comodato_acc_id.id

                #Actualiza estado a Contabilizado
                obj_account_asset_asset.write(cr, uid, act.id, {'invoice_state':'invoiced'})

                #CREA CABECERA
                move=obj_account_move.create(cr, uid, {'partner_id':act.partner_id.id, 'name':'ACTIVOS FIJOS/Ingreso #'+str(act.numero_ingreso), 'company_id':act.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':act.code+'/'+act.name})
                #CREA DETALLE
                move_det1=obj_account_move_line.create(cr, uid, {'company_id':act.company_id.id, 'partner_id':act.partner_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':act.purchase_value, 'ref':act.name, 'account_id':cuenta, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'ACTIVO FIJO #'+act.code+'/'+act.name, 'amount_currency':0.00})
                move_det2=obj_account_move_line.create(cr, uid, {'company_id':act.company_id.id, 'partner_id':act.partner_id.id, 'blocked':False, 'credit':act.purchase_value, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':act.name, 'account_id':cuenta2, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'ACTIVO FIJO #'+act.code+'/'+act.name, 'amount_currency':0.00})

        return True

    def onchange_tipo(self, cr, uid, ids, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {},
                        }      
        return res

    def onchange_proveedor(self, cr, uid, ids, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {},
                        }      
        return res

    _defaults = {
    }
		
wizard_account_asset_generar_asiento()



#***GENERAR BAJA***
class wizard_account_asset_generar_baja(osv.osv_memory):
    _name = 'wizard.account.asset.generar_baja'
	
    _columns = {
        #'asset_id': fields.many2one('account.asset.asset', 'Activo Fijo a Dar de Baja', required=True),
        'journal_id': fields.many2one('account.journal', 'Diario Destino', required=True),
        'date': fields.date(u'Fecha', required=True),
        'asset_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_baja_rel', 'wizard_id', 'asset_id', 'Activos a Dar de Baja', required=True),
	}

    def genera_baja(self, cr, uid, ids, context=None):
        obj_account_period=self.pool.get('account.period')
        obj_account_asset_asset=self.pool.get('account.asset.asset')
        obj_account_asset_depreciation_line=self.pool.get('account.asset.depreciation.line')
        obj_account_move=self.pool.get('account.move')
        obj_account_move_line=self.pool.get('account.move.line')
        #Bucle Principal
        for wiz in self.browse(cr, uid, ids):
            #Obtiene Periodo
            ids_period=[]
            ids_period=obj_account_period.search(cr, uid, [('date_start','<=',wiz.date),('date_stop','>=',wiz.date)])
            if not ids_period:
                raise osv.except_osv(_('Error!'), _('No está definido el Período...'))
            for per in obj_account_period.browse(cr, uid, ids_period):
                periodo=per.id
            #Recorre ACTIVOS - Baja N Activos
            for activo in wiz.asset_ids:
                if activo.clasificador=='bsc':
                    #CREA CABECERA
                    move=obj_account_move.create(cr, uid, {'name':'BAJA ACTIVO FIJO #'+activo.code, 'company_id':activo.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':activo.code+'/'+activo.name})
                    #CREA DETALLE
                    move_det1=obj_account_move_line.create(cr, uid, {'company_id':activo.company_id.id, 'blocked':False, 'credit':activo.purchase_value, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':activo.name, 'account_id':activo.category_id.account_complemento_deb_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA ACTIVO FIJO #'+activo.code+'/'+activo.name, 'amount_currency':0.00})
                    move_det2=obj_account_move_line.create(cr, uid, {'company_id':activo.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':activo.purchase_value, 'ref':activo.name, 'account_id':activo.category_id.account_complemento_acc_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA ACTIVO FIJO #'+activo.code+'/'+activo.name, 'amount_currency':0.00})

                if activo.clasificador=='bld':
                    #Cuenta de Activo
                    if activo.tipo_gasto=='corriente':
                        cuenta=activo.category_id.account_asset_id.id
                    if activo.tipo_gasto=='invobras':
                        cuenta=activo.category_id.account_asset_io_id.id
                    if activo.tipo_gasto=='invprogramas':
                        cuenta=activo.category_id.account_asset_ip_id.id
                    #Calcula Depreciacion a la Fecha
                    ids_depr=obj_account_asset_depreciation_line.search(cr, uid, [('asset_id','=',activo.id)], order='sequence')
                    valor_depreciacion=0.00
                    for depr in obj_account_asset_depreciation_line.browse(cr, uid, ids_depr):
                        fecha_baja=datetime.strptime(activo.baja_date,'%Y-%m-%d')
                        fecha_depr=datetime.strptime(depr.depreciation_date,'%Y-%m-%d')
                        if fecha_baja.year>fecha_depr.year:
                            valor_depreciacion+=depr.amount
                        if fecha_baja.year==fecha_depr.year:
                            if depr.sequence==1:
                                fecha_ini=datetime(fecha_depr.year,fecha_depr.month,fecha_depr.day,0,0,0)
                                fecha_fin=datetime(fecha_depr.year,12,31,0,0,0)
                                diferencia_fin=fecha_fin-fecha_ini
                                dias=diferencia_fin.days
                            else:
                                fecha_ini=datetime(fecha_depr.year,1,1,0,0,0)
                                fecha_ini=fecha_ini-timedelta(days=1)
                                dias=365
                            diferencia=fecha_baja-fecha_ini
                            if dias>0:
                                valor_depreciacion=valor_depreciacion + round(depr.amount * diferencia.days / dias, 2)
                            valor_patrimonio=activo.purchase_value-valor_depreciacion
                    #CREA CABECERA
                    move=obj_account_move.create(cr, uid, {'name':'BAJA ACTIVO FIJO #'+activo.code, 'company_id':activo.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':activo.code+'/'+activo.name})
                    #CREA DETALLE
                    move_det1=obj_account_move_line.create(cr, uid, {'company_id':activo.company_id.id, 'blocked':False, 'credit':activo.purchase_value, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':activo.name, 'account_id':cuenta, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'ACTIVO FIJO #'+activo.code+'/'+activo.name, 'amount_currency':0.00})
                    move_det2=obj_account_move_line.create(cr, uid, {'company_id':activo.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':valor_depreciacion, 'ref':activo.name, 'account_id':activo.category_id.account_depreciation_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'DEPRECIACION ACTIVO FIJO #'+activo.code+'/'+activo.name, 'amount_currency':0.00})
                    move_det3=obj_account_move_line.create(cr, uid, {'company_id':activo.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':valor_patrimonio, 'ref':activo.name, 'account_id':activo.category_id.account_patrimonio_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA PATRIMONIO ACTIVO FIJO #'+activo.code+'/'+activo.name, 'amount_currency':0.00})

                #Actualiza baja Contabilizado
                obj_account_asset_asset.write(cr, uid, activo.id, {'baja_contabilizada':True})

        baja1activo="""            if wiz.asset_id.clasificador=='bsc':
                #CREA CABECERA
                move=obj_account_move.create(cr, uid, {'name':'BAJA ACTIVO FIJO #'+wiz.asset_id.code, 'company_id':wiz.asset_id.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':wiz.asset_id.code+'/'+wiz.asset_id.name})
                #CREA DETALLE
                move_det1=obj_account_move_line.create(cr, uid, {'company_id':wiz.asset_id.company_id.id, 'blocked':False, 'credit':wiz.asset_id.purchase_value, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':wiz.asset_id.name, 'account_id':wiz.asset_id.category_id.account_complemento_deb_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA ACTIVO FIJO #'+wiz.asset_id.code+'/'+wiz.asset_id.name, 'amount_currency':0.00})
                move_det2=obj_account_move_line.create(cr, uid, {'company_id':wiz.asset_id.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':wiz.asset_id.purchase_value, 'ref':wiz.asset_id.name, 'account_id':wiz.asset_id.category_id.account_complemento_acc_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA ACTIVO FIJO #'+wiz.asset_id.code+'/'+wiz.asset_id.name, 'amount_currency':0.00})

            if wiz.asset_id.clasificador=='bld':
                #Cuenta de Activo
                if wiz.asset_id.tipo_gasto=='corriente':
                    cuenta=wiz.asset_id.category_id.account_asset_id.id
                if wiz.asset_id.tipo_gasto=='invobras':
                    cuenta=wiz.asset_id.category_id.account_asset_io_id.id
                if wiz.asset_id.tipo_gasto=='invprogramas':
                    cuenta=wiz.asset_id.category_id.account_asset_ip_id.id
                #Calcula Depreciacion a la Fecha
                ids_depr=obj_account_asset_depreciation_line.search(cr, uid, [('asset_id','=',wiz.asset_id.id)], order='sequence')
                valor_depreciacion=0.00
                for depr in obj_account_asset_depreciation_line.browse(cr, uid, ids_depr):
                    fecha_baja=datetime.strptime(wiz.asset_id.baja_date,'%Y-%m-%d')
                    fecha_depr=datetime.strptime(depr.depreciation_date,'%Y-%m-%d')
                    if fecha_baja.year>fecha_depr.year:
                        valor_depreciacion+=depr.amount
                    if fecha_baja.year==fecha_depr.year:
                        if depr.sequence==1:
                            fecha_ini=datetime(fecha_depr.year,fecha_depr.month,fecha_depr.day,0,0,0)
                            fecha_fin=datetime(fecha_depr.year,12,31,0,0,0)
                            diferencia_fin=fecha_fin-fecha_ini
                            dias=diferencia_fin.days
                        else:
                            fecha_ini=datetime(fecha_depr.year,1,1,0,0,0)
                            fecha_ini=fecha_ini-timedelta(days=1)
                            dias=365
                        diferencia=fecha_baja-fecha_ini
                        if dias>0:
                            valor_depreciacion=valor_depreciacion + round(depr.amount * diferencia.days / dias, 2)
                        valor_patrimonio=wiz.asset_id.purchase_value-valor_depreciacion
                #CREA CABECERA
                move=obj_account_move.create(cr, uid, {'name':'BAJA ACTIVO FIJO #'+wiz.asset_id.code, 'company_id':wiz.asset_id.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':wiz.asset_id.code+'/'+wiz.asset_id.name})
                #CREA DETALLE
                move_det1=obj_account_move_line.create(cr, uid, {'company_id':wiz.asset_id.company_id.id, 'blocked':False, 'credit':wiz.asset_id.purchase_value, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':wiz.asset_id.name, 'account_id':cuenta, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'ACTIVO FIJO #'+wiz.asset_id.code+'/'+wiz.asset_id.name, 'amount_currency':0.00})
                move_det2=obj_account_move_line.create(cr, uid, {'company_id':wiz.asset_id.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':valor_depreciacion, 'ref':wiz.asset_id.name, 'account_id':wiz.asset_id.category_id.account_depreciation_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'DEPRECIACION ACTIVO FIJO #'+wiz.asset_id.code+'/'+wiz.asset_id.name, 'amount_currency':0.00})
                move_det3=obj_account_move_line.create(cr, uid, {'company_id':wiz.asset_id.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':valor_patrimonio, 'ref':wiz.asset_id.name, 'account_id':wiz.asset_id.category_id.account_patrimonio_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'BAJA PATRIMONIO ACTIVO FIJO #'+wiz.asset_id.code+'/'+wiz.asset_id.name, 'amount_currency':0.00})

            #Actualiza baja Contabilizado
            obj_account_asset_asset.write(cr, uid, wiz.asset_id.id, {'baja_contabilizada':True})
"""


        return True

    _defaults = {
    }
		
wizard_account_asset_generar_baja()



#***GENERAR DEPRECIACIONES***
class wizard_account_asset_generar_depreciaciones(osv.osv_memory):
    _name = 'wizard.account.asset.generar_depreciaciones'
	
    _columns = {
        'fy_id': fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True),
        'journal_id': fields.many2one('account.journal', 'Diario Destino', required=True),
        'account_id': fields.many2one('account.account', u'Cuenta Contable Acreedora', required=True),
        'date': fields.date(u'Fecha', required=True),

	}

    def genera_depreciaciones(self, cr, uid, ids, context=None):
        obj_account_period=self.pool.get('account.period')
        obj_account_asset_asset=self.pool.get('account.asset.asset')
        obj_account_asset_depreciation_line=self.pool.get('account.asset.depreciation.line')
        obj_account_move=self.pool.get('account.move')
        obj_account_move_line=self.pool.get('account.move.line')
        total = 0.00
        #Bucle Principal
        for wiz in self.browse(cr, uid, ids):
            #Obtiene Periodo
            ids_period=[]
            ids_period=obj_account_period.search(cr, uid, [('date_start','<=',wiz.date),('date_stop','>=',wiz.date)])
            if not ids_period:
                raise osv.except_osv(_('Error!'), _('No está definido el Período...'))
            for per in obj_account_period.browse(cr, uid, ids_period):
                periodo=per.id

            #Recorre Activos Fijos en estado Operativo y que tengan que Depreciarse
            ids_asset = []
            ids_asset = obj_account_asset_asset.search(cr, uid, [('state','=','open'),('method_number','>',0)])
            if ids_asset:
                #CREA CABECERA
                move=obj_account_move.create(cr, uid, {'name':'DEPRECIACIONES ACTIVOS FIJOS PERIODO '+wiz.fy_id.name, 'company_id':wiz.fy_id.company_id.id, 'journal_id':wiz.journal_id.id, 'state':'draft', 'period_id':periodo, 'date':wiz.date, 'ref':'DEPRECIACIONES AF '+wiz.fy_id.name})
            for asset in obj_account_asset_asset.browse(cr, uid, ids_asset):
                #Recorre depreciaciones pendientes del periodo seleccionado x activo fijo
                ids_depreciation = obj_account_asset_depreciation_line.search(cr, uid, [('asset_id','=',asset.id),('move_check','=',False)])
                for depr in obj_account_asset_depreciation_line.browse(cr, uid, ids_depreciation):
                    fecha_periodo=datetime.strptime(wiz.fy_id.date_stop,'%Y-%m-%d')
                    fecha_depr=datetime.strptime(depr.depreciation_date,'%Y-%m-%d')
                    if fecha_periodo.year==fecha_depr.year:
                        #Cuenta de Activo
                        if asset.tipo_gasto=='corriente':
                            cuenta=asset.category_id.account_asset_id.id
                        if asset.tipo_gasto=='invobras':
                            cuenta=asset.category_id.account_asset_io_id.id
                        if asset.tipo_gasto=='invprogramas':
                            cuenta=asset.category_id.account_asset_ip_id.id
                        #ACUMULA VALOR
                        total+=depr.amount
                        #CREA DETALLE x ACTIVO al DEBE
                        move_det1=obj_account_move_line.create(cr, uid, {'company_id':asset.company_id.id, 'blocked':False, 'credit':0.00, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':depr.amount, 'ref':asset.name, 'account_id':cuenta, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'DEPRECIACION ACTIVO FIJO #'+asset.code+'/'+asset.name, 'amount_currency':0.00, 'asset_id':asset.id})
                        #Marca como Contabilizada la Línea
                        obj_account_asset_depreciation_line.write(cr, uid, depr.id, {'move_check':True, 'move_id':move})
            #CREA DETALLE TOTALIZADO EN CTA ACREEDORA al HABER
            move_det2=obj_account_move_line.create(cr, uid, {'company_id':wiz.fy_id.company_id.id, 'blocked':False, 'credit':total, 'centralisation':'normal', 'journal_id':wiz.journal_id.id, 'state':'valid', 'debit':0.00, 'ref':'TOTAL DE DEPRECIACIONES PERIODO '+wiz.fy_id.name, 'account_id':wiz.account_id.id, 'period_id':periodo, 'date_created':wiz.date, 'date':wiz.date, 'move_id':move, 'name':'TOTAL DE DEPRECIACIONES DE ACTIVOS FIJOS PERIODO '+wiz.fy_id.name, 'amount_currency':0.00})               

        return True

    _defaults = {
    }
		
wizard_account_asset_generar_depreciaciones()



#***REPORT INGRESO***
class wizard_account_asset_report_ingreso(osv.osv_memory):
    _name = 'wizard.account.asset.report_ingreso'
	
    _columns = {
        #'ingreso': fields.integer(u'Ingreso No.', required=True),
        'partner_id': fields.many2one('res.partner', u'Proveedor'),   
        'fecha': fields.date(u'Fecha', required=True),
		'elaborado_id': fields.many2one('hr.employee', u'Elaborado Por', required=True),        
        'activos_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_ingreso_rel', 'ingreso_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
	}

    def onchange_proveedor(self, cr, uid, ids, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {},
                        }      
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return self.pool['report'].get_action(cr, uid, [], 'gad_account_asset.account_asset_ingreso', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['elaborado_id', 'fecha', 'partner_id', 'activos_ids'], context=context)[0]
        for field in ['elaborado_id', 'fecha', 'partner_id', 'activos_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    _defaults = {
        'fecha': lambda *a: time.strftime("%Y-%m-%d"),
    }
		
wizard_account_asset_report_ingreso()



#***REPORT TARJETA***
class wizard_account_asset_report_tarjeta_bienes(osv.osv_memory):
    _name = 'wizard.account.asset.report_tarjeta_bienes'
	
    _columns = {
        'numero': fields.integer(u'Tarjeta No.', required=True),
        'fecha': fields.date(u'Fecha', required=True),
		'elaborado_id': fields.many2one('hr.employee', u'Elaborado Por', required=True),        
		'employee_id': fields.many2one('hr.employee', u'Responsable / Custodio', required=True),
		'department_id': fields.many2one('hr.department', u'Departamento', required=True),
		'job_id': fields.many2one('hr.job', u'Cargo', required=True),
        'propiedades': fields.boolean(u'Mostrar Propiedades?'),
        'activos_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_tarjeta_bienes_rel', 'tarjeta_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
	}

    def onchange_custodio(self, cr, uid, ids, employee_id, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {}, 'department_id':False, 'job_id':False}

        obj_hr_contract = self.pool.get('hr.contract')
        ids_hr_contract = []
        ids_hr_contract = obj_hr_contract.search(cr,uid,[('employee_id','=',employee_id)],limit=1,order="date_start desc")
        if ids_hr_contract:
            for contract in obj_hr_contract.browse(cr,uid,ids_hr_contract):
                dep=contract.department_id.id
                job=contract.job_id.id
            res['value'] = {'activos_ids': {},'department_id':dep, 'job_id':job}

        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return self.pool['report'].get_action(cr, uid, [], 'gad_account_asset.account_asset_tarjeta', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['elaborado_id', 'numero', 'fecha', 'employee_id', 'department_id', 'job_id', 'propiedades', 'activos_ids'], context=context)[0]
        for field in ['elaborado_id', 'numero', 'fecha', 'employee_id', 'department_id', 'job_id', 'propiedades', 'activos_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    _defaults = {
        'numero': 0,
        'propiedades': False,
        'fecha': lambda *a: time.strftime("%Y-%m-%d"),
    }
		
wizard_account_asset_report_tarjeta_bienes()



#***REPORT CERTIFICADO NO TENER BIENES A CARGO***
class wizard_account_asset_report_certificado_no(osv.osv_memory):
    _name = 'wizard.account.asset.report_certificado_no'
	
    _columns = {
        'fecha': fields.date(u'Fecha', required=True),
		'elaborado_id': fields.many2one('hr.employee', u'Elaborado Por', required=True),        
		'employee_id': fields.many2one('hr.employee', u'Funcionario', required=True),
		'department_id': fields.many2one('hr.department', u'Departamento', required=True),
		'job_id': fields.many2one('hr.job', u'Cargo', required=True),
        'omitir_verificacion': fields.boolean(u'Omitir Verificación?'),
        'activos_ids': fields.many2many('account.asset.asset', 'wizard_account_asset_certificado_no_rel', 'certificado_id', 'asset_id', 'Detalle de Activos Fijos', required=False),
	}

    def onchange_custodio(self, cr, uid, ids, employee_id, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'activos_ids': {}, 'department_id':False, 'job_id':False}

        #Activos a Cargo
        asset_ids=[]
        obj_account_asset = self.pool.get('account.asset.asset')
        asset_ids=obj_account_asset.search(cr, uid, [('employee_id','=',employee_id),('state','=','open')])

        obj_hr_contract = self.pool.get('hr.contract')
        ids_hr_contract = []
        ids_hr_contract = obj_hr_contract.search(cr,uid,[('employee_id','=',employee_id)],limit=1,order="date_start desc")
        if ids_hr_contract:
            for contract in obj_hr_contract.browse(cr,uid,ids_hr_contract):
                dep=contract.department_id.id
                job=contract.job_id.id
            res['value'] = {'activos_ids': asset_ids,'department_id':dep, 'job_id':job}
        else:
            res['value'] = {'activos_ids': asset_ids,'department_id':False, 'job_id':False}

        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        return self.pool['report'].get_action(cr, uid, [], 'gad_account_asset.account_asset_certificado_no', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if context.get('omitir_verificacion')==False:
            if context.get('activos_ids')[0][2]!=[]:
                raise osv.except_osv('Mensaje de Error !', 'Este funcionario TIENE BIENES A SU CARGO...')

        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['elaborado_id', 'fecha', 'employee_id', 'department_id', 'job_id', 'activos_ids'], context=context)[0]
        for field in ['elaborado_id', 'fecha', 'employee_id', 'department_id', 'job_id', 'activos_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        return self._print_report(cr, uid, ids, data, context=context)

    _defaults = {
        'fecha': lambda *a: time.strftime("%Y-%m-%d"),
        'omitir_verificacion':False,
    }
		
wizard_account_asset_report_certificado_no()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
