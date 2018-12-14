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
import time
import unicodedata
import exceptions



#***ACTIVOS FIJOS***
class account_asset(osv.osv):
    _inherit = 'account.asset.asset'

    def name_get(self, cr, uid, ids, context=None):        
        # el name_ger devuelve el Código del activo, (el name no es único)
        if not ids:
            return []
        res = []
        for record in self.read(cr, uid, ids, ['id','code','name'], context=context):
            try:
                aux = str(record['code']) +'/'+ str(record['name'])
                res.append((record['id'], aux ))
            except:
                pass
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        # devuelve el nombre y código del activo
        ids = []
        ids_descrip = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_descrip))
        if name:
            code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)           
            ids = list(set(ids + code))
        return self.name_get(cr, uid, ids, context=context)

    def _compute_iva(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            subtotal = round((obj.purchase_value*100)/(100+obj.porcentaje_iva),2)
            iva = obj.purchase_value - subtotal
            res[obj.id] = iva
        return res

    def _compute_subtotal(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            subtotal = round((obj.purchase_value*100)/(100+obj.porcentaje_iva),2)
            res[obj.id] = subtotal
        return res

    def onchange_iva_check(self, cr, uid, ids, iva_check, context=None):   
        #on_change: Pone en 0% cuando no tiene IVA
        res = {'value': {}}
        if iva_check==False:
            res['value'] = {'porcentaje_iva': 0.00}
        return res

    def onchange_tipo_ingreso(self, cr, uid, ids, tipo_ingreso, context=None):   
        #on_change: Pone el valor del invoice_state
        res = {'value': {}}
        if tipo_ingreso=='inicial':
            res['value'] = {'invoice_state': 'none'}
        else:
            res['value'] = {'invoice_state': '2binvoiced'}
        return res

    def onchange_categoria(self, cr, uid, ids, category_id, context=None):   
        #on_change: Pone el # de depreciaciones de la categoría
        res = {}
        if category_id:
            obj_category=self.pool.get('account.asset.category')
            category_ids=[]
            category_ids=obj_category.search(cr, uid, [('id','=', category_id)])
            for cat in obj_category.browse(cr, uid, category_ids):
                num=cat.method_number
            res['value'] = {'method_number': num}
        return {'value': res}

    def onchange_clasificador(self, cr, uid, ids, context=None):   
        #on_change: vacía la categoría
        res = {'value': {}}
        res['value'] = {'category_id': False,
                        }      
        return res

    #def onchange_purchase_value(self, cr, uid, ids, purchase_value, method_number, context=None):
    #    val = {}
    #    if method_number==0:
    #        return val
    #    salvage_value = purchase_value / 10
    #    val['salvage_value'] = salvage_value
        #val['value_residual'] = purchase_value - salvage_value
    #    return {'value': val}    

    _columns = {
        'clasificador': fields.selection([('bld', u'Bienes de Larga Duración'),('bsc', u'Bienes Sujetos a Control')], 'Clasificador', required=True),
        'category_id': fields.many2one('account.asset.category', u'Categoría', required=True),
        'employee_id': fields.many2one('hr.employee', u'Responsable / Custodio'),
        'department_id': fields.many2one('hr.department', u'Dpto. / Unidad Operativa'),
        'estado': fields.selection([('bueno', 'Bueno'),('regular', 'Regular'),('malo', 'Malo')], 'Estado del Bien', required=True),
        'tipo_ingreso': fields.selection([('compra','Compra'),('tomafisica',u'Toma Física'),('donacion',u'Donación'),('comodato','Comodato'),('inicial','Carga Inicial')], 'Tipo de Ingreso', required=True),
        'doc_ref': fields.char(u'Doc. Referencia', size=32),
        'numero_ingreso': fields.integer(u'# Ingreso', required=True),
        'code': fields.char(u'Código', size=32, required=True),
        'baja_date': fields.date(u'Fecha de Baja'),
        'tiene_iva': fields.boolean(u'Tiene IVA?'),
        'porcentaje_iva': fields.float(u'% IVA', required=True),
        'valor_iva': fields.function(_compute_iva, string=u'Valor IVA', method=True, store=False, type='float'),
        'valor_subtotal': fields.function(_compute_subtotal, string=u'Valor Subtotal', method=True, store=False, type='float'),
        'state': fields.selection([('draft','Borrador'),('open','Operativo'),('close','Dado de Baja')], 'Status', required=True, copy=False,
                                  help="When an asset is created, the status is 'Borrador'.\n" \
                                       "If the asset is confirmed, the status goes in 'Operativo' and the depreciation lines can be posted in the accounting.\n" \
                                       "You can manually close an asset when the depreciation is over. If the last line of depreciation is posted, the asset automatically goes in that status."),
        'propiedades_ids': fields.one2many('account.asset.propiedades','asset_id','Propiedades'),
        'propiedades_adicionales': fields.text(u'Propiedades Adicionales'),
        'componentes_ids': fields.one2many('account.asset.componentes','asset_id','Componentes'),
        'historial_ids': fields.one2many('account.asset.historial','asset_id','Historial'),
		'motivo_baja': fields.selection([('Fin Vida',u'Fin Vida Útil'),('Deterioro','Deterioro'),('Siniestro','Siniestro'),('Robo','Robo'),(u'Pérdida',u'Pérdida'),('Otro','Otro')], u'Motivo', required=False),
		'detalle_baja': fields.char(u'Detalle de la Baja', size=64, required=False),
        'invoice_state': fields.selection([("invoiced", "Facturado"), ("2binvoiced", "Para facturar"), ("none", "No Aplicable")], "Control factura", required=True),
        'baja_contabilizada': fields.boolean(u'Baja Contabilizada', required=True),
        'tipo_gasto': fields.selection([("corriente", "Corriente"), ("invobras", u"Inversión Obras"), ("invprogramas", "Inversión Programas")], "Tipo de Gasto",),
        }

    def validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.tiene_iva==True and obj.porcentaje_iva==0.00:
                raise osv.except_osv(_('Error!'), _('El IVA no puede ser 0.00%...'))
            if obj.tiene_iva==False and obj.porcentaje_iva!=0.00:
                raise osv.except_osv(_('Error!'), _('El IVA debe ser 0.00%...'))
            num=obj.numero_ingreso
            #Historial
            vals = {
                    'asset_id': obj.id,
                    'user_id': uid,
                    'name': 'Cambio de Estado',
                    'department_id': obj.department_id.id,
                    'employee_id':obj.employee_id.id,
                    'estado': obj.estado,
                    'state': 'open',
                    'descripcion': 'Tipo: ' + obj.tipo_ingreso + ' / Fecha: ' + str(obj.purchase_date) + ' / Valor: ' + str(obj.purchase_value) + u' / Categoría: ' + obj.category_id.name
                    }
            historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)
        if num==0:
            cr.execute("SELECT COALESCE(max(numero_ingreso),0) + 1 FROM account_asset_asset")
            tabla=map(lambda x: x[0], cr.fetchall())
            num=tabla[0]

        self.compute_depreciation_board(cr,uid,ids)

        return self.write(cr, uid, ids, {
            'state':'open',
            'numero_ingreso':int(num),
        }, context)

    def set_to_draft(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.invoice_state=='invoiced':
                raise osv.except_osv(_('Error!'), _('Este Activo ya fue Contabilizado, no puede pasar a BORRADOR...'))
            #Historial
            vals = {
                    'asset_id': obj.id,
                    'user_id': uid,
                    'name': 'Cambio de Estado',
                    'state': 'draft',
                    }
            historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)


    def unlink(self, cr, uid, ids, context=None):
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.account_move_line_ids: 
                raise osv.except_osv(_('Error!'), _('You cannot delete an asset that contains posted depreciation lines.'))
            if asset.state!='draft':
                raise osv.except_osv(_('Error!'), _('No puede Eliminar el Activo Fijo en este Estado...'))
        return super(account_asset, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        res=[]
        #GENERA CODIGO
        obj_category=self.pool.get('account.asset.category')
        for categ in obj_category.browse(cr,uid,[int(vals["category_id"])]):
            #cod_categ=categ.code.zfill(4)
            cr.execute("SELECT right('000000'||(COALESCE(max(right(code,6)),'0')::integer + 1)::text,6) FROM account_asset_asset WHERE category_id = " + str(vals["category_id"]) )
            tabla=map(lambda x: x[0], cr.fetchall())
            seq=tabla[0]
            vals['method_number']=categ.method_number
        code = categ.code + '-' + str(seq)
        vals["code"]=code
        vals["salvage_value"]=0
        if vals['method_number']>0:
            vals["salvage_value"]=vals["purchase_value"]/10.00
        #CREA ACTIVO
        res=super(account_asset, self).create(cr, uid, vals, context=context)
        #PROPIEDADES
        obj_category_propiedades=self.pool.get('account.asset.category.propiedades')
        obj_asset_propiedades=self.pool.get('account.asset.propiedades')
        propiedades_ids=[]
        propiedades_ids=obj_category_propiedades.search(cr, uid, [('category_id','=', int(vals["category_id"]))])
        if propiedades_ids:
            for prop in obj_category_propiedades.browse(cr,uid,propiedades_ids):
                obj_asset_propiedades.create(cr, uid, {'asset_id': res, 'category_propiedades_id':prop.id, 'obligatorio':prop.obligatorio}, context=context)
        #if vals.has_key("from_factura"):
        #    if vals['from_factura']==False:
        #        move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'ingreso','cause':'Registrado en sistema'}, context=None)
        #        self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': res,'move_id':move_id}, context=None)                         
        #else:
        #    move_id=self.pool.get('gt.account.asset.moves').create(cr, uid, {'type':'ingreso','cause':'Registrado en sistema'}, context=None)
        #    self.pool.get('gt.account.asset.moves.relation').create(cr, uid, {'asset_id': res,'move_id':move_id}, context=None)                
        return res

    def write(self, cr, uid, ids, vals, context=None):
        #    """
        #    Redefinición de método write
        #    """
        for asset in self.browse(cr,uid,ids):
            if asset.method_number>0:
                if vals.has_key('purchase_value'):
                    vals['salvage_value'] = vals['purchase_value']/10.00
        return super(account_asset, self).write(cr, uid, ids, vals, context)

    def action_print_baja(self, cr, uid, ids, context=None):
        """
        :action to print Baja
        """
        if context is None:
            context = {}
        report_name = 'account_asset_baja'
        baja = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [baja.id], 'model': 'account.asset.asset'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'account.asset.asset',
            'datas': datas,
            'nodestroy': True,                        
            }
    
    _sql_constraints = [('unique_code','unique(code)',u'Código ya Existente...')]

    _defaults = {
        'code': '/',
        'estado': 'bueno',
        'clasificador':'bld',
        'numero_ingreso':0,
        'tiene_iva':'t',
        'porcentaje_iva':0.00,
        'prorata':True,
        'invoice_state':'2binvoiced',
        'baja_contabilizada':False,
    }

    _order = 'code'

account_asset()



#***PROPIEDADES DE ACTIVOS***
class account_asset_propiedades(osv.osv):
    _name = 'account.asset.propiedades'
    _description = 'Propiedades de Activos Fijos'   
     
    _columns = {      
        'asset_id' : fields.many2one('account.asset.asset', 'Activo Fijo', readonly=True, required=True, ondelete='cascade'),
        'category_propiedades_id' : fields.many2one('account.asset.category.propiedades', u'Propiedad', required=True, readonly=True),
        'obligatorio' : fields.boolean(u'Obligatorio', readonly=True),
        'valor' : fields.char(u'Valor', size=128),
        }
        
    def unlink(self, cr, uid, ids, context=None):
        # redefine unlink para que no pueda eliminar propiedades de tipos
        for formulario in self.browse(cr, uid, ids, context):
                raise osv.except_osv('Error', 'No puede eliminar un registro de propiedad de activos')
        return False 
         
account_asset_propiedades() 



#***COMPONENTES***
class account_asset_componente(osv.osv):
    '''
    Componentes de activos
    '''
    _description = 'Componentes de Activos Fijos' 
    _name = 'account.asset.componentes'  
    _columns = {
        'asset_id': fields.many2one('account.asset.asset', 'Activo Fijo', readonly=True, required=True, ondelete='cascade'),
        'name': fields.char(u'Componente', size=32, required=True),       
        'cantidad': fields.integer(u'Cantidad', required=True),
        'descripcion': fields.char(u'Descripción', size=128),  
        }
    _defaults = {
        'cantidad': 1,
    }
             
account_asset_componente()



#***HISTORIAL***
class account_asset_historial(osv.osv):
    '''
    Historial de cambios en Activos Fijos
    '''
    _description = 'Historial de Activos Fijos' 
    _name = 'account.asset.historial'  
    _columns = {
        'asset_id': fields.many2one('account.asset.asset', 'Activo Fijo', readonly=True, required=True, ondelete='cascade'),
        'fecha_hora': fields.datetime(u'Fecha/Hora', required=True, readonly=True),
        'user_id' : fields.many2one('res.users', u'Usuario', required=True, readonly=True),
        'name': fields.char(u'Descripción', size=32, required=True),      
        'department_id': fields.many2one('hr.department', u'Dpto. / Unidad Operativa', readonly=True),
        'employee_id': fields.many2one('hr.employee', u'Responsable / Custodio', readonly=True),
        'estado': fields.selection([('bueno', 'Bueno'),('regular', 'Regular'),('malo', 'Malo')], 'Estado del Bien'),
        'state': fields.selection([('draft','Borrador'),('open','Operativo'),('close','Dado de Baja')], 'Estado'), 
        'descripcion': fields.char(u'Detalle', size=128), 
        }

    _defaults = {
        'fecha_hora': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    _order = 'fecha_hora desc'
             
account_asset_historial()



#***TRANSFERENCIAS***
class account_asset_transfer(osv.osv):
    '''
    Transferencias de Activos Fijos
    '''
    _description = 'Transferencias de Activos Fijos' 
    _name = 'account.asset.transfer'  
    _columns = {
        'employee_origen_id': fields.many2one('hr.employee', 'Responsable/Custodio Origen', required=True),
        'employee_destino_id': fields.many2one('hr.employee', 'Responsable/Custodio Destino', required=True),
        'department_destino_id': fields.many2one('hr.department', u'Dpto./Unidad Operativa Destino', required=True),
        'employee_autoriza_id': fields.many2one('hr.employee', 'Autorizado por', required=True),
        'code': fields.char(u'Código', size=6, required=True, readonly=True),      
        'name': fields.char(u'Descripción', size=64, required=True),      
        'observaciones': fields.text(u'Observaciones', required=False),      
        'state': fields.selection([('draft','Borrador'),('done','Realizado')], 'Estado', required=True), 
        'transfer_activos_ids': fields.many2many('account.asset.asset', 'account_asset_transfer_rel', 'transfer_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
        }

    def create(self, cr, uid, vals, context=None):
        res=[]
        #GENERA CODIGO
        cr.execute("SELECT right('000000'||(COALESCE(max(right(code,6)),'0')::integer + 1)::text,6) FROM account_asset_transfer")
        tabla=map(lambda x: x[0], cr.fetchall())
        seq=tabla[0]
        code = str(seq)
        vals["code"]=code
        #CREA TRANSFERENCIA
        res=super(account_asset_transfer, self).create(cr, uid, vals, context=context)

        return res

    _defaults = {
        'code': '/',
        'state': 'draft',
    }

    def onchange_origen(self, cr, uid, ids, context=None):   
        #on_change: vacía detalle de activos
        res = {'value': {}}
        res['value'] = {'transfer_activos_ids': {},
                        }      
        return res

    def done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for transfer in self.browse(cr, uid, ids, context=context):
            for obj in transfer.transfer_activos_ids:
                self.pool.get('account.asset.asset').write(cr,uid,[obj.id],{'employee_id':transfer.employee_destino_id.id,'department_id':transfer.department_destino_id.id})
                #Historial
                vals = {
                    'asset_id': obj.id,
                    'user_id': uid,
                    'name': 'Transferencia',
                    'department_id': transfer.department_destino_id.id,
                    'employee_id':transfer.employee_destino_id.id,
                    'descripcion': '#' + transfer.code + ' / ' + transfer.name
                    }
                historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)

        return self.write(cr, uid, ids, {
            'state':'done',
        }, context)

    _order = 'code desc'
             
account_asset_transfer()



#***BAJAS***
class account_asset_baja(osv.osv):
    '''
    Bajas de Activos Fijos
    '''
    _description = 'Bajas de Activos Fijos' 
    _name = 'account.asset.bajas'  
    _columns = {
        'employee_autoriza_id': fields.many2one('hr.employee', 'Autorizado por', required=True),
        'code': fields.char(u'Código', size=6, required=True, readonly=True),      
        'name': fields.char(u'Descripción', size=64, required=True),      
        'fecha_baja': fields.date(u'Fecha Baja', required=True),      
        'state': fields.selection([('draft','Borrador'),('done','Realizado')], 'Estado', required=True), 
        'observaciones': fields.text(u'Observaciones', required=False),
        'contabilizar_baja': fields.boolean(u'Contabilizar Baja?'),
        'baja_activos_ids': fields.many2many('account.asset.asset', 'account_asset_baja_rel', 'baja_id', 'asset_id', 'Detalle de Activos Fijos', required=True),
        }

    def create(self, cr, uid, vals, context=None):
        res=[]
        #GENERA CODIGO
        cr.execute("SELECT right('000000'||(COALESCE(max(right(code,6)),'0')::integer + 1)::text,6) FROM account_asset_bajas")
        tabla=map(lambda x: x[0], cr.fetchall())
        seq=tabla[0]
        code = str(seq)
        vals["code"]=code
        #CREA TRANSFERENCIA
        res=super(account_asset_baja, self).create(cr, uid, vals, context=context)

        return res

    _defaults = {
        'code': '/',
        'state': 'draft',
        'contabilizar_baja': True,
    }

    def done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for baja in self.browse(cr, uid, ids, context=context):
            #Contabilizar o no la Baja
            baja_state=False
            if baja.contabilizar_baja==False:
                baja_state=True
            for obj in baja.baja_activos_ids:
                if baja.fecha_baja<obj.purchase_date:
                    raise osv.except_osv(_('Error!'), _('Fecha de Baja incorrecta...'))
                self.pool.get('account.asset.asset').write(cr,uid,[obj.id],{'state':'close', 'invoice_state':'invoiced', 'baja_date':baja.fecha_baja, 'baja_contabilizada':baja_state})
                #Historial
                vals = {
                    'asset_id': obj.id,
                    'user_id': uid,
                    'name': 'Baja de Activo Fijo',
                    'state': 'close',
                    'descripcion': '#' + baja.code + ' / ' + baja.name
                    }
                historial_id = self.pool.get('account.asset.historial').create(cr, uid, vals, context=context)

        return self.write(cr, uid, ids, {
            'state':'done',
        }, context)

    _order = 'code desc'
             
account_asset_baja()



#***CATEGORIAS DE ACTIVOS FIJOS***
class account_asset_category(osv.osv):

    _inherit = 'account.asset.category'

    _columns = {
        'name': fields.char(u'Descripción', size=64, required=True, select=1),
        'code': fields.char(u'Código', size=10),                
        'clasificador': fields.selection([('bld', u'Bienes de Larga Duración'),('bsc', u'Bienes Sujetos a Control')], 'Clasificador', required=True),
        'account_asset_id': fields.many2one('account.account', u'Cuenta de Activo', required=True, domain=[('type','=','other')]),
        'account_asset_io_id': fields.many2one('account.account', u'Cuenta Inversión Obras', required=True, domain=[('type','=','other')]),
        'account_asset_ip_id': fields.many2one('account.account', u'Cuenta Inversión Programas', required=True, domain=[('type','=','other')]),
        'account_depreciation_id': fields.many2one('account.account', u'Cuenta de Depreciación', required=True, domain=[('type','=','other')]),
        'account_expense_depreciation_id': fields.many2one('account.account', u'Cuenta Gastos Amortización', required=True, domain=[('type','=','other')]),
        'account_ctaxpagar_id': fields.many2one('account.account', u'Cuenta x Pagar', required=True, domain=[('type','=','other')]),
        'account_ctaxpagar_inv_id': fields.many2one('account.account', u'Cuenta x Pagar Inversión', required=True, domain=[('type','=','other')]),
        'account_donaciones_acc_id': fields.many2one('account.account', 'Cuenta Accreedora Donaciones', domain=[('type','=','other')]),
        'account_patrimonio_id': fields.many2one('account.account', 'Cuenta Baja Patrimonio', domain=[('type','=','other')]),
        'account_comodato_deb_id': fields.many2one('account.account', 'Cuenta Deudora Comodato', domain=[('type','=','other')]),
        'account_comodato_acc_id': fields.many2one('account.account', 'Cuenta Acreedora Comodato', domain=[('type','=','other')]),
        'account_complemento_deb_id': fields.many2one('account.account', 'Cuenta Deudora Complemento', domain=[('type','=','other')]),
        'account_complemento_acc_id': fields.many2one('account.account', 'Cuenta Acreedora Complemento', domain=[('type','=','other')]),
        'propiedades_ids': fields.one2many('account.asset.category.propiedades','category_id','Propiedades'),
        }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = (record.code or '') + ' - ' + record.name
            res.append((record.id, name))
        return res

    def generar_producto(self, cr, uid, ids, context=None):
        obj_product_template=self.pool.get('product.template')
        obj_product_product=self.pool.get('product.product')
        obj_product_category=self.pool.get('product.category')
        for cat in self.browse(cr, uid, ids):
            ids_product_product = obj_product_product.search(cr, uid, [('default_code','=','ACTIVOS-'+cat.code)])
            if ids_product_product:
                raise osv.except_osv(_('Error!'), _('Producto ya Existente...'))
            ids_product_category=obj_product_category.search(cr,uid,[('name','=','ACTIVOS')])
            if not ids_product_category:
                raise osv.except_osv(_('Error!'), _(u'No existe la categoría ACTIVOS en módulo de Inventarios...'))
            template=obj_product_template.create(cr, uid, {'warranty':0, 'list_price':0.00, 'mes_type':'fixed', 'uom_id':1, 'uos_coeff':1.00, 'sale_ok':False, 'categ_id':ids_product_category[0], 'company_id':1, 'uom_po_id':1, 'active':True, 'rental':False, 'name':'ACTIVOS/'+cat.name, 'type':'product','sale_delay':7,'purchase_ok':True})

            ids_product_product2 = obj_product_product.search(cr, uid, [('product_tmpl_id','=',template)])

        return obj_product_product.write(cr, uid, ids_product_product2, {'default_code':'ACTIVOS-'+cat.code})
        
    _sql_constraints = [('code_category_unique', 'unique(code)', u'El código debe ser Único...'),
                        ('name_category_unique', 'unique(name)', u'La descripción debe ser Única...')
                        ]

    _order = 'clasificador,code'

    _defaults = {
        'clasificador':'bld',
        'prorata':True,
    }

account_asset_category()



#***PROPIEDADES x CATEGORIA***
class account_asset_category_propiedades(osv.osv):
    '''
    Propiedades por Categoría
    '''    

    _description = u'Propiedades por Categoría de Activo Fijo' 
    _name = 'account.asset.category.propiedades'  
    _columns = {
        'name': fields.char(u'Descripción', size=32, required=True),
        'category_id': fields.many2one('account.asset.category', u'Categoría', required=True),
        'obligatorio': fields.boolean(u'Obligatorio?'),
        'prioridad': fields.integer(u'Prioridad', required=True),
        }
    
    _sql_constraints = [('unique_asset_category_property', 'unique(category_id,name)', u'La propiedad debe ser Única...')]

    _defaults = {
        'prioridad':0,
        'obligatorio':False,
    }

    _order = 'category_id,prioridad,name'
    
account_asset_category_propiedades()




#***EMPLEADO - BIENES A CARGO***
class account_asset_hr_employee_(osv.osv):
    '''
    Agregar  Relacion de usuario y sus activos a cargo
    '''
    _inherit = 'hr.employee'
    _columns = {
        'account_asset_ids': fields.one2many('account.asset.asset','employee_id','Bienes a Cargo',readonly=True),
        }

account_asset_hr_employee_()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
