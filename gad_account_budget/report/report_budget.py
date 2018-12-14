# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>).
#    Application developed by: Patricio Argudo C.
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
from openerp.report import report_sxw
from openerp.osv import osv


class budget_doc(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(budget_doc, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_budget_doc(osv.AbstractModel):
    _name = 'report.gad_account_budget.budget_doc'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.budget_doc'
    _wrapped_report_class = budget_doc




class budget_certificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(budget_certificate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_budget_certificate(osv.AbstractModel):
    _name = 'report.gad_account_budget.budget_certificate'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.budget_certificate'
    _wrapped_report_class = budget_certificate



class budget_reform(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(budget_reform, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_budget_reform(osv.AbstractModel):
    _name = 'report.gad_account_budget.budget_reform'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.budget_reform'
    _wrapped_report_class = budget_reform



class cedula_ingresos(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cedula_ingresos, self).__init__(cr, uid, name, context=context)

        self.budget_id=context['budget_id']
        self.budget_name=context['budget_name']
        self.niveles=context['niveles']
        self.fecha=context['fecha']

        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'obtener_datos': self.obtener_datos
        })

    def obtener_datos(self):
        data=[]
        query=''
        fecha = self.fecha

        if self.niveles:
            query = "CREATE TEMP TABLE TEMP_INGRESOS AS \
                    SELECT	BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    + COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
	                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) DEVENGADO, \
	                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
	                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) RECAUDADO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'1' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'2' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'3' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'4' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'999' NIVEL \
                    FROM	TEMP_INGRESOS \
                    ORDER BY 1;"
        else:
            query = "CREATE TEMP TABLE TEMP_INGRESOS AS \
                    SELECT	BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    + COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE(ROUND((SELECT SUM(IB1.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB1 WHERE IB1.BUDGET_LINE_ID=BL.ID \
	                    AND IB1.INVOICE_ID IN (SELECT I1.ID FROM ACCOUNT_INVOICE I1 WHERE I1.STATE IN ('open','paid') AND I1.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) DEVENGADO, \
	                    COALESCE(ROUND((SELECT SUM(IB2.AMOUNT) FROM ACCOUNT_INVOICE_BUDGET IB2 WHERE IB2.BUDGET_LINE_ID=BL.ID \
	                    AND IB2.INVOICE_ID IN (SELECT I2.ID FROM ACCOUNT_INVOICE I2 WHERE I2.STATE='paid' AND I2.DATE_INVOICE<='"+fecha+"'))::NUMERIC,2),0.00) RECAUDADO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'4' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, \
                        ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(RECAUDADO)::NUMERIC,2),'999G999G999D99')) RECAUDADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-RECAUDADO)::NUMERIC,2),'999G999G999D99')) X_RECAUDAR,'999' NIVEL \
                    FROM	TEMP_INGRESOS \
                    ORDER BY 1;"

        self.cr.execute(query)

        for resultado in self.cr.fetchall():
            data.append(resultado)

        return data
      
class wrapped_cedula_ingresos(osv.AbstractModel):
    _name = 'report.gad_account_budget.cedula_ingresos'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.cedula_ingresos'
    _wrapped_report_class = cedula_ingresos




class cedula_gastos(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cedula_gastos, self).__init__(cr, uid, name, context=context)

        self.budget_id=context['budget_id']
        self.budget_name=context['budget_name']
        self.niveles=context['niveles']
        self.fecha=context['fecha']

        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'obtener_datos': self.obtener_datos
        })

    def obtener_datos(self):
        data=[]
        query=''
        fecha = self.fecha

        if self.niveles:
            query=  "CREATE TEMP TABLE TEMP_GASTOS AS \
                    SELECT	EST.ID AREA, PRG.ID PROGRAMA, BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
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
                    INNER	JOIN PROJECT_TASK T ON (T.ID=BL.TASK_ID) \
                    INNER	JOIN PROJECT_PROJECT P ON (P.ID=T.PROJECT_ID) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=P.ESTRATEGY_ID) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=P.PROGRAM_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY EST.ID, PRG.ID, BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	EST.SEQUENCE::TEXT, EST.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '10' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    GROUP BY EST.SEQUENCE::TEXT, EST.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '100' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '1' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '2' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '3' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '4' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '999' NIVEL \
                    FROM	TEMP_GASTOS \
                    ORDER BY 1;"
        else:
            query="CREATE TEMP TABLE TEMP_GASTOS AS \
                    SELECT	EST.ID AREA, PRG.ID PROGRAMA, BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
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
                    INNER	JOIN PROJECT_TASK T ON (T.ID=BL.TASK_ID) \
                    INNER	JOIN PROJECT_PROJECT P ON (P.ID=T.PROJECT_ID) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=P.ESTRATEGY_ID) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=P.PROGRAM_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY EST.ID, PRG.ID, BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '4' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL),'999G999G999D99')) INICIAL, \
                        ltrim(to_char(SUM(REFORMA),'999G999G999D99')) REFORMA, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
	                    ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) COMPROMETIDO, ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) X_COMPROMETER, \
	                    ltrim(to_char(ROUND(SUM(DEVENGADO)::NUMERIC,2),'999G999G999D99')) DEVENGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-DEVENGADO)::NUMERIC,2),'999G999G999D99')) X_DEVENGAR, \
	                    ltrim(to_char(ROUND(SUM(PAGADO)::NUMERIC,2),'999G999G999D99')) PAGADO, ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-PAGADO)::NUMERIC,2),'999G999G999D99')) X_PAGAR, '999' NIVEL \
                    FROM	TEMP_GASTOS \
                    ORDER BY 1;"

        self.cr.execute(query)

        for resultado in self.cr.fetchall():
            data.append(resultado)

        return data
      
