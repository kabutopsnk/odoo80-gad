
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
from openerp import netsvc
from openerp.tools.translate import _
from time import strftime

import datetime
import base64
import StringIO

class invoice_budget_doc(osv.osv):
    _name = 'account.invoice.budget'
    _description = u'Relación entre la factura y el documento contable'
    
    _columns = {
                'invoice_id': fields.many2one('account.invoice', u'Factura', ondelete='cascade'),
                'move_id': fields.many2one('account.move', u'Asiento Contable', ondelete='cascade'),
                #'budget_doc_line': fields.many2one('crossovered.budget.doc.line', u'Linea Presupuesto', ondelete='cascade'),
                'budget_doc_line': fields.many2one('crossovered.budget.doc.line', u'Linea Presupuesto', required=True),
                'budget_line_id': fields.related('budget_doc_line', 'budget_line_id', type='many2one', relation='crossovered.budget.lines', store=True, string=u'Linea Planificación Presupuesto'),
                'amount': fields.float(u'Valor', required=True),
                'state': fields.related('invoice_id','state', type='selection', selection=[('draft','Draft'),
                                                                                           ('proforma','Pro-forma'),
                                                                                           ('proforma2','Pro-forma'),
                                                                                           ('open','Open'),
                                                                                           ('paid','Paid'),
                                                                                           ('cancel','Cancelled'),], string='Estado'),
                'state_move': fields.related('move_id', 'state', type='selection', selection=[('draft','Sin Contabilizar'), ('posted','Contabilizado'),], string=u'Estado', readonly=True)
                }
    
    _defaults = {
                 'amount': 0,
                 }
    
    _sql_constraints = [
                        ('unique_budget_invoice', 'unique(invoice_id,budget_line_id)', u'Solo puede registrar 1 vez la linea de presupuesto en la factura actual.')
                        ]
    
invoice_budget_doc()

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Supplier Invoice
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Supplier Refund
}

