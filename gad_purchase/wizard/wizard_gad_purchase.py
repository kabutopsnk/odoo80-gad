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
#from datetime import datetime
import unicodedata


#***REGRESA A BORRADOR***
class wizard_purchase_requisition_regresa_borrador(osv.osv_memory):
    _name = 'wizard.purchase.requisition.regresa_borrador'
	
    _columns = {
		'descripcion': fields.char(u'Descripción', size=128, required=True),
	}

    def cambia_estado(self, cr, uid, ids, context=None):
        req=context.get('active_id',False)
        for wizard in self.browse(cr, uid, ids, context=None):
            #Elimina Cotizaciones
            for obj in self.pool.get('purchase.requisition').browse(cr, uid, [req]):
                for cot in obj.purchase_ids:
                    print str(cot.id)
                    self.pool.get('purchase.order').unlink(cr, uid, [cot.id])
            self.pool.get('purchase.requisition').write(cr,uid,[req],{'state':'draft','budget_doc_id':False})
            self.pool.get('purchase.requisition')._generate_historial(cr,uid,req,'<-Regresa a Borrador',wizard.descripcion)
        return {'type':'ir.actions.act_window_close'}
    
wizard_purchase_requisition_regresa_borrador()



#***CANCELAR***
class wizard_purchase_requisition_cancelar(osv.osv_memory):
    _name = 'wizard.purchase.requisition.cancelar'
	
    _columns = {
		'descripcion': fields.char(u'Descripción', size=128, required=True),
	}

    def cambia_estado(self, cr, uid, ids, context=None):
        req=context.get('active_id',False)
        for wizard in self.browse(cr, uid, ids, context=None):
            self.pool.get('purchase.requisition').write(cr,uid,[req],{'state':'cancel','budget_doc_id':False})
            self.pool.get('purchase.requisition')._generate_historial(cr,uid,req,'Cancelado',wizard.descripcion)
        return {'type':'ir.actions.act_window_close'}
    
wizard_purchase_requisition_cancelar()



#***CREAR COTIZACIÓN***
class wizard_purchase_requisition_crear_cotizacion(osv.osv_memory):
    _name = 'wizard.purchase.requisition.crear_cotizacion'
	
    _columns = {
		'partner_id': fields.many2one(u'res.partner', u'Proveedor', required=True),
	}

    def crea_cotizacion(self, cr, uid, ids, context=None):
        #Stock Location
        loc=0
        loc_ids=[]
        loc_ids=self.pool.get('stock.location').search(cr, uid, ['|',('name','=','Proveedores'),('name','=','Suppliers')])
        if loc_ids:
            loc=loc_ids[0]
        #Product Pricelist
        ppl=0
        ppl_ids=[]
        ppl_ids=self.pool.get('product.pricelist').search(cr, uid, [('type','=','purchase')])
        if ppl_ids:
            ppl=ppl_ids[0]
        #Fech
        hoy = time.strftime('%Y-%m-%d')

        req=context.get('active_id',False)
        for wizard in self.browse(cr, uid, ids, context=None):
            cot=self.pool.get('purchase.order').create(cr,uid,{'partner_id':wizard.partner_id.id, 'requisition_id':req, 'state':'draft', 'shipped':False, 'location_id':loc, 'pricelist_id':ppl})
            for req_cab in self.pool.get('purchase.requisition').browse(cr, uid, [req], context=None):
                for req_line in req_cab.line_ids:
                    cot_line=self.pool.get('purchase.order.line').create(cr,uid,{'order_id':cot, 'name':req_line.name or '-', 'product_id':req_line.product_id.id, 'product_qty':req_line.product_qty, 'product_uom':req_line.product_uom_id.id, 'price_unit':0.00, 'date_planned':hoy})
        return {'type':'ir.actions.act_window_close'}
    
wizard_purchase_requisition_crear_cotizacion()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
