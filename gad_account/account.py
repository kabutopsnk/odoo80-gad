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


class gad_account(osv.osv):

    _inherit = 'account.account'

    _columns = {
        'budget_debit_id': fields.many2one('account.budget.post', u'Asociación Presupuestaria Débito'),
        'budget_credit_id': fields.many2one('account.budget.post', u'Asociación Presupuestaria Crédito'),
        }

gad_account()

"""class account_move_budget(osv.osv):
    _name = 'account.move.budget'
    _description = u'Relación entre el asiento contable y el presupuesto'
    
    _columns = {
                'invoice_id': fields.many2one('account.invoice', u'Factura', ondelete='cascade'),
                'move_id': fields.many2one('account.move', u'Asiento Contable', ondelete='cascade'),
                #'budget_doc_line': fields.many2one('crossovered.budget.doc.line', u'Linea Presupuesto', ondelete='cascade'),
                'budget_doc_line': fields.many2one('crossovered.budget.doc.line', u'Linea Presupuesto', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'budget_line_id': fields.related('budget_doc_line', 'budget_line_id', type='many2one', relation='crossovered.budget.lines', store=True, string=u'Linea Planificación Presupuesto', readonly=True),
                'accrued_amount': fields.float(u'Valor Devengado', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'paid_amount': fields.float(u'Valor Pagado', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'state': fields.related('move_id', 'state', type='selection', selection=[('draft','Sin Contabilizar'), ('posted','Contabilizado'),], string=u'Estado', readonly=True)
                }
    
    _order = "move_id desc, state"
    #valores por defecto
    _defaults = {
                 'accrued_amount': 0,
                 'paid_amount': 0,
                 'state': 'draft'
                 }
    
    _sql_constraints = [
                        ('unique_budget_invoice', 'unique(invoice_id,budget_line_id)', u'Solo puede registrar 1 vez la linea de presupuesto en la factura actual.')
                        ]
    
account_move_budget()"""

class gad_account_move(osv.osv):

    _inherit = 'account.move'

    _columns = {
        #'budget_doc_id': fields.many2one('crossovered.budget.doc', u'Documento Presupuestario', readonly=True),
        'budget_doc_id': fields.many2one('crossovered.budget.doc', u'Documento Presupuestario', states={'posted':[('readonly',True)]}),
        #'move_budget': fields.one2many('account.move.budget', 'move_id', u'Detalle presupuestario', states={'posted':[('readonly',True)]}),
        'move_budget': fields.one2many('account.invoice.budget', 'move_id', u'Detalle presupuestario', states={'posted':[('readonly',True)]}),
        }

gad_account_move()

class gad_account_move_line(osv.osv):

    _inherit = 'account.move.line'
    
    _columns = {
                'conciliacion_bancaria': fields.boolean(u'Conciliado?'),
                'conciliacion_referencia': fields.char(u'Referencia Conciliación', size=50),
                }
    
    _defaults = {
                 'conciliacion_bancaria': False,
                 'conciliacion_referencia': '',
                 }

    _sql_constraints = [
        ('credit_debit1', 'CHECK (credit*debit=0)',  '/nValor incorrecto de crédito o débito en el registro contable !'),
        ('credit_debit2', 'CHECK (1=1)', '/nValor incorrecto de crédito o débito en el registro contable !'), # CHECK (credit+debit>=0)
    ]

gad_account_move_line()

"""class gad_account_bank_conciliacion(osv.osv):
    _name = 'account.bank.conciliacion'
    _description = u"Conciliación Bancaria"
    
    _columns = {
                'name': fields.char(u'Descripción', required=True),
                'period_id': fields.many2one('account.period', u'Periodo', required=True),
                'account_id': fields.many2one('account.account', u'Cuenta de Banco', required=True),
                'line_ids': fields.one2many('account.bank.conciliacion.line', 'head_id', u'Detalle'),
                }
    
    
gad_account_bank_conciliacion()

class gad_account_bank_conciliacion_line(osv.osv):
    _name = 'account.bank.conciliacion.line'
    _description = u"Detalle de Conciliación Bancaria"
    
    _columns = {
                'head_id': fields.many2one('account.bank.conciliacion', u'Conciliacion bancaria', ondelete='cascade'),
                'move_id': fields.many2one('account.move.line', u'Asiento Contable', required=True),
                'debit': fields.float(u'Débito'),
                'credit': fields.float(u'Crédito'),
                }
    
    
gad_account_bank_conciliacion_line()"""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
