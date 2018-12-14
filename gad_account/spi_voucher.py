
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

from time import strftime
import datetime

import StringIO
import base64
import unicodedata
import hashlib
import zipfile
try:
    import zlib
    COMPRESSION = zipfile.ZIP_DEFLATED
except:
    COMPRESSION = zipfile.ZIP_STORED

"""class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    _columns = {
                'spi' : fields.boolean(u'SPI Generado')
                }
    
    _defaults = {
                 'spi': False,
                 }
    
account_voucher()"""

class account_spi_concept(osv.osv):
    _name = 'account.spi.concept'
    _description = 'Concepto de pago de SPI'
    
    _columns = {
                'code': fields.char(u'Código', size=10, required=True),
                'name': fields.char(u'Concepto', size=200, required=True),
                }
    
    _order = 'code asc'
    
    _sql_constraints = [
                    ('unique_code', 'unique(code)', u'No puede registrar el mismo código más de 1 vez'),
                    ('unique_name', 'unique(name)', u'No puede registrar el mismo concepto más de 1 vez')
                    ]
    
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
            name = '[' + record.code + '] ' + record.name
            res.append((record.id, name))
        return res
    
account_spi_concept()

class account_spi_voucher(osv.osv):
    _name= 'account.spi.voucher'
    
    _columns = {
                'move_id': fields.many2one('account.move.line', u'Pago'),# domain=[('account_id.type', '=', 'payable'),('credit','>','0'),('partner_id','is not', None)]),
                'concept_id': fields.many2one('account.spi.concept', u'Concepto'),
                #'tipo_beneficiario': fields.selection([('1','Empleado'),('2','Proveedor')], u'Tipo de beneficiario'),
                #'voucher_id':fields.many2one('account.voucher', u'Pago', domain=[('spi','=',False)]),
                'state': fields.selection([('draft',u'Borrador'),('done',u'Realizado'),('reject',u'Rechazado')], u'Estado', readonly=True),
                'head_id': fields.many2one(u'account.spi', u'Cabecera', required=True, ondelete="cascade"),
                #'value': fields.related('voucher_id', 'amount', string=u'Monto', type='float', readonly=True, store=False)
                'value': fields.related('move_id', 'credit', string=u'Monto', type='float', readonly=True, store=False),
                'partner_id': fields.related('move_id', 'partner_id', string=u'Proveedor', type='many2one', relation='res.partner', readonly=True, store=False),
                }
    
    _defaults = {
                 'state': 'draft',
                 'type_person': '2',
                 }
    
    """def _check_voucher(self, cr, uid, ids):
        for this in self.browse(cr, uid, ids):
            pagos = self.search(cr, uid, [('voucher_id','=',this.voucher_id.id),('state','in',('draft','done'))])
            if len(pagos)>1:
                return False
            else:
                return True

    _constraints = [
        (_check_voucher, u'El registro es inválido, NO puede realizar el mismo pago 2 veces', ['state','voucher_id']),
        ]"""

account_spi_voucher()

class account_spi_resume(osv.osv):
    _name = 'account.spi.resume'
    _columns = dict(
        number = fields.char(u'Identificador',size=20, required=True),
        name = fields.char(u'Banco',size=20, required=True),
        qty = fields.integer(u'# Pagos', required=True),
        amount = fields.float(u'$ Monto', required=True),
        head_id = fields.many2one(u'account.spi', u'Cabecera', required=True, ondelete="cascade"),
        )
account_spi_resume