class ec_account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _calcular_clave(self, cr, uid, ids, fields, arg, context):
        res = {}
        #obj_invbudget = self.pool.get('account.invoice.budget')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                           'clave_acceso': '',
                           }
            if obj.type=='in_invoice':
                continue
            fecha_emision = obj.date_invoice
            fecha_emision = fecha_emision[8:10] + fecha_emision[5:7] + fecha_emision[0:4]
            tipo_comprobante = obj.auth_inv_id.type_id.code
            ruc = obj.company_id.partner_id.identifier
            ambiente = '1' # - 1 pruebas - 2 produccion
            serie = obj.auth_inv_id.serie_entidad + obj.auth_inv_id.serie_emision
            comprobante = obj.supplier_invoice_number and obj.supplier_invoice_number or obj.invoice_number[6:]
            
            ahora = datetime.datetime.now()
            segundos_actuales = ahora.hour*3600 + ahora.minute*60 + ahora.second
            codigo_num = str(obj.id).zfill(8)[:8]#str(segundos_actuales).zfill(8)
            
            tipo_emision = '1'
            
            res[obj.id]['clave_acceso'] = fecha_emision     #+ ' 8 ' 
            res[obj.id]['clave_acceso'] += tipo_comprobante #+ ' 2 '
            res[obj.id]['clave_acceso'] += ruc              #+ ' 13 '
            res[obj.id]['clave_acceso'] += ambiente         #+ ' 1 '
            res[obj.id]['clave_acceso'] += serie            #+ ' 6 '
            res[obj.id]['clave_acceso'] += comprobante      #+ ' 9 '
            res[obj.id]['clave_acceso'] += codigo_num       #+ ' 8 '
            res[obj.id]['clave_acceso'] += tipo_emision     #+ ' 1 '
            
            #print len(res[obj.id]['clave_acceso'])
            mult = 2
            suma = 0
            clave_invertida = res[obj.id]['clave_acceso'][::-1]
            print clave_invertida
            for caracter in clave_invertida:
                try:
                    numero = int(caracter)
                    
                except ValueError:
                    numero = 0
                numero = numero * mult
                suma += numero
                mult += 1
                if mult > 7:
                    mult = 2
            modulo = suma%11
            modulo = 11-modulo
            if modulo == 10:
                modulo = 1
            res[obj.id]['clave_acceso'] += str(modulo)    #+ ' 1 '
            
            
            
        return res
    
    _columns = {
                #'authorization_number': fields.char(u'Número de Autorización', required=False, readonly=True, size=64, states={'draft':[('readonly',False)]}),
                #'comprobante_id': fields.many2one('account.sri.comprobante', u'Tipo de Comprobante', required=False,  readonly=True, states={'draft':[('readonly',False)]}),
                #'sustento_id': fields.many2one('account.sri.sustento', u'Sustento del Comprobante', required=False,  readonly=True, states={'draft':[('readonly',False)]}),
                #'fecha_hasta': fields.date(u'Válido hasta', readonly=True, states={'draft':[('readonly',False)]}),
                'budget_doc_id': fields.many2one('crossovered.budget.doc', u'Documento Presupuestario', readonly=True, states={'draft':[('readonly',False)]}),
                'invoice_budget_lines': fields.one2many('account.invoice.budget', 'invoice_id', u'Detalle Presupuestario', readonly=True, states={'draft':[('readonly',False)]}),
                
                'main_invoice_id': fields.many2one('account.invoice', u'Documento Original', readonly=True),
                'clave_acceso': fields.function(_calcular_clave, string=u'Clave de acceso', multi="einvoice", store=False, method=True, type='char'), #49 caracteres
                }
    
    def action_budget_account(self, cr, uid, ids, context={}):
        obj_budget = self.pool.get('account.invoice.budget')
        for obj in self.browse(cr, uid, ids):
            for budget in obj.invoice_budget_lines:
                obj_budget.write(cr, uid, budget.id, {'move_id': obj.move_id.id})
    
    
    def crear_archivo_csv(self, cr, uid, ids, context={}):
        for this in self.browse(cr, uid, ids, context):
            #if this.type != 'out_invoice':
            #    continue
            name = this.company_id.partner_id.identifier + '-f-' + this.auth_inv_id.serie_entidad + '-' + this.auth_inv_id.serie_emision + '-' + this.invoice_number[6:] + '.csv'
            f = open ('facturas/'+ name,'w')
            f.write('''AMBIENTE;TIPOEMISION;RAZONSOCIAL;NOMBRECOMERCIAL;RUC;CLAVEACCESO;CODDOC;ESTAB;PTOEMI;SECUENCIAL;DIRECCIONMATRIZ;FECHADEEMISION;DIRESTABLECIMIENTO;CONTRIBUYENTEESPECIAL;OBLIGADOCONTABILIDAD;TIPOIDENTFICACONCOMPRADOR;GUIAREMISION;RAZONSOCIALCOMPRADOR;IDENTIFICACIONCOMPRADOR;VALORTOTALSINIMPUESTOS;VALORTOTALDESCUENTOS;PROPINA;IMPORTETOTAL;MONEDA;CAMPOADICIONAL;TOTALCONIMPUESTOS;PAGOS\n''')
            datos = ''
            datos += '1' #ambiente - 1 pruebas  - 2 produccion
            datos += ';1' #tipo de emision
            datos += ';' + this.company_id.partner_id.name
            datos += ';' + this.company_id.partner_id.name
            datos += ';' + this.company_id.partner_id.identifier
            datos += ';' + this.clave_acceso
            datos += ';' + this.auth_inv_id.type_id.code
            datos += ';' + this.auth_inv_id.serie_entidad
            datos += ';' + this.auth_inv_id.serie_emision
            datos += ';' + this.invoice_number[6:]
            datos += ';' + str(this.company_id.partner_id.street)
            fecha_factura = datetime.datetime.strptime(this.date_invoice, '%Y-%m-%d')
            datos += ';' + fecha_factura.strftime("%d/%m/%Y")
            datos += ';' + str(this.company_id.partner_id.street)
            datos += ';' + str(this.company_id.codigo_ce) #str(this.fiscal_position.sequence).zfill(3) #campo que pide como contribuyente especial
            datos += ';SI'
            
            tipo_identificador = '04'
            if this.partner_id.type_identifier=='ruc':
                tipo_identificador = '04'
            if this.partner_id.type_identifier=='cedula':
                tipo_identificador = '05'
            if this.partner_id.type_identifier=='pasaporte':
                tipo_identificador = '06'
            datos += ';' + tipo_identificador
            datos += ';' #guia de remision
            datos += ';' + this.partner_id.name
            datos += ';' + this.partner_id.identifier
            datos += ';' + str(this.amount_untaxed)
            datos += ';0.00' #descuentos
            datos += ';0.00' #propina
            datos += ';' + str(this.amount_pay)
            datos += ';DOLAR' #moneda
            datos += ';' + '{"CAMPOADICIONAL":[{"NOMBRE":"DIRECCION","VALOR":"' + str(this.partner_id.street) + '"},{"NOMBRE":"TELEFONO","VALOR":"' + str(this.partner_id.phone) + '"},{"NOMBRE":"EMAIL","VALOR":"' + str(this.partner_id.email) + '"}]}'
            if this.tax_line:
                datos += ';' + '{"TOTALCONIMPUESTOS":['
                for impuesto in this.tax_line:
                    cod_impuesto = impuesto.tax_code_id.code
                    datos += '{"CODIGOIMPUESTO":"' + impuesto.tax_code_id.code + '","VALOR":"' + str(impuesto.amount) + '","DESCUENTOADICIONAL":"0.00","CODIGOPORCENTAJE":"' + str(impuesto.sequence) + '","BASEIMPONIBLE":"' + str(impuesto.base) + '","TARIFA":"' + "{0:.2f}".format(impuesto.percent) + '"},'
                    #debemos cambiar le tax.sequence, para darle al funcionalidad del manual del SRI, por el codigo de impuesto
                datos += ']}'
            datos += ';{"PAGOS":[{"TOTAL":"' + str(this.amount_pay) + '","FORMAPAGO":"20","PLAZO":"30","UNIDADTIEMPO":"DIAS"}]}'
            f.write(datos)
            f.write('\n=EOC')
            f.write('\nCODIGO;DESCRIPCION;CANTIDAD;PRECIOUNITARIO;DESCUENTO;PRECIOTOALSINIMPUESTO;IMPUESTOS\n')
            if this.invoice_line:
                for detail in this.invoice_line:
                    detalle = ''
                    detalle += detail.product_id.default_code or ''
                    detalle += ';' + detail.product_id.name
                    detalle += ';' + str(detail.quantity)
                    detalle += ';' + str(detail.price_unit)
                    detalle += ';0.00'
                    detalle += ';' + str(detail.price_subtotal)
                    detalle += ';{"IMPUESTOS":['
                    if detail.invoice_line_tax_id:
                        for dimpuesto in detail.invoice_line_tax_id:
                            #import pdb
                            #pdb.set_trace()
                            detalle += '{"CODIGOIMPUESTO":"' + dimpuesto.tax_code_id.code + '","VALOR":"' + "{0:.2f}".format(detail.price_subtotal*dimpuesto.amount) + '","CODIGOPORCENTAJE":"' + str(dimpuesto.sequence) + '","BASEIMPONIBLE":"' + str(detail.price_subtotal) + '","TARIFA":"' + "{0:.2f}".format(dimpuesto.porcentaje) + '"},'
                            #pass
                    detalle += ']}'
                    f.write(detalle)
            f.write('\n=EOD')
            f.close()
    
    
    
    def create_retention(self, cr, uid, ids, context={}):
        obj_retention = self.pool.get('account.retention')
        obj_invtax = self.pool.get('account.invoice.tax')
        for this in self.browse(cr, uid, ids, context=context):
            retention_id = obj_retention.create(cr, uid, {
                                                          'name': 'BORRADOR',
                                                          'invoice_id': this.id,
                                                          'type': this.type,
                                                          'date': strftime("%Y-%m-%d"),
                                                          }, context=context)
            for tax in this.tax_line:
                obj_invtax.write(cr, uid, tax.id, {'retention_id':retention_id}, context=context)
                
                
    def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice to refund
            :param string date: refund creation date from the wizard
            :param integer period_id: force account.period from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id', 'company_id',
                'account_id', 'currency_id', 'payment_term', 'user_id', 'fiscal_position']:
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line'] = self._refund_cleanup_lines(invoice.invoice_line)

        tax_lines = filter(lambda l: l.manual, invoice.tax_line)
        values['tax_line'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase_refund')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale_refund')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        
        #adicional
        values['main_invoice_id'] = invoice.id

        if period_id:
            values['period_id'] = period_id
        if description:
            values['name'] = description
        return values
    
    def _check_invoice_budget(self, cr, uid, ids, context={}):
        """partidas_factura = {}
        partidas_budget = {}"""
        suma_partidas = 0
        for this in self.browse(cr, uid, ids, context=context):
            if this.state in ['open','paid'] and this.type == 'in_invoice' and this.budget_doc_id:
            #if this.state in ['open','paid'] and this.type == 'in_invoice':
                """for invoice_line in this.invoice_line:
                    if not partidas_factura
            MONEDA;CAMPOADICIONAL;TOTALCONIMPUESTOS;PAGOS''').has_key(invoice_line.account_id.budget_debit_id.id):
                        partidas_factura[invoice_line.account_id.budget_debit_id.id] = invoice_line.price_subtotal
                    else:
                        partidas_factura[invoice_line.account_id.budget_debit_id.id] += invoice_line.price_subtotal"""
                for movebudget in this.invoice_budget_lines:
                    suma_partidas += movebudget.amount
                    #if not partidas_budget.has_key(movebudget.budget_doc_line.general_budget_id.id):
                    #    partidas_budget[movebudget.budget_doc_line.general_budget_id.id] = movebudget.amount
                    #else:
                    #    partidas_budget[movebudget.budget_doc_line.general_budget_id.id] += movebudget.amount
                """if (not partidas_budget) or (not partidas_factura):
                    return False
                for partida in partidas_budget.keys():
                    if not partidas_factura.has_key(partida):
                        return False
                    else:
                        if ("%.2f" % partidas_factura[partida]) != ("%.2f" % partidas_budget[partida]):
                            return False"""
                #print this.amount_total
                #print suma_partidas
                if suma_partidas != this.amount_total:
                    print suma_partidas
                    print this.amount_total
                    return True #False
                else:
                    return True
            else:
                return True
        return True
    
    _constraints = [
                    (_check_invoice_budget, '\nEl valor de la cuenta contable debe empatar con el valor de la partida', ['invoice_bugdet_lines','invoice_line','state']),
                    ]
    
ec_account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