class wrapped_cedula_gastos(osv.AbstractModel):
    _name = 'report.gad_account_budget.cedula_gastos'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.cedula_gastos'
    _wrapped_report_class = cedula_gastos



class estado_ejecucion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(estado_ejecucion, self).__init__(cr, uid, name, context=context)

        self.budget_type=context['budget_type']
        self.budget_id=context['budget_id']
        self.budget_name=context['budget_name']
        self.fecha=context['fecha']

        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'obtener_datos': self.obtener_datos
        })

    def obtener_datos(self):
        data=[]
        query=''
        fecha = self.fecha

        if self.budget_type=='I':
            query = "CREATE TEMP TABLE TEMP_INGRESOS AS \
                    SELECT	BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    + COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE((SELECT SUM(DL.COMMITED_AMOUNT) FROM CROSSOVERED_BUDGET_DOC_LINE DL WHERE DL.BUDGET_LINE_ID=BL.ID  AND DL.STATE='commited' \
	                    AND BUDGET_DOC_ID IN (SELECT ID FROM CROSSOVERED_BUDGET_DOC D WHERE D.STATE='commited' AND DATE_COMMITED<='"+fecha+"')),0.00) COMPROMETIDO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
	                    ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '1' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
	                    ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '2' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
	                    ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '3' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO,  \
	                    ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '4' NIVEL \
                    FROM	TEMP_INGRESOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    GROUP BY BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(SUM(COMPROMETIDO),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(SUM(INICIAL+REFORMA-COMPROMETIDO),'999G999G999D99')) DIFERENCIA, '999' NIVEL \
                    FROM	TEMP_INGRESOS \
                    ORDER BY 1;"

        if self.budget_type=='G':
            query = "CREATE TEMP TABLE TEMP_GASTOS AS \
                    SELECT	EST.ID AREA, PRG.ID PROGRAMA, BL.ID BL_ID, BP.CODE PARTIDA, BL.PLANNED_AMOUNT INICIAL, \
	                    COALESCE((SELECT SUM(CASE WHEN RL1.TYPE_TRANSACTION='ampliacion' THEN RL1.AMOUNT ELSE RL1.AMOUNT*(-1) END) FROM crossovered_budget_REFORM_LINE RL1 \
	                    WHERE RL1.BUDGET1_ID=BL.ID AND RL1.STATE='done' AND RL1.BUDGET_REFORM_ID IN (SELECT R1.ID FROM CROSSOVERED_BUDGET_REFORM R1 WHERE R1.STATE='done' AND R1.FECHA<='"+fecha+"')),0.00) \
	                    +COALESCE((SELECT SUM(RL2.AMOUNT) FROM crossovered_budget_REFORM_LINE RL2 WHERE RL2.BUDGET2_ID=BL.ID AND RL2.STATE='done' AND RL2.TYPE_TRANSACTION='transferencia' \
	                    AND RL2.BUDGET_REFORM_ID IN (SELECT R2.ID FROM CROSSOVERED_BUDGET_REFORM R2 WHERE R2.STATE='done' AND R2.FECHA<='"+fecha+"')),0.00) REFORMA, \
	                    COALESCE((SELECT SUM(DL.COMMITED_AMOUNT) FROM CROSSOVERED_BUDGET_DOC_LINE DL WHERE DL.BUDGET_LINE_ID=BL.ID  AND DL.STATE='commited' \
	                    AND BUDGET_DOC_ID IN (SELECT ID FROM CROSSOVERED_BUDGET_DOC D WHERE D.STATE='commited' AND DATE_COMMITED<='"+fecha+"')),0.00) COMPROMETIDO \
                    FROM	CROSSOVERED_BUDGET B \
                    INNER	JOIN CROSSOVERED_BUDGET_LINES BL ON (BL.CROSSOVERED_BUDGET_ID=B.ID) \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.ID=BL.GENERAL_BUDGET_ID) \
                    INNER	JOIN PROJECT_TASK T ON (T.ID=BL.TASK_ID) \
                    INNER	JOIN PROJECT_PROJECT P ON (P.ID=T.PROJECT_ID) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=P.ESTRATEGY_ID) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=P.PROGRAM_ID) \
                    WHERE	B.ID = "+self.budget_id+" \
                    GROUP BY EST.ID, PRG.ID, BL.ID, BP.CODE, BL.PLANNED_AMOUNT; \
                    SELECT	EST.SEQUENCE::TEXT, EST.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '10' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    GROUP BY EST.SEQUENCE::TEXT, EST.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '100' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT, PRG.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '1' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,1)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '2' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,2)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '3' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=LEFT(PARTIDA,4)) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME, ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '4' NIVEL \
                    FROM	TEMP_GASTOS \
                    INNER	JOIN ACCOUNT_BUDGET_POST BP ON (BP.CODE=PARTIDA) \
                    INNER	JOIN PROJECT_ESTRATEGY EST ON (EST.ID=AREA) \
                    INNER	JOIN PROJECT_PROGRAM PRG ON (PRG.ID=PROGRAMA) \
                    GROUP BY EST.SEQUENCE::TEXT||PRG.SEQUENCE::TEXT||'.'||BP.CODE, BP.NAME \
                    UNION \
                    SELECT	'TOTAL:', '', ltrim(to_char(SUM(INICIAL+REFORMA),'999G999G999D99')) CODIFICADO, \
                        ltrim(to_char(ROUND(SUM(COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) EJECUTADO, \
                        ltrim(to_char(ROUND(SUM(INICIAL+REFORMA-COMPROMETIDO)::NUMERIC,2),'999G999G999D99')) DIFERENCIA, '999' NIVEL \
                    FROM	TEMP_GASTOS \
                    ORDER BY 1;"

        self.cr.execute(query)

        for resultado in self.cr.fetchall():
            data.append(resultado)

        return data
      
class wrapped_estado_ejecucion(osv.AbstractModel):
    _name = 'report.gad_account_budget.estado_ejecucion'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_budget.estado_ejecucion'
    _wrapped_report_class = estado_ejecucion



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
