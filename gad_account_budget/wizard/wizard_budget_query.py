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



class WizardBudgetQuery(osv.TransientModel):
    _name = 'wizard.budget.query'

    _columns = {
                'budget_id': fields.many2one('crossovered.budget', required=True, string='Presupuesto', domain=[('state','in',['confirm','validate'])]),
                }

    def action_budgets(self, cr, uid, ids, context=None):

        wiz = self.browse(cr, uid, ids, context)[0]
        model_data = self.pool.get('ir.model.data')

        tipo=''
        if wiz.budget_id.budget_type=='G':
            tipo='Gastos'
            tree_view = model_data.get_object_reference(cr, uid, 'gad_account', 'view_account_crossovered_budget_line_tree')

        if wiz.budget_id.budget_type=='I':
            tipo='Ingresos'
            tree_view = model_data.get_object_reference(cr, uid, 'gad_account', 'view_account_crossovered_budget_line_tree_ingresos')

        return {
            'name':      u'Cédula Presupuestaria de '+tipo,
            'type':      'ir.actions.act_window',
            'res_model': 'crossovered.budget.lines',
            'view_type': 'form',
            'view_mode': 'tree',
            'views':     [(tree_view and tree_view[1] or False, 'tree')],
            'domain':    "[('crossovered_budget_id','=',%s)]" % wiz.budget_id.id
            }

WizardBudgetQuery()