class account_spi(osv.osv):

    _name = 'account.spi'
    
    _columns = {
                'date': fields.datetime(u'Fecha'),
                'line_ids': fields.one2many('account.spi.voucher', 'head_id', u'Detalle de Pagos'),
                'state':fields.selection([('draft',u'Borrador'),('send',u'Generado'),('closed',u'Cerrado')], u'Estado', readonly=True),
                'file_name': fields.char(u'Nombre SPI', size=124, readonly=True),
                'file_namelb': fields.char(u'Nombre SPI LB', size=124, readonly=True),
                'file_spi': fields.binary(u'Archivo SPI', readonly=True),
                'file_lb': fields.binary(u'Archivo SPI LB', readonly=True),
                #'file_generate':fields.boolean(u'Generado SPI', readonly=True),
                'file_dig': fields.char(u'MD5', size=256, readonly=True),
                'file_amount': fields.float(u'Total SPI', readonly=True),
                'file_resume': fields.one2many('account.spi.resume', 'head_id', u'Detalle SPI'),
                'file_reference': fields.char(u'Referencia SPI', size=5, required=True),
                #'file_journal':fields.many2one('account.journal', u'Diario', domain=[('type','=','bank')]),
                'file_account':fields.many2one('res.partner.bank', u'Cuenta Bancaria', domain=[('partner_id','=',1)]),
                #'journal_id': fields.many2one('account.journal', u'Diario'),
                #'move_id': fields.many2one('account.move', u'Asiento Contable', readonly=True),
                #'budget_doc_id': fields.many2one('crossovered.budget.doc', u'Presupuesto', readonly=True),
    }
    
    _defaults = {
                 'date': lambda self, cr, uid, context={}: strftime("%Y-%m-%d"),
                 'state': 'draft',
                 }
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.state != 'draft':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar, solo puede realizar esta operación en estado Borrador'))
        return super(account_spi, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def crear_spi(self, cr, uid, ids, context={}):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('account.spi.resume')
        bank_obj = self.pool.get('res.bank')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        
        for this in self.browse(cr, uid, ids):
            resume_ids = line_obj.search(cr, uid, [('head_id','=',this.id)])
            if resume_ids:
                line_obj.unlink(cr, uid, resume_ids)
            #j = 0
            buf = StringIO.StringIO()
            buf_lb = StringIO.StringIO()
            bancos = {}
            
            if not this.file_account.acc_number:
                raise osv.except_osv('No se puede generar el archivo SPI!', 'No existe numero de cuenta bancaria!!!')
            
            #id_partner = {}
            #data2 = {}
            #data3 = {}
            #data4 = {}
            #lines = this.line_ids
            #tot_amount = 0
            
            fecha = datetime.datetime.strptime(this.date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
            num_cta_empresa = this.file_account.acc_number
            reference = this.file_reference
            transacciones = str(len(this.line_ids))
            total = sum(line.value for line in this.line_ids)
            str_tot = str(total)
            aux_descripcion = 'PAGOS ' + company.name.upper()
            aux_descripcion = aux_descripcion[:30]
            ciudad = company.city
            
            
            cabecera_lb = fecha[:10] + '\t' + num_cta_empresa + '\t' + company.name + '\r\n'
            cabecera_lb = unicodedata.normalize('NFKD',cabecera_lb).encode('ascii','ignore')
            buf_lb.write(cabecera_lb.upper())
            
            cabecera = fecha + ',' + reference + ',' + transacciones + ',01' + ',' + str_tot + ',0000000000000000000000' + ',' + num_cta_empresa + ',' + num_cta_empresa + ',' + aux_descripcion + ',' + ciudad + ',' + fecha[3:10] + '\r\n'
            cabecera = unicodedata.normalize('NFKD',cabecera).encode('ascii','ignore')
            buf.write(cabecera.upper())
            
            if len(this.line_ids)>0:
                for line in this.line_ids:
                    if not line.move_id.partner_id.bank_ids:
                        raise osv.except_osv(u'No se puede generar el archivo SPI !', u'No existe cuenta bancaria configurada para ' + line.move_id.partner_id.name)
                    
                    partner = partner_obj.browse(cr, uid, line.partner_id.id)
                    partner_name = partner.name
                    partner_cut = partner_name[:30]
                    
                    str_val="%.2f"%(line.value)
                    
                    bank_id = 0
                    bank_code = n_lleno = tipo_cta = bank_name = ''
                    for cuenta in line.move_id.partner_id.bank_ids:
                        bank_code = cuenta.bank.bic[:8]
                        n_lleno = cuenta.acc_number
                        bank_name = cuenta.bank.name
                        if cuenta.state == 'c':
                            tipo_cta = '1'
                        elif cuenta.state == 'a':
                            tipo_cta = '2'
                        else:
                            raise osv.except_osv(u'No se puede generar el archivo error !', u'No se reconoce el tipo de cuenta bancaria')
                        break
                    
                    tipo_benef = 2
                    
                    aux_descripcion = 'PAGOS ' + company.name.upper()
                    aux_descripcion = aux_descripcion[:30]
                    
                    #import pdb
                    #pdb.set_trace()
                        
                    detalle= line.move_id.move_id.name[-5:] + ',' + str_val + ',' + line.concept_id.code + ',' + bank_code + ',' + n_lleno + ',0' + tipo_cta +',' + partner_cut + ',' + line.move_id.name + ',' + partner.identifier + '\r\n'
                    detalle = unicodedata.normalize('NFKD',detalle).encode('ascii','ignore')
                    buf.write(detalle.upper())
                    
                    detalle_lb = partner.identifier + '\t' + partner_cut + '\t' + n_lleno + '\t' + str_val + '\t' + bank_code + '\t' + str(tipo_benef) +'\r\n'
                    detalle_lb = unicodedata.normalize('NFKD',detalle_lb).encode('ascii','ignore')
                    buf_lb.write(detalle_lb.upper())
                    
                    if not bancos.has_key(bank_id):
                        bancos[bank_id] = {
                                           'amount': 0.00,
                                           'qty' : 0,
                                           'bic': bank_code,
                                           'name': bank_name,
                                           }
                    bancos[bank_id]['amount'] += line.value
                    bancos[bank_id]['qty'] += 1

            for banco in bancos.keys():
                line_obj.create(cr, uid, {
                        'number':bancos[banco]['bic'],
                        'name':bancos[banco]['name'],
                        'qty':bancos[banco]['qty'],
                        'amount':bancos[banco]['amount'],
                        'head_id':this.id,
                        })
                    
            name = "%s.TXT" % ("SPI-SP")
            name_lb = "%s.TXT" % ("SPI-SP_LB")
#            out = base64.encodestring(buf.getvalue())
#            buf.close()
#            self.write(cr, uid, ids, {'archivo': out, 'file_name': name,'total_amount':tot_amount,'state':'Generado'})
            digest_name = 'SPI-SP.md5'
            #checksum
            digest1 = '%s' % (hashlib.md5(buf.getvalue()).hexdigest())
            digest = '%s %s\n' % (hashlib.md5(buf.getvalue()).hexdigest(), name)
            file_digest = open(digest_name, 'w')
            file_digest.write(digest)
            file_digest.close()
            file_spi = open(name, 'w')
            file_spi.write(buf.getvalue())
            file_spi.close()
            #checksum2
            file_spilb = open(name_lb, 'w')
            file_spilb.write(buf_lb.getvalue())
            file_spilb.close()
            outlb = base64.encodestring(buf_lb.getvalue())
            buf.close()
            #zip file
            zf_name = 'sip-sp %s.zip' % strftime('%Y-%m-%d')
            zf = zipfile.ZipFile(zf_name, mode='w')
            zf_buf = StringIO.StringIO()
            try:
                zf.write(digest_name, compress_type=COMPRESSION)
                zf.write(name)
            finally:
                zf.close()
            zf_tmp = open(zf_name, 'rb')
            zf_buf.write(zf_tmp.read())
            out = base64.encodestring(zf_buf.getvalue())
            zf_buf.close()
            #import pdb
            #pdb.set_trace()
            self.write(cr, uid, ids, {'file_dig':digest1,
                                      'file_spi': out, 
                                      'file_name': zf_name,
                                      'file_lb':outlb,
                                      'file_namelb': name_lb,
                                      'file_amount':total})#,'file_generate':True})
            return True

account_spi()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
