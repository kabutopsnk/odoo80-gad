# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
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

#from lxml import etree

from openerp.osv import fields, osv
import time
import StringIO
import base64
from datetime import datetime
#from openerp.addons.gad_tools import XLSWriter

import xlwt


class WizardAccountReport(osv.TransientModel):
    _name = 'wizard.account.report'


    _columns = {
                'fy_id': fields.many2one('account.fiscalyear', required=True, string=u'Ejercicio Fiscal'),
                'period_id': fields.many2one('account.period', required=False, string=u'Período'),
                #'documento': fields.selection([ ('con_inicial',  u'Apertura Inicial'),
                #                                ('con_balance',  u'Balance de Comprobación'),
                #                                ('con_transfer', u'Transferencias'),
                #                                ('pre_inicial',  u'Presupuesto Inicial'),
                #                                ('pre_cedula',   u'Cédula de Ingresos y Gastos')], u'Tipo de Documento', required=True),
                'datas_fname':fields.char('Nombre Archivo', size=32),
                'datas':fields.binary('Archivo',readonly=True),
                }

    def onchange_fy(self, cr, uid, ids, fy_id, context=None):
        return {'value': {'period_id': False}}

    def generar(self, cr, uid, ids, context=None):

        wiz = self.browse(cr, uid, ids, context)[0]
        #model_data = self.pool.get('ir.model.data')

        obj_fy=self.pool.get('account.fiscalyear')
        obj_period=self.pool.get('account.period')
        obj_budget = self.pool.get("crossovered.budget")

        for per in obj_period.browse(cr, uid, [wiz.period_id.id]):
            name=per.name[:2]
            fecha1=per.date_start
            fecha2=per.date_stop
            
        #BALANCE DE COMPROBACION
        #buf1 = StringIO.StringIO()
        #writer = XLSWriter.XLSWriter()
        book = xlwt.Workbook()
        sheet_bc = book.add_sheet("Balance Comprobacion")
        
        #SITUACION FINANCIERA
        sheet_sf = book.add_sheet("Situacion Financiera")
        
        #writer.append(['PERIODO:',wiz.period_id.name])
        #writer.append([])
        #writer.append(['CODIGO','INICIAL DEBE','INICIAL HABER','MOVIMIENTOS DEBE','MOVIMIENTOS HABER','SUMAS DEBE','SUMAS HABER','FINAL DEBE','FINAL HABER'])
        sheet_bc.write(0,0,'Periodo:')
        sheet_bc.write(0,1,wiz.period_id.name)
        
        sheet_bc.write(2,0,'CODIGO')
        sheet_bc.write(2,1,'CODIGO')
        sheet_bc.write(2,2,'Inicial DEBE')
        sheet_bc.write(2,3,'Inicial HABER')
        sheet_bc.write(2,4,'Movimientos DEBE')
        sheet_bc.write(2,5,'Movimientos HABER')
        sheet_bc.write(2,6,'Sumas DEBE')
        sheet_bc.write(2,7,'Sumas HABER')
        sheet_bc.write(2,8,'FINAL DEBE')
        sheet_bc.write(2,9,'FINAL HABER')
        
        sheet_sf.write(0,0,'Periodo:')
        sheet_sf.write(0,1,wiz.period_id.name)
        
        sheet_sf.write(2,0,'CODIGO')
        sheet_sf.write(2,1,'DESCRIPCION')
        sheet_sf.write(2,2,'CANTIDAD')
        
        
        query = "CREATE TEMP TABLE TEMP_BALANCE1 AS \
                SELECT	LEFT(A.CODE,3)::INTEGER NIV1, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END NIV2, \
                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END NIV3, A.NAME NOMBRE, \
                        COALESCE(SUM(L.DEBIT),0.00) DEU_INI, COALESCE(SUM(L.CREDIT),0.00) ACR_INI, 0.00 DEU_FLU, 0.00 ACR_FLU \
                FROM	ACCOUNT_MOVE_LINE L \
                INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                WHERE	L.STATE='valid' AND L.DATE < '"+fecha1+"' \
                GROUP BY LEFT(A.CODE,3)::INTEGER, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END, \
                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END, A.NAME \
                UNION ALL \
                SELECT	LEFT(A.CODE,3)::INTEGER NIV1, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END NIV2, \
                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END NIV3, A.NAME NOMBRE, \
                        0.00 DEU_INI, 0.00 ACR_INI, COALESCE(SUM(L.DEBIT),0.00) DEU_FLU, COALESCE(SUM(L.CREDIT),0.00) ACR_FLU \
                FROM	ACCOUNT_MOVE_LINE L \
                INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                WHERE	L.STATE='valid' AND L.DATE BETWEEN '"+fecha1+"' AND '"+fecha2+"' \
                GROUP BY LEFT(A.CODE,3)::INTEGER, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END, \
                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END, A.NAME; \
                SELECT	DATE_PART('month','"+fecha2+"'::DATE)::INTEGER::TEXT||'|'||NIV1::TEXT||'|'||NIV2||'|'||NIV3::TEXT||'|'||NOMBRE||'|'||SUM(DEU_INI)::TEXT||'|'|| \
                        SUM(ACR_INI)::TEXT||'|'||SUM(DEU_FLU)::TEXT||'|'||SUM(ACR_FLU)::TEXT||'|'||SUM(DEU_INI+DEU_FLU)::TEXT||'|'||SUM(ACR_INI+ACR_FLU)::TEXT||'|'|| \
                        CASE WHEN SUM(DEU_INI+DEU_FLU)>SUM(ACR_INI+ACR_FLU) THEN SUM(DEU_INI+DEU_FLU)-SUM(ACR_INI+ACR_FLU) ELSE 0.00 END::TEXT||'|'|| \
                        CASE WHEN SUM(ACR_INI+ACR_FLU)>SUM(DEU_INI+DEU_FLU) THEN SUM(ACR_INI+ACR_FLU)-SUM(DEU_INI+DEU_FLU) ELSE 0.00 END::TEXT \
                FROM	TEMP_BALANCE1 \
                GROUP BY NIV1, NIV2, NIV3, NOMBRE ORDER BY NIV1, NIV2, NIV3, NOMBRE;"

        cr.execute(query)
        i = 2
        resultados = cr.fetchall()
        for resultado in resultados:
            i += 1
            linea = resultado[0].split('|')
            sheet_bc.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
            sheet_bc.write(i, 1, linea[4])
            sheet_bc.write(i, 2, float(linea[5].replace(".","")))
            sheet_bc.write(i, 3, float(linea[6].replace(".","")))
            sheet_bc.write(i, 4, float(linea[7].replace(".","")))
            sheet_bc.write(i, 5, float(linea[8].replace(".","")))
            sheet_bc.write(i, 6, float(linea[9].replace(".","")))
            sheet_bc.write(i, 7, float(linea[10].replace(".","")))
            sheet_bc.write(i, 8, float(linea[11].replace(".","")))
            sheet_bc.write(i, 9, float(linea[12].replace(".","")))
            
            sheet_sf.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
            sheet_sf.write(i, 1, linea[4])
            sheet_sf.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            
        #Estado de Operaciones
        sheet_eo = book.add_sheet("Estado Operaciones")
        
        sheet_eo.write(0,0,'Periodo:')
        sheet_eo.write(0,1,wiz.period_id.name)
        
        sheet_eo.write(2,0,'Codigo')
        sheet_eo.write(2,1,'Denominacion')
        sheet_eo.write(2,2,'Cantidad')
        
        #Estado de Operaciones
        sheet_ef = book.add_sheet("Estado Flujos")
        
        sheet_ef.write(0,0,'Periodo:')
        sheet_ef.write(0,1,wiz.period_id.name)
        
        sheet_ef.write(2,0,'Codigo')
        sheet_ef.write(2,1,'Denominacion')
        sheet_ef.write(2,2,'Cantidad')
        
        i = j = 4
        sheet_eo.write(i, 1, "RESULTADO DE EXPLOTACION")
        sheet_ef.write(j, 1, "FUENTES CORRIENTES")
        i += 1
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1]=='624':
                i += 1
                sheet_eo.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_eo.write(i, 1, linea[4])
                sheet_eo.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            if linea[1]=='113' and linea[2].zfill(2)[:1]=='1':
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
                
        i += 2
        j += 2
        sheet_eo.write(i, 1, "RESULTADO DE OPERACION")
        sheet_ef.write(j, 1, "USOS CORRIENTES")
        i += 1
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1] in ['621', '623', '631', '633', '634']:
                i += 1
                sheet_eo.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_eo.write(i, 1, linea[4])
                sheet_eo.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            if linea[1]=='213' and linea[2].zfill(2)[:1]=='5':
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
                
        i += 2
        j += 2
        sheet_eo.write(i, 1, "TRANSFERENCIAS NETAS")
        sheet_ef.write(j, 1, "FUENTES DE CAPITAL")
        i += 1
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1] in ['626', '636']:
                i += 1
                sheet_eo.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_eo.write(i, 1, linea[4])
                sheet_eo.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            if linea[1]=='113' and linea[2].zfill(2)[:1]=='2':
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
                
        i += 2
        j += 2
        sheet_eo.write(i, 1, "RESULTADO FINANCIERO")
        sheet_ef.write(j, 1, "USOS DE PRODUCCION, INVERSION Y CAPITAL")
        i += 1
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1] in ['625', '635']:
                i += 1
                sheet_eo.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_eo.write(i, 1, linea[4])
                sheet_eo.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            if linea[1]=='213' and linea[2].zfill(2)[:1] in ['7','8']:
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
                
        i += 2
        j += 2
        sheet_eo.write(i, 1, "RESULTADO DEL EJERCICIO")
        sheet_ef.write(j, 1, "APLICACION DEL SUPEAVIT O FINANCIAMIENTO DEL DEFICIT")
        j += 2
        sheet_ef.write(j, 1, "FUENTES DE FINANCIAMIENTO")
        i += 1
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1] in ['618']:
                i += 1
                sheet_eo.write(i, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_eo.write(i, 1, linea[4])
                sheet_eo.write(i, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            if linea[1]=='113' and linea[2].zfill(2)[:1] in ['3','9']:
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            
        j += 2
        sheet_ef.write(j, 1, "USOS DE FINANCIAMIENTO")
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1]=='213' and linea[2].zfill(2)[:1] in ['9']:
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
                
        j += 2
        sheet_ef.write(j, 1, "FLUJOS NO PRESUPUESTARIOS")
        j += 1
        for resultado in resultados:
            linea = resultado[0].split('|')
            if linea[1] in ['213','113'] and linea[2].zfill(2)[:1] in ['8']:
                j += 1
                sheet_ef.write(j, 0, linea[1] + '.' + linea[2].zfill(2) + '.' + linea[3].zfill(2))
                sheet_ef.write(j, 1, linea[4])
                sheet_ef.write(j, 2, float(linea[11].replace(".","")) - float(linea[12].replace(".","")))
            
        #CEDULA INGRESOS
        sheet_ci = book.add_sheet("Cedula Ingresos")
        
        sheet_ci.write(0,0,'Periodo:')
        sheet_ci.write(0,1,wiz.period_id.name)
        
        sheet_ci.write(2,0,'Codigo')
        sheet_ci.write(2,1,'Denominacion')
        sheet_ci.write(2,2,'Inicial')
        sheet_ci.write(2,3,'Modificado')
        sheet_ci.write(2,4,'Codificado')
        sheet_ci.write(2,5,'Devengado')
        sheet_ci.write(2,6,'Recaudado')
        
        budget_id = obj_budget.search(cr, uid, [('date_from','<=',fecha2),('date_to','>=',fecha2),('budget_type','=','I')])
        query = "CREATE TEMP TABLE TEMP_INGRESOS AS \
                SELECT    BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha2+"')),0.00) \
                    + COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha2+"')),0.00) REFORMA, \
                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha2+"'))::NUMERIC,2),0.00) DEVENGADO, \
                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha2+"'))::NUMERIC,2),0.00) RECAUDADO \
                FROM    CROSSOVERED_BUDGET B \
                INNER    JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                WHERE    B.ID = "+ str(budget_id[0]) +" \
                GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                SELECT    BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                    ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'1' NIVEL \
                FROM    TEMP_INGRESOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                GROUP BY BP.CODE, BP.NAME \
                UNION \
                SELECT    BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                    ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'2' NIVEL \
                FROM    TEMP_INGRESOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                GROUP BY BP.CODE, BP.NAME \
                UNION \
                SELECT    BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                    ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'3' NIVEL \
                FROM    TEMP_INGRESOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                GROUP BY BP.CODE, BP.NAME \
                UNION \
                SELECT    BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                    ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'4' NIVEL \
                FROM    TEMP_INGRESOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                GROUP BY BP.CODE, BP.NAME \
                UNION \
                SELECT    'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                    ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'999' NIVEL \
                FROM    TEMP_INGRESOS \
                ORDER BY 1;"

        cr.execute(query)
        i=2
        for resultado in cr.fetchall():
            i += 1
            sheet_ci.write(i,0,resultado[0])
            sheet_ci.write(i,1,resultado[1])
            sheet_ci.write(i,2,float((resultado[2].replace(".","")).replace(",",".") ))
            sheet_ci.write(i,3,float((resultado[3].replace(".","")).replace(",",".") ))
            sheet_ci.write(i,4,float((resultado[4].replace(".","")).replace(",",".") ))
            sheet_ci.write(i,5,float((resultado[5].replace(".","")).replace(",",".") ))
            sheet_ci.write(i,6,float((resultado[6].replace(".","")).replace(",",".") ))
            
        
            
        #CEDULA GASTOS
        sheet_cg = book.add_sheet("Cedula Gastos")
        
        sheet_cg.write(0,0,'Periodo:')
        sheet_cg.write(0,1,wiz.period_id.name)
        
        sheet_cg.write(2,0,'Codigo')
        sheet_cg.write(2,1,'Denominacion')
        sheet_cg.write(2,2,'Inicial')
        sheet_cg.write(2,3,'Modificado')
        sheet_cg.write(2,4,'Codificado')
        sheet_cg.write(2,5,'Comprometido')
        sheet_cg.write(2,6,'Devengado')
        sheet_cg.write(2,7,'Pagado')
        
        budget_id = obj_budget.search(cr, uid, [('date_from','<=',fecha2),('date_to','>=',fecha2),('budget_type','=','G')])
        query=  "CREATE TEMP TABLE TEMP_GASTOS AS \
                SELECT    EST.ID AREA, PRG.ID PROGRAMA, BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha2+"')),0.00) \
                    +COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha2+"')),0.00) REFORMA, \
                    COALESCE((SELECT SUM(DL.COMMITED_AMOUNT) FROM CROSSOVERED_BUDGET_DOC_LINE DL WHERE DL.BUDGET_LINE_ID=BL.ID  AND DL.STATE='commited' \
                    AND BUDGET_DOC_ID IN (SELECT ID FROM CROSSOVERED_BUDGET_DOC D WHERE D.STATE='commited' AND DATE_COMMITED<='"+fecha2+"')),0.00) COMPROMETIDO, \
                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha2+"'))::NUMERIC,2),0.00) DEVENGADO, \
                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha2+"'))::NUMERIC,2),0.00) PAGADO \
                FROM    CROSSOVERED_BUDGET B \
                INNER    JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                INNER    JOIN PROJECT_TASK T ON (T.ID=BL.TASK_ID) \
                INNER    JOIN PROJECT_PROJECT P ON (P.ID=T.PROJECT_ID) \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=P.ESTRATEGY_ID) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=P.PROGRAM_ID) \
                WHERE    B.ID = "+ str(budget_id[0]) +" \
                GROUP BY EST.ID, PRG.ID, BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                SELECT    EST.SEQUENCE::TEXT, EST.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '10' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                GROUP BY EST.SEQUENCE::TEXT, EST.NAME \
                UNION \
                SELECT    EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '100' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME \
                UNION \
                SELECT    EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '1' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                UNION \
                SELECT    EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '2' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                UNION \
                SELECT    EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '3' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                UNION \
                SELECT    EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '4' NIVEL \
                FROM    TEMP_GASTOS \
                INNER    JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                INNER    JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                INNER    JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                UNION \
                SELECT    'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                    ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '999' NIVEL \
                FROM    TEMP_GASTOS \
                ORDER BY 1;"
                
        cr.execute(query)
        i=2
        for resultado in cr.fetchall():
            i += 1
            sheet_cg.write(i,0,resultado[0])
            sheet_cg.write(i,1,resultado[1])
            sheet_cg.write(i,2,float((resultado[2].replace(".","")).replace(",",".") ))
            sheet_cg.write(i,3,float((resultado[3].replace(".","")).replace(",",".") ))
            sheet_cg.write(i,4,float((resultado[4].replace(".","")).replace(",",".") ))
            sheet_cg.write(i,5,float((resultado[5].replace(".","")).replace(",",".") ))
            sheet_cg.write(i,6,float((resultado[6].replace(".","")).replace(",",".") ))
            sheet_cg.write(i,7,float((resultado[7].replace(".","")).replace(",",".") ))
        
            
        #GUARDAMOS TODO
        book.save("reporte_contable.xls")
        out = open("reporte_contable.xls","rb").read().encode("base64")

        self.write(cr, uid, ids, {'datas': out, 'datas_fname': "reporte_contable.xls"})


        return {
            'type': 'ir.actions.act_window',
            'name': 'Reportes Contabilidad',
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wizard.account.report',
            'res_id': wiz.id,
            'nodestroy': True,
            'target': 'new',
            'context': context,
            }


WizardAccountReport()