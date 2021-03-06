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

import time
import base64
import StringIO
from lxml import etree
from lxml.etree import DocumentInvalid
import os
import datetime
import logging

from openerp.osv import osv, orm, fields

tpIdProv = {
    'ruc': '01',
    'cedula': '02',
    'pasaporte': '03',
}

tpIdCliente = {
    'ruc': '04',
    'cedula': '05',
    'pasaporte': '06'
    }


class wizard_ats(orm.TransientModel):

    _name = 'wizard.ats'
    _description = 'Anexo Transaccional Simplificado'
    __logger = logging.getLogger(_name)

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _get_company(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    def act_cancel(self, cr, uid, ids, context):
        return {'type': 'ir.actions.act_window_close'}

    def process_lines(self, cr, uid, lines):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        temp = {}
        for line in lines:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {
                        'baseImpAir': 0,
                        'valRetAir': 0
                    }
                temp[line.base_code_id.code]['baseImpAir'] += line.base_amount
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code  # noqa
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00  # noqa
                temp[line.base_code_id.code]['valRetAir'] += abs(line.amount)
        for k, v in temp.items():
            data_air.append(v)
        return data_air

    def convertir_fecha(self, fecha):
        """
        fecha: '2012-12-15'
        return: '15/12/2012'
        """
        f = fecha.split('-')
        date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
        return date.strftime('%d/%m/%Y')

    def _get_ventas(self, cr, period_id, journal_id=False):
        sql_ventas = "SELECT type, sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice \
                      WHERE type IN ('out_invoice', 'out_refund') \
                      AND state IN ('open','paid') \
                      AND period_id = %s" % period_id
        if journal_id:
            where = " AND journal_id=%s" % journal_id
            sql_ventas += where
        sql_ventas += " GROUP BY type"
        cr.execute(sql_ventas)
        res = cr.fetchall()
        resultado = sum(map(lambda x: x[0] == 'out_refund' and x[1] * -1 or x[1], res))  # noqa
        return '%.2f' % resultado

    def _get_ret_iva(self, invoice):
        """
        Return (valRetBien10, valRetServ20,
        valorRetBienes,
        valorRetServicios, valorRetServ100)
        """
        retBien10 = 0
        retServ20 = 0
        retBien = 0
        retServ = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_b':
                if tax.percent == '10':
                    retBien10 += abs(tax.tax_amount)
                else:
                    retBien += abs(tax.tax_amount)
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
                elif tax.percent == '20':
                    retServ20 += abs(tax.tax_amount)
                else:
                    retServ += abs(tax.tax_amount)
        return retBien10, retServ20, retBien, retServ, retServ100

    def act_export_ats(self, cr, uid, ids, context):
        inv_obj = self.pool.get('account.invoice')
        wiz = self.browse(cr, uid, ids)[0]
        period_id = wiz.period_id.id
        ruc = wiz.company_id.partner_id.identifier
        ats = etree.Element('iva')
        etree.SubElement(ats, 'TipoIDInformante').text = 'R'
        etree.SubElement(ats, 'IdInformante').text = str(ruc)
        etree.SubElement(ats, 'razonSocial').text = wiz.company_id.name
        period = self.pool.get('account.period').browse(cr, uid, [period_id])[0]  # noqa
        etree.SubElement(ats, 'Anio').text = time.strftime('%Y', time.strptime(period.date_start, '%Y-%m-%d'))  # noqa
        etree.SubElement(ats, 'Mes'). text = time.strftime('%m', time.strptime(period.date_start, '%Y-%m-%d'))  # noqa
        etree.SubElement(ats, 'numEstabRuc').text = wiz.num_estab_ruc.zfill(3)
        total_ventas = self._get_ventas(cr, period_id)
        etree.SubElement(ats, 'totalVentas').text = total_ventas
        etree.SubElement(ats, 'codigoOperativo').text = 'IVA'
        compras = etree.Element('compras')
        # Facturas de Compra con retenciones
        inv_ids = inv_obj.search(cr, uid, [('state', 'in', ['open', 'paid']),
                                           ('period_id', '=', period_id),
                                           ('type', 'in', ['in_invoice', 'liq_purchase']),  # noqa
                                           ('company_id', '=', wiz.company_id.id)])  # noqa
        self.__logger.info("Compras registradas: %s" % len(inv_ids))
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detallecompras = etree.Element('detalleCompras')
            etree.SubElement(detallecompras, 'codSustento').text = inv.sustento_id.code  # noqa
            if not inv.partner_id.identifier:
                raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)  # noqa
            etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[inv.partner_id.type_identifier]  # noqa
            etree.SubElement(detallecompras, 'idProv').text = inv.partner_id.identifier  # noqa
            if inv.auth_inv_id:
                tcomp = inv.auth_inv_id.type_id.code
            else:
                tcomp = '03'
            etree.SubElement(detallecompras, 'tipoComprobante').text = tcomp
            etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(inv.date_invoice)  # noqa
            if inv.type == 'in_invoice':
                se = inv.auth_inv_id.serie_entidad
                pe = inv.auth_inv_id.serie_emision
                sec = '%09d' % int(inv.reference)
                auth = inv.auth_inv_id.name
            elif inv.type == 'liq_purchase':
                se = inv.journal_id.auth_id.serie_entidad
                pe = inv.journal_id.auth_id.serie_emision
                sec = inv.number[8:]
                auth = inv.journal_id.auth_id.name
            etree.SubElement(detallecompras, 'establecimiento').text = se
            etree.SubElement(detallecompras, 'puntoEmision').text = pe
            etree.SubElement(detallecompras, 'secuencial').text = sec
            etree.SubElement(detallecompras, 'fechaEmision').text = self.convertir_fecha(inv.date_invoice)  # noqa
            etree.SubElement(detallecompras, 'autorizacion').text = auth
            etree.SubElement(detallecompras, 'baseNoGraIva').text = inv.amount_novat == 0 and '0.00' or '%.2f' % inv.amount_novat  # noqa
            etree.SubElement(detallecompras, 'baseImponible').text = '%.2f' % inv.amount_vat_cero  # noqa
            etree.SubElement(detallecompras, 'baseImpGrav').text = '%.2f' % inv.amount_vat  # noqa
            etree.SubElement(detallecompras, 'baseImpExe').text = '0.00'
            etree.SubElement(detallecompras, 'montoIce').text = '0.00'
            etree.SubElement(detallecompras, 'montoIva').text = '%.2f' % inv.amount_tax  # noqa
            valRetBien10, valRetServ20, valorRetBienes, valorRetServicios, valorRetServ100 = self._get_ret_iva(inv)  # noqa
            etree.SubElement(detallecompras, 'valRetBien10').text = '%.2f' % valRetBien10  # noqa
            etree.SubElement(detallecompras, 'valRetServ20').text = '%.2f' % valRetServ20  # noqa
            etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f' % valorRetBienes  # noqa
            # etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f'%abs(inv.taxed_ret_vatb)  # noqa
            etree.SubElement(detallecompras, 'valorRetServicios').text = '%.2f' % valorRetServicios  # noqa
            etree.SubElement(detallecompras, 'valRetServ100').text = '%.2f' % valorRetServ100  # noqa
            etree.SubElement(detallecompras, 'totbasesImpReemb').text = '0.00'
            pagoExterior = etree.Element('pagoExterior')
            etree.SubElement(pagoExterior, 'pagoLocExt').text = '01'
            etree.SubElement(pagoExterior, 'paisEfecPago').text = 'NA'
            etree.SubElement(pagoExterior, 'aplicConvDobTrib').text = 'NA'
            etree.SubElement(pagoExterior, 'pagExtSujRetNorLeg').text = 'NA'
            detallecompras.append(pagoExterior)
            if inv.amount_pay >= wiz.pay_limit:
                formasDePago = etree.Element('formasDePago')
                etree.SubElement(formasDePago, 'formaPago').text = '02'
                detallecompras.append(formasDePago)
            if inv.retention_ir or inv.no_retention_ir:
                air = etree.Element('air')
                data_air = self.process_lines(cr, uid, inv.tax_line)
                for da in data_air:
                    detalleAir = etree.Element('detalleAir')
                    etree.SubElement(detalleAir, 'codRetAir').text = da['codRetAir']  # noqa
                    etree.SubElement(detalleAir, 'baseImpAir').text = '%.2f' % da['baseImpAir']  # noqa
                    etree.SubElement(detalleAir, 'porcentajeAir').text = '%.2f' % da['porcentajeAir']  # noqa
                    etree.SubElement(detalleAir, 'valRetAir').text = '%.2f' % da['valRetAir']  # noqa
                    air.append(detalleAir)
                detallecompras.append(air)
            flag = False
            if inv.retention_id and (inv.retention_ir or inv.retention_vat):
                flag = True
                etree.SubElement(detallecompras, 'estabRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_entidad or '000'  # noqa
                etree.SubElement(detallecompras, 'ptoEmiRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_emision or '000'  # noqa
                etree.SubElement(detallecompras, 'secRetencion1').text = flag and inv.retention_id.num_document[6:] or '%09d' % 0  # noqa
                etree.SubElement(detallecompras, 'autRetencion1').text = flag and inv.journal_id.auth_ret_id.name or '%010d' % 0  # noqa
                etree.SubElement(detallecompras, 'fechaEmiRet1').text = flag and self.convertir_fecha(inv.retention_id.date)  # noqa
            compras.append(detallecompras)
        ats.append(compras)
        if float(total_ventas) > 0:
            # VENTAS DECLARADAS
            ventas = etree.Element('ventas')
            inv_ids = inv_obj.search(cr, uid, [
                ('state', 'in', ['open', 'paid']),
                ('period_id', '=', period_id),
                ('type', 'in', ['out_invoice', 'out_refund']),
                ('company_id', '=', wiz.company_id.id)])
            pdata = {}
            self.__logger.info("Ventas registradas: %s" % len(inv_ids))
            for inv in inv_obj.browse(cr, uid, inv_ids):
                part_id = inv.partner_id.id
                tipoComprobante = inv.journal_id.auth_id.type_id.code
                keyp = '%s-%s' % (part_id, tipoComprobante)
                partner_data = {
                    keyp: {
                        'tpIdCliente': inv.partner_id.type_identifier,
                        'idCliente': inv.partner_id.identifier,
                        'numeroComprobantes': 0,
                        'basenoGraIva': 0,
                        'baseImponible': 0,
                        'baseImpGrav': 0,
                        'montoIva': 0,
                        'valorRetRenta': 0,
                        'tipoComprobante': tipoComprobante,
                        'valorRetIva': 0
                    }
                }
                if not pdata.get(keyp, False):
                    pdata.update(partner_data)
                elif pdata[keyp]['tipoComprobante'] == tipoComprobante:
                    pdata[keyp]['numeroComprobantes'] += 1
                else:
                    pdata.update(partner_data)
                pdata[keyp]['basenoGraIva'] += inv.amount_novat
                pdata[keyp]['baseImponible'] += inv.amount_vat_cero
                pdata[keyp]['baseImpGrav'] += inv.amount_vat
                pdata[keyp]['montoIva'] += inv.amount_tax
                if inv.retention_ir:
                    data_air = self.process_lines(cr, uid, inv.tax_line)
                    for dt in data_air:
                        pdata[keyp]['valorRetRenta'] += dt['valRetAir']
                pdata[keyp]['valorRetIva'] += abs(inv.taxed_ret_vatb) + abs(inv.taxed_ret_vatsrv)  # noqa

            for k, v in pdata.items():
                detalleVentas = etree.Element('detalleVentas')
                etree.SubElement(detalleVentas, 'tpIdCliente').text = tpIdCliente[v['tpIdCliente']]  # noqa
                etree.SubElement(detalleVentas, 'idCliente').text = v['idCliente']  # noqa
                etree.SubElement(detalleVentas, 'parteRelVtas').text = 'NO'
                etree.SubElement(detalleVentas, 'tipoComprobante').text = v['tipoComprobante']  # noqa
                etree.SubElement(detalleVentas, 'numeroComprobantes').text = str(v['numeroComprobantes'])  # noqa
                etree.SubElement(detalleVentas, 'baseNoGraIva').text = '%.2f' % v['basenoGraIva']  # noqa
                etree.SubElement(detalleVentas, 'baseImponible').text = '%.2f' % v['baseImponible']  # noqa
                etree.SubElement(detalleVentas, 'baseImpGrav').text = '%.2f' % v['baseImpGrav']  # noqa
                etree.SubElement(detalleVentas, 'montoIva').text = '%.2f' % v['montoIva']  # noqa
                etree.SubElement(detalleVentas, 'valorRetIva').text = '%.2f' % v['valorRetIva']  # noqa
                etree.SubElement(detalleVentas, 'valorRetRenta').text = '%.2f' % v['valorRetRenta']  # noqa
                ventas.append(detalleVentas)
            ats.append(ventas)
        # Ventas establecimiento
        ventasEstablecimiento = etree.Element('ventasEstablecimiento')
        ventaEst = etree.Element('ventaEst')
        etree.SubElement(ventaEst, 'codEstab').text = inv.journal_id.auth_id.serie_emision  # noqa
        etree.SubElement(ventaEst, 'ventasEstab').text = self._get_ventas(cr, period_id)  # noqa
        ventasEstablecimiento.append(ventaEst)
        ats.append(ventasEstablecimiento)
        # Documentos Anulados
        anulados = etree.Element('anulados')
        inv_ids = inv_obj.search(cr, uid, [('state', '=', 'cancel'),
                                           ('period_id', '=', period_id),
                                           ('type', '=', 'out_invoice'),
                                           ('company_id', '=', wiz.company_id.id)])  # noqa
        self.__logger.info("Ventas Anuladas: %s" % len(inv_ids))
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code  # noqa
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad  # noqa
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision  # noqa
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name  # noqa
            anulados.append(detalleAnulados)
        # Liquidaciones de compra
        liq_ids = inv_obj.search(cr, uid, [('state', '=', 'cancel'),
                                           ('period_id', '=', period_id),
                                           ('type', '=', 'liq_purchase'),
                                           ('company_id', '=', wiz.company_id.id)])  # noqa
        for inv in inv_obj.browse(cr, uid, liq_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code  # noqa
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad  # noqa
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision  # noqa
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name  # noqa
            anulados.append(detalleAnulados)
        retention_obj = self.pool.get('account.retention')
        ret_ids = retention_obj.search(cr, uid, [('state', '=', 'cancel'),
                                                 ('in_type', '=', 'ret_out_invoice'),  # noqa
                                                 ('date', '>=', wiz.period_id.date_start),  # noqa
                                                 ('date', '<=', wiz.period_id.date_stop)])  # noqa
        for ret in retention_obj.browse(cr, uid, ret_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = ret.auth_id.type_id.code  # noqa
            etree.SubElement(detalleAnulados, 'establecimiento').text = ret.auth_id.serie_entidad  # noqa
            etree.SubElement(detalleAnulados, 'puntoEmision').text = ret.auth_id.serie_emision  # noqa
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(ret.num_document[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(ret.num_document[8:]))  # noqa
            etree.SubElement(detalleAnulados, 'autorizacion').text = ret.auth_id.name  # noqa
            anulados.append(detalleAnulados)
        ats.append(anulados)
        file_path = os.path.join(os.path.dirname(__file__), 'XSD/ats.xsd')
        schema_file = open(file_path)
        file_ats = etree.tostring(ats,
                                  pretty_print=True,
                                  encoding='iso-8859-1')
        # validata schema
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not wiz.no_validate:
            try:
                xmlschema.assertValid(ats)
            except DocumentInvalid as e:
                #import pdb
                #pdb.set_trace()
                raise osv.except_osv(
                    'Error de Datos',
                    u"""El sistema generó el XML pero los datos no pasan la validación XSD del SRI.
                    \nLos errores mas comunes son:\n
                    * RUC,Cédula o Pasaporte contiene caracteres no válidos.
                    \n* Números de documentos están duplicados.\n\n
                    El siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))  # noqa
        buf = StringIO.StringIO()
        buf.write(file_ats)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s%s.XML" % (
            "AT",
            wiz.period_id.name[:2],
            wiz.period_id.name[3:8]
        )
        self.write(cr, uid, ids, {
            'state': 'export',
            'data': out,
            'fcname': name
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.ats',
            'view_mode': ' form',
            'view_type': ' form',
            'res_id': wiz.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    _columns = {
        'fcname': fields.char('Nombre de Archivo', size=50, readonly=True),
        'period_id': fields.many2one('account.period', 'Periodo'),
        'company_id': fields.many2one('res.company', 'Compania'),
        'num_estab_ruc': fields.char(
            'Num. de Establecimientos',
            size=3,
            required=True
        ),
        'pay_limit': fields.float('Limite de Pago'),
        'data': fields.binary('Archivo XML'),
        'no_validate': fields.boolean('No Validar'),
        'state': fields.selection(
            (
                ('choose', 'choose'),
                ('export', 'export')
            )
        ),
        }

    _defaults = {
        'state': 'choose',
        'period_id': _get_period,
        'company_id': _get_company,
        'pay_limit': 1000.00,
        'num_estab_ruc': '001'
    }
