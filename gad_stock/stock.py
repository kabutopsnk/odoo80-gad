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
import time
import openerp.addons.decimal_precision as dp

class stock_picking_document(osv.osv):
    _name = 'stock.picking.doc'
    _description = u'Documento de Transacción en Bodega'
    
    _columns = {
                'name': fields.char(u'Documento', size=50, required=True),
                }
    
    _sql_constraints = [
                        ('unique_name', 'unique(name)', u'Solo puede crear 1 documento con el nombre indicado.')
                        ]
    
stock_picking_document()

class picking_out_account(osv.osv):
    _name = 'picking.out.account'
    _description = u'Interfaz contable de Egresos en Bodega'
    
    _columns = {
                'date': fields.date(u'Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'line_ids': fields.one2many('picking.out.account.line', 'picking_out_id', u'Detalle', readonly=True),
                'period_id': fields.many2one('account.period', u'Periodo', required=True, domain=[('state','=','draft')], readonly=True, states={'draft': [('readonly', False)]}),
                'type_id': fields.many2one('stock.picking.type', u'Operación', required=True, domain=[('code','=','outgoing')], readonly=True, states={'draft': [('readonly', False)]}),
                'state': fields.selection([('draft','Borrador'),('done','Realizado')], u'Estado', readonly=True),
                'move_id': fields.many2one('account.move', u'Asiento Contable', readonly=True),
                'journal_id': fields.many2one('account.journal', u'Diario', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                #'picking_ids':fields.many2many('stock.picking', 'rel_picking_account', 'out_id', 'picking_id', u'Operaciones',)
                }
    
    _order = 'date desc, state, period_id desc'
    
    _defaults = {
                 'state': 'draft',
                 #'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                 'date': time.strftime('%Y-%m-%d'),
                 }
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state != 'draft':
                raise osv.except_osv(('Operación no permitida !'), ('Solo se puede eliminar en estado Borrador'))
        return super(picking_out_account, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def calcular_asiento(self, cr, uid, ids, context={}):
        resultados = {}
        obj_stock = self.pool.get("stock.picking")
        obj_detail = self.pool.get("picking.out.account.line")
        resultado = {}
        for this in self.browse(cr, uid, ids):
            detail_ids = obj_detail.search(cr, uid, [('picking_out_id','=',this.id)])
            if detail_ids:
                obj_detail.unlink(cr, uid, detail_ids)
            picking_ids = obj_stock.search(cr, uid, [('picking_type_id','=',this.type_id.id),
                                                     ('date_done','>=',this.period_id.date_start),
                                                     ('date_done','<=',this.period_id.date_stop),
                                                     ('invoice_state','=','2binvoiced')])
            for picking in obj_stock.browse(cr, uid, picking_ids, context={}):
                for line in picking.move_lines:
                    if not line.product_id.categ_id.property_stock_account_output_categ:
                        raise osv.except_osv(u'Error de Configuración', u'La categoría del producto ' + line.product_id.name + ' no tiene configurada la cuenta de salida de stock')
                    if not (line.product_id.property_account_expense or line.product_id.categ_id.property_account_expense_categ):
                        raise osv.except_osv(u'Error de Configuración', u'La categoría del producto ' + line.product_id.name + ' no tiene configurada la cuenta de salida de stock')
                    expense_account = line.product_id.property_account_expense and line.product_id.property_account_expense.id or line.product_id.categ_id.property_account_expense_categ.id
                    out_account = line.product_id.categ_id.property_stock_account_output_categ.id
                    if picking.analytic_account_id.id not in resultados.keys():
                        resultados[picking.analytic_account_id.id] = {expense_account : {'debit': 0, 'credit':0}}
                        resultados[picking.analytic_account_id.id] = {out_account : {'debit': 0, 'credit':0}}
                    if expense_account not in resultados[picking.analytic_account_id.id].keys():
                        resultados[picking.analytic_account_id.id][expense_account] = {'debit': 0, 'credit':0}
                    if out_account not in resultados[picking.analytic_account_id.id].keys():
                        resultados[picking.analytic_account_id.id][out_account] = {'debit': 0, 'credit':0}
                    resultados[picking.analytic_account_id.id][expense_account]['debit'] += (line.product_uom_qty * line.price_unit)
                    resultados[picking.analytic_account_id.id][out_account]['credit'] += (line.product_uom_qty * line.price_unit)
            for centro_costo in resultados.keys():
                for cuenta in resultados[centro_costo].keys():
                    obj_detail.create(cr, uid, {
                                                'picking_out_id': this.id,
                                                'account_id': cuenta,
                                                'analytic_account_id': centro_costo,
                                                'debit': resultados[centro_costo][cuenta]['debit'],
                                                'credit': resultados[centro_costo][cuenta]['credit'],
                                                })
                    
                    
    def crear_asiento(self, cr, uid, ids, context={}):
        obj_move = self.pool.get('account.move')
        obj_line = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            move_id = obj_move.create(cr, uid, {
                                                'journal_id': this.journal_id.id,
                                                'period_id': this.period_id.id,
                                                'date': this.date,
                                                })
            for line in this.line_ids:
                obj_line.create(cr, uid, {
                                          'move_id': move_id,
                                          'account_id': line.account_id.id,
                                          'analytic_account_id': line.analytic_account_id.id,
                                          'debit': line.debit,
                                          'credit': line.credit,
                                          'name': 'Egresos Inventario',
                                          })
            self.write(cr, uid, this.id, {'move_id': move_id, 'state':'done'})
    
picking_out_account()

class picking_out_account_line(osv.osv):
    _name = 'picking.out.account.line'
    _description = u'Detalle de interfaz contable de Egresos en Bodega'
    
    _columns = {
                'picking_out_id': fields.many2one('picking.out.account', u'Interfaz de Egresos', ondelete="cascade"),
                'account_id': fields.many2one('account.account', u'Cuenta Contable', required=True),
                'analytic_account_id': fields.many2one('account.analytic.account', u'Centro de Costo', required=True, domain=[('type','=','contract')]),
                'debit': fields.float(u'Débito'),
                'credit': fields.float(u'Crédito'),
                #'amount': fields.float(u'Valor'),
                #'move_type': fields.selection([('D',u'Débito'),('C',u'Crédito')], u'Tipo de movimiento', required=True),
                }
    
    _order = 'picking_out_id desc, account_id'
    
    _defaults = {
                 'debit': 0,
                 'credit': 0,
                 }
    
picking_out_account_line()

class gads_stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
                'doc_id': fields.many2one('stock.picking.doc', u'Documento', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
                'analytic_account_id': fields.many2one('account.analytic.account', u'Centro de Costo', domain=[('type','=','contract')], states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
                'employee_id': fields.many2one('hr.employee', u'Responsable'),
                }
    
    _defaults = {
                 'move_type': 'one',
                 'invoice_state': '2binvoiced',
                 }
    
    def crear_egreso(self, cr, uid, ids, context={}):
        obj_picking = self.pool.get("stock.picking")
        obj_move = self.pool.get("stock.move")
        for this in self.browse(cr, uid, ids):
            data = {
                    'invoice_state': '2binvoiced',
                    'move_type': 'one',
                    'picking_type_id': this.picking_type_id.id + 1,
                    'origin': this.name,
                    }
            picking_id = obj_picking.create(cr, uid, data, context=context)
            for linea in this.move_lines:
                data_line = {
                             'picking_id': picking_id,
                             'origin': this.name,
                             'invoice_state': '2binvoiced',
                             'picking_type_id': this.picking_type_id.id + 1,
                             'product_id': linea.product_id.id,
                             'product_uom': linea.product_uom.id,
                             'price_unit': linea.product_id.standard_price,
                             'product_uom_qty': linea.product_uom_qty,
                             'product_uos_qty': linea.product_uos_qty,
                             #'product_qty': linea.product_qty,
                             'name': linea.name,
                             }
                obj_move.create(cr, uid, data_line, context=context)
            
            #return {
            #        'type': 'ir.actions.act_window',
            #        'res_model': 'stock.picking',
            #        'view_type': 'form',
            #        'view_mode': 'form',
            #        #'target': 'new',
            #        }
    

    def _check_incoming(self, cr, uid, ids):
        for this in self.browse(cr, uid, ids):
            if this.state not in ['draft','cancel']:
                if this.picking_type_code == 'incoming' and not (this.partner_id):
                    return False
                elif this.picking_type_code == 'incoming' and this.analytic_account_id:
                    return False
                else:
                    return True
            else:
                return True
            
    def _check_outgoing(self, cr, uid, ids):
        for this in self.browse(cr, uid, ids):
            if this.state not in ['draft','cancel']:
                if this.picking_type_code == 'outgoing' and not (this.analytic_account_id):
                    return False
                elif this.picking_type_code == 'outgoing' and this.partner_id:
                    return False
                else:
                    return True
            else:
                return True

    _constraints = [
        (_check_incoming, u'Debe registrar Empresa en el Ingreso a Bodega, y NO debe registrar Centro de Costo.', []),
        (_check_outgoing, u'Debe registrar Centro de Costo en el Egreso de Bodega, y NO debe registrar Empresa.', []),
        ]

gads_stock_picking()

class gad_stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def _calcular_valores(self, cr, uid, ids, fields, arg, context):
        res={}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                           'subtotal_move': obj.price_unit * obj.product_uom_qty,
                           }
        #print res
        return res
    
    _columns = {
                'subtotal_move' : fields.function(_calcular_valores, string=u'Subtotal', store=False, method=True, multi='stock_picking_values', digits_compute=dp.get_precision('Account')),
                }
    
    _defaults = {
                 'invoice_state': '2binvoiced',
                 }
    
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        #se modifica el método original para agregar tambien el precio del producto en el on_change
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id = product.uos_id and product.uos_id.id or False
        result = {
            'name': product.partner_ref,
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_uom_qty': 1.00,
            'product_uos_qty': self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'price_unit': product.standard_price or 0.0,
        }
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}
    
gad_stock_move()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
