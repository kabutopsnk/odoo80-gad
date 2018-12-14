
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
import openerp.addons.decimal_precision as dp


class account_crossovered_budget_lines(osv.osv):
    _inherit = 'crossovered.budget.lines'
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        obj_post = self.pool.get("account.budget.post")
        ids_budget = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_budget))
        #print args
        if name:
            #print 'code | ' + str(operator) + ' | ' + name
            ids_name = obj_post.search(cr, uid, [('code', operator, name)], limit=limit, context=context)
            #print ids_name
            ids_budget = self.search(cr, uid, [('general_budget_id', 'in', ids_name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_budget))
            ids_name = obj_post.search(cr, uid, [('name', operator, name)], limit=limit, context=context)
            #print ids_name
            ids_budget = self.search(cr, uid, [('general_budget_id', 'in', ids_name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_budget))
        return self.name_get(cr, uid, ids, context=context)
    
    def _calcular_valores_contables(self, cr, uid, ids, fields, arg, context):
        res = {}
        obj_invbudget = self.pool.get('account.invoice.budget')

        x_comprometer=0.00
        x_devengar=0.00
        x_pagar_recaudar=0.00
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {
                           'accrued_amount': 0.00,
                           'paid_amount': 0.00,
                           }
            invbudget_ids = obj_invbudget.search(cr, uid, [('budget_line_id','=',obj.id)])
            for linea in obj_invbudget.browse(cr, uid, invbudget_ids, context=context):
                if linea.state in ('open','paid'):
                    res[obj.id]['accrued_amount'] += linea.amount
                if linea.state == 'paid':
                    res[obj.id]['paid_amount'] += linea.amount
                if not linea.state and linea.state_move == 'posted':
                    res[obj.id]['accrued_amount'] += linea.amount
                    res[obj.id]['paid_amount'] += linea.amount
            #SALDOS
            res[obj.id]['x_comprometer_amount']=obj.coded_amount-obj.commited_amount
            res[obj.id]['x_devengar_amount']=obj.coded_amount-res[obj.id]['accrued_amount']
            res[obj.id]['x_pag_rec_amount']=obj.coded_amount-res[obj.id]['paid_amount']
        #print res
        return res
    
    def _get_invoice_budget(self, cr, uid, ids, context):
        result = {}
        for budget in self.pool.get('account.invoice.budget').browse(cr, uid, ids, context):
            if budget.state in ('open','paid'):
                result[budget.budget_line_id.id] = True
        print result.keys()
        return result.keys()

    STORE_VAR = {
                 'account.invoice.budget': (_get_invoice_budget, ['amount','budget_doc_line','state'], 10),
                 }
    
    _columns = {
                'accrued_amount':fields.function(_calcular_valores_contables, string=u'Devengado', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
                'paid_amount':fields.function(_calcular_valores_contables, string=u'Pagado', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
                'x_comprometer_amount':fields.function(_calcular_valores_contables, string=u'Saldo X Comprometer', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
                'x_devengar_amount':fields.function(_calcular_valores_contables, string=u'Saldo X Devengar', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
                'x_pag_rec_amount':fields.function(_calcular_valores_contables, string=u'Saldo x Pagar/Recaudar', store=False, method=True, multi='account_budget_lines', digits_compute=dp.get_precision('Account')),
        }

account_crossovered_budget_lines()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