class WizardBudgetCedula(osv.TransientModel):
    _name = 'wizard.budget.cedula'

    _columns = {
                'budget_type': fields.selection([('G','Gasto'),('I','Ingreso')], u'Tipo Presupuestario', required=True),
                'budget_id': fields.many2one('crossovered.budget', required=True, string='Presupuesto', domain=[('state','in',['confirm','validate'])]),
                'niveles': fields.boolean(u'Mostrar x Niveles?'),
                'fecha': fields.date(u'Fecha de Corte', required=True),
                }

    _defaults = {
        'niveles': True, 'fecha': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def onchange_type(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget_id': False}}

    def check_report(self, cr, uid, ids, context=None):

        wiz = self.browse(cr, uid, ids, context)[0]
        datas = {'ids':[1], 'model': 'crossovered.budget.lines'}

        tipo=''
        if wiz.budget_type=='G':
            tipo='Gastos'
            reporte='gad_account_budget.cedula_gastos'

        if wiz.budget_type=='I':
            tipo='Ingresos'
            reporte='gad_account_budget.cedula_ingresos'

        return {
            'name':      u'Cédula Presupuestaria de '+tipo,
            'type':      'ir.actions.report.xml',
            'report_name': reporte,
            'res_model': 'crossovered.budget.lines',
            'data': datas,
            'nodestroy': True,
            'context':    {'budget_type':wiz.budget_type, 'budget_id': str(wiz.budget_id.id), 'budget_name': wiz.budget_id.name, 'niveles': wiz.niveles, 'fecha':wiz.fecha}
            }

WizardBudgetCedula()



class WizardBudgetEstadoEjecucion(osv.TransientModel):
    _name = 'wizard.budget.estado_ejecucion'

    _columns = {
                'budget_type': fields.selection([('G','Gasto'),('I','Ingreso')], u'Tipo Presupuestario', required=True),
                'budget_id': fields.many2one('crossovered.budget', required=True, string='Presupuesto', domain=[('state','in',['confirm','validate'])]),
                'fecha': fields.date(u'Fecha de Corte', required=True),
                }

    _defaults = {
        'fecha': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def onchange_type(self, cr, uid, ids, task_id=False, context=None):
        return {'value': {'budget_id': False}}

    def check_report(self, cr, uid, ids, context=None):

        wiz = self.browse(cr, uid, ids, context)[0]
        datas = {'ids':[1], 'model': 'crossovered.budget.lines'}

        return {
            'name':      u'Estado de Ejecución Presupuestaria',
            'type':      'ir.actions.report.xml',
            'report_name': 'gad_account_budget.estado_ejecucion',
            'res_model': 'crossovered.budget.lines',
            'data': datas,
            'nodestroy': True,
            'context':    {'budget_type':wiz.budget_type, 'budget_id': str(wiz.budget_id.id), 'budget_name': wiz.budget_id.name, 'fecha':wiz.fecha}
            }

WizardBudgetEstadoEjecucion()



class WizardEsigef(osv.TransientModel):
    _name = 'wizard.esigef'

    _columns = {
                'fy_id': fields.many2one('account.fiscalyear', required=True, string=u'Ejercicio Fiscal'),
                'period_id': fields.many2one('account.period', required=False, string=u'Período'),
                'documento': fields.selection([ ('con_inicial',  u'Apertura Inicial'),
                                                ('con_balance',  u'Balance de Comprobación'),
                                                ('con_transfer', u'Transferencias'),
                                                ('pre_inicial',  u'Presupuesto Inicial'),
                                                ('pre_cedula',   u'Cédula de Ingresos y Gastos')], u'Tipo de Documento', required=True),
                'datas_fname':fields.char('Nombre Archivo', size=32),
                'datas':fields.binary('Archivo',readonly=True),
                }

    def onchange_fy(self, cr, uid, ids, fy_id, context=None):
        return {'value': {'period_id': False}}

    def generar(self, cr, uid, ids, context=None):

        wiz = self.browse(cr, uid, ids, context)[0]
        model_data = self.pool.get('ir.model.data')

        name1=""
        query=""
        obj_fy=self.pool.get('account.fiscalyear')
        obj_period=self.pool.get('account.period')

        buf1 = StringIO.StringIO()

        if context.get('documento')=='con_inicial':
            for fy in obj_fy.browse(cr, uid, [context.get('fy_id')]):
                fecha=fy.date_start
            name1 = "00 Contabilidad.txt"
            query = "SELECT	'1|'||LEFT(A.CODE,3)::INTEGER::TEXT||'|'|| \
	                        CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER::TEXT ELSE '0' END || '|' || \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER::TEXT ELSE '0' END || '|' || \
	                        COALESCE(SUM(L.DEBIT),0.00)::TEXT || '|' || COALESCE(SUM(L.CREDIT),0.00)::TEXT \
                    FROM	ACCOUNT_MOVE_LINE L \
                    INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                    WHERE	L.STATE='valid' AND L.DATE < '"+fecha+"' \
                    GROUP BY LEFT(A.CODE,3), \
	                        CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER::TEXT ELSE '0' END, \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER::TEXT ELSE '0' END \
                    ORDER BY 1;"

        if context.get('documento')=='con_balance':
            name=''
            for per in obj_period.browse(cr, uid, [context.get('period_id')]):
                name=per.name[:2]
                fecha1=per.date_start
                fecha2=per.date_stop
            name1 = name + " Contabilidad.txt"
            query = "CREATE TEMP TABLE TEMP_BALANCE1 AS \
                    SELECT	LEFT(A.CODE,3)::INTEGER NIV1, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END NIV2, \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END NIV3, \
	                        COALESCE(SUM(L.DEBIT),0.00) DEU_INI, COALESCE(SUM(L.CREDIT),0.00) ACR_INI, 0.00 DEU_FLU, 0.00 ACR_FLU \
                    FROM	ACCOUNT_MOVE_LINE L \
                    INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                    WHERE	L.STATE='valid' AND L.DATE < '"+fecha1+"' \
                    GROUP BY LEFT(A.CODE,3)::INTEGER, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END, \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END \
                    UNION ALL \
                    SELECT	LEFT(A.CODE,3)::INTEGER NIV1, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END NIV2, \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END NIV3, \
	                        0.00 DEU_INI, 0.00 ACR_INI, COALESCE(SUM(L.DEBIT),0.00) DEU_FLU, COALESCE(SUM(L.CREDIT),0.00) ACR_FLU \
                    FROM	ACCOUNT_MOVE_LINE L \
                    INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                    WHERE	L.STATE='valid' AND L.DATE BETWEEN '"+fecha1+"' AND '"+fecha2+"' \
                    GROUP BY LEFT(A.CODE,3)::INTEGER, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END, \
	                        CASE WHEN LENGTH(A.CODE)>7 THEN SUBSTRING(A.CODE,8,2)::INTEGER ELSE 0 END; \
                    SELECT	DATE_PART('month','"+fecha2+"'::DATE)::INTEGER::TEXT||'|'||NIV1::TEXT||'|'||NIV2||'|'||NIV3::TEXT||'|'||SUM(DEU_INI)::TEXT||'|'|| \
	                        SUM(ACR_INI)::TEXT||'|'||SUM(DEU_FLU)::TEXT||'|'||SUM(ACR_FLU)::TEXT||'|'||SUM(DEU_INI+DEU_FLU)::TEXT||'|'||SUM(ACR_INI+ACR_FLU)::TEXT||'|'|| \
	                        CASE WHEN SUM(DEU_INI+DEU_FLU)>SUM(ACR_INI+ACR_FLU) THEN SUM(DEU_INI+DEU_FLU)-SUM(ACR_INI+ACR_FLU) ELSE 0.00 END::TEXT||'|'|| \
	                        CASE WHEN SUM(ACR_INI+ACR_FLU)>SUM(DEU_INI+DEU_FLU) THEN SUM(ACR_INI+ACR_FLU)-SUM(DEU_INI+DEU_FLU) ELSE 0.00 END::TEXT \
                    FROM	TEMP_BALANCE1 \
                    GROUP BY NIV1, NIV2, NIV3;"

        if context.get('documento')=='con_transfer':
            name=''
            for per in obj_period.browse(cr, uid, [context.get('period_id')]):
                name=per.name[:2]
                fecha1=per.date_start
                fecha2=per.date_stop
            name1 = name + " Transferencias.txt"
            query = "CREATE TEMP TABLE TEMP_TRANSFER1 AS \
                    SELECT	LEFT(A.CODE,3)::INTEGER NIV1, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END NIV2, \
	                        P.IDENTIFIER PARTNER, COALESCE(SUM(L.DEBIT),0.00) DEU_FLU, COALESCE(SUM(L.CREDIT),0.00) ACR_FLU \
                    FROM	ACCOUNT_MOVE_LINE L \
                    INNER	JOIN ACCOUNT_ACCOUNT A ON (L.ACCOUNT_ID=A.ID) \
                    INNER	JOIN RES_PARTNER P ON (P.ID=L.PARTNER_ID) \
                    WHERE	L.STATE='valid' AND L.DATE BETWEEN '"+fecha1+"' AND '"+fecha2+"' \
                            AND LENGTH(A.CODE)>=6 AND LEFT(A.CODE,6) IN ('113.18','113.28','213.58','213.78','213.88') \
	                        AND (P.IDENTIFIER='9999999999996' OR P.IDENTIFIER LIKE '__6%') \
                    GROUP BY LEFT(A.CODE,3)::INTEGER, CASE WHEN LENGTH(A.CODE)>4 THEN SUBSTRING(A.CODE,5,2)::INTEGER ELSE 0 END, P.IDENTIFIER; \
                    SELECT	DATE_PART('month','"+fecha2+"'::DATE)::INTEGER::TEXT||'|'||NIV1::TEXT||'|'||NIV2||'|0|'|| \
	                        CASE WHEN NIV1=113 THEN PARTNER ELSE (SELECT IDENTIFIER FROM RES_PARTNER WHERE ID=1) END||'|'|| \
	                        CASE WHEN NIV1=213 THEN PARTNER ELSE (SELECT IDENTIFIER FROM RES_PARTNER WHERE ID=1) END||'|'|| \
	                        DEU_FLU::TEXT||'|'||ACR_FLU::TEXT||'|0' \
                    FROM	TEMP_TRANSFER1 \
                    ORDER BY 1;"

        if context.get('documento')=='pre_inicial':
            name1 = "00 Presupuesto.txt"
            query = "SELECT	'1|I|'||LEFT(BP.CODE,2)::INTEGER::TEXT||'|'||SUBSTRING(BP.CODE,3,2)::INTEGER::TEXT||'|'|| \
                            SUBSTRING(BP.CODE,5,2)::INTEGER::TEXT||'|'||SUM(BL.PLANNED_AMOUNT)::TEXT, 1 ORDEN \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    WHERE	B.FY_ID=" + str(context.get('fy_id')) + " AND B.BUDGET_TYPE = 'I' \
                    GROUP BY LEFT(BP.CODE,2),SUBSTRING(BP.CODE,3,2),SUBSTRING(BP.CODE,5,2) \
                    UNION \
                    SELECT	'1|G|'||LEFT(BP.CODE,2)::INTEGER::TEXT||'|'||SUBSTRING(BP.CODE,3,2)::INTEGER::TEXT||'|'|| \
                            SUBSTRING(BP.CODE,5,2)::INTEGER::TEXT||'|000|'||BE.CODE||'|'||SUM(BL.PLANNED_AMOUNT)::TEXT, 2 ORDEN \
                    FROM	CROSSOVERED_BUDGET B  \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    INNER	JOIN CROSSOVERED_BUDGET_EXPENSE BE ON (BE.ID=BL.BUDGET_EXPENSE_ID) \
                    WHERE	B.FY_ID=" + str(context.get('fy_id')) + " AND B.BUDGET_TYPE = 'G' \
                    GROUP BY LEFT(BP.CODE,2),SUBSTRING(BP.CODE,3,2),SUBSTRING(BP.CODE,5,2), BE.CODE \
                    ORDER BY 2,1;"

        if context.get('documento')=='pre_cedula':
            name=''
            for per in obj_period.browse(cr, uid, [context.get('period_id')]):
                name=per.name[:2]
                fecha=per.date_stop
            name1 = name + " Presupuesto.txt"

            query = "CREATE TEMP TABLE TEMP_INGRESOS AS \
                    SELECT	BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    +COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
	                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) DEVENGADO, \
	                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
	                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) RECAUDADO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    WHERE	B.FY_ID = " + str(context.get('fy_id')) + " AND B.BUDGET_TYPE='I' \
                    GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    CREATE TEMP TABLE TEMP_GASTOS AS \
                    SELECT	BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, BE.CODE ORIENTACION, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    +COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE((SELECT SUM(DL.COMMITED_AMOUNT) FROM CROSSOVERED_BUDGET_DOC_LINE DL WHERE DL.BUDGET_LINE_ID=BL.ID  AND DL.STATE='commited' \
	                    AND BUDGET_DOC_ID IN (SELECT ID FROM CROSSOVERED_BUDGET_DOC D WHERE D.STATE='commited' AND DATE_COMMITED<='"+fecha+"')),0.00) COMPROMETIDO, \
	                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
	                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) DEVENGADO, \
	                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
	                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) PAGADO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    INNER	JOIN CROSSOVERED_BUDGET_EXPENSE BE ON (BE.ID=BL.BUDGET_EXPENSE_ID) \
                    WHERE	B.FY_ID = " + str(context.get('fy_id')) + " AND B.BUDGET_TYPE='G' \
                    GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT, BE.CODE; \
                    SELECT	DATE_PART('month','"+fecha+"'::DATE)::INTEGER::TEXT||'|I|'|| \
	                    SUBSTRING(PARTIDA,1,2)::INTEGER::TEXT||'|'||SUBSTRING(PARTIDA,3,2)::INTEGER::TEXT||'|'||SUBSTRING(PARTIDA,5,2)::INTEGER::TEXT||'|'|| \
	                    SUM(INICIAL)||'|'||SUM(REFORMA)||'|'||SUM(INICIAL+REFORMA)||'|'||SUM(DEVENGADO)||'|'||SUM(RECAUDADO)||'|'||SUM(INICIAL+REFORMA-DEVENGADO), 1 ORDEN \
                    FROM	TEMP_INGRESOS \
                    GROUP BY SUBSTRING(PARTIDA,1,2),SUBSTRING(PARTIDA,3,2),SUBSTRING(PARTIDA,5,2) \
                    UNION \
                    SELECT	DATE_PART('month','"+fecha+"'::DATE)::INTEGER::TEXT||'|G|'|| \
	                    SUBSTRING(PARTIDA,1,2)::INTEGER::TEXT||'|'||SUBSTRING(PARTIDA,3,2)::INTEGER::TEXT||'|'||SUBSTRING(PARTIDA,5,2)::INTEGER::TEXT||'|000|'||ORIENTACION||'|'|| \
	                    SUM(INICIAL)||'|'||SUM(REFORMA)||'|'||SUM(INICIAL+REFORMA)||'|'||SUM(COMPROMETIDO)||'|'||SUM(DEVENGADO)||'|'||SUM(PAGADO)||'|'|| \
	                    SUM(INICIAL+REFORMA-COMPROMETIDO)||'|'||SUM(INICIAL+REFORMA-DEVENGADO), 2 ORDEN \
                    FROM	TEMP_GASTOS \
                    GROUP BY SUBSTRING(PARTIDA,1,2),SUBSTRING(PARTIDA,3,2),SUBSTRING(PARTIDA,5,2), ORIENTACION \
                    ORDER BY 2,1;"

        cr.execute(query)
        for resultado in cr.fetchall():
            buf1.write(resultado[0]+'\r\n')

        out1 = base64.encodestring(buf1.getvalue())

        buf1.close()

        self.write(cr, uid, ids, {'datas': out1, 'datas_fname': name1})


        return {
            'type': 'ir.actions.act_window',
            'name': 'Archivos Planos E-Sigef',
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wizard.esigef',
            'res_id': wiz.id,
            'nodestroy': True,
            'target': 'new',
            'context': context,
            }


WizardEsigef()


