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
from datetime import datetime

from openerp import models, fields, api
from openerp.exceptions import Warning as UserError


class AccountAtsDoc(models.Model):
    _name = 'account.ats.doc'
    _description = 'Tipos Comprobantes Autorizados'

    code = fields.Char(u'Código', size=2, required=True)
    name = fields.Char(u'Tipo Comprobante', size=64, required=True)


class AccountAtsSustento(models.Model):
    _name = 'account.ats.sustento'
    _description = 'Sustento del Comprobante'

    def name_get(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cursor, uid, ids, context=context)
        for record in reads:
            name = '%s - %s' % (record.code, record.type)
            res.append((record.id, name))
        return res

    _rec_name = 'type'

    code = fields.Char(u'Código', size=2, required=True)
    type = fields.Char(u'Tipo de Sustento', size=64, required=True)


class AccountAuthorisation(models.Model):

    _name = 'account.authorisation'
    _description = 'Authorisation for Accounting Documents'
    _order = 'expiration_date desc'

    def name_get(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        for record in self.browse(cursor, uid, ids, context=context):
            name = u'%s (%s-%s)' % (
                record.type_id.name,
                record.num_start,
                record.num_end
            )
            res.append((record.id, name))
        return res

    @api.one
    def _check_active(self):
        """
        Check the due_date to give the value active field
        """
        now = datetime.strptime(time.strftime("%Y-%m-%d"), '%Y-%m-%d')
        due_date = datetime.strptime(self.expiration_date, '%Y-%m-%d')
        self.active = now < due_date

    def _get_type(self):
        return self._context.get('type', 'in_invoice')  # pylint: disable=E1101

    def _get_in_type(self):
        return self._context.get('in_type', 'externo')

    def _get_partner(self):
        partner = self.env.user.company_id.partner_id
        if self._context.get('partner_id'):
            partner = self._context.get('partner_id')
        return partner

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        partner_id = self.env.user.company_id.partner_id.id
        if values.get('partner_id', False) and values['partner_id'] == partner_id:  # noqa
            name_type = '{0}_{1}'.format(values['name'], values['type_id'])
            code_obj = self.env['ir.sequence.type']
            seq_obj = self.env['ir.sequence']
            code_data = {
                'code': '%s.%s.%s' % (name_type, values['serie_entidad'], values['serie_emision']),  # noqa
                'name': name_type
                }
            code = code_obj.create(code_data)
            sequence_data = {
                'name': name_type,
                'padding': 9,
                'number_next': values['num_start'],
                'code': code.code
                }
            seq = seq_obj.create(sequence_data)
            values.update({'sequence_id': seq.id})
        return super(AccountAuthorisation, self).create(values)

    @api.multi
    def unlink(self):
        journal = self.env['account.journal']
        res = journal.search(['|', ('auth_id', '=', self.id), ('auth_ret_id', '=', self.id)])  # noqa
        if res:
            raise UserError(
                'Alerta',
                'Esta autorización esta relacionada a un diario.'
            )
        return super(AccountAuthorisation, self).unlink()

    name = fields.Char(u'Num. de Autorización', size=128)
    serie_entidad = fields.Char(u'Serie Entidad', size=3, required=True)
    serie_emision = fields.Char(u'Serie Emision', size=3, required=True)
    num_start = fields.Integer(u'Desde', required=True)
    num_end = fields.Integer(u'Hasta', required=True)
    is_electronic = fields.Boolean(u'Documento Electrónico ?')
    expiration_date = fields.Date(u'Fecha de Vencimiento', required=True)
    active = fields.Boolean(
        compute='_check_active',
        string=u'Activo',
        store=True,
        default=True
        )
    in_type = fields.Selection(
        [('interno', 'Internas'),
         ('externo', 'Externas')],
        string=u'Tipo Interno',
        readonly=True,
        change_default=True,
        default=_get_in_type
        )
    type_id = fields.Many2one(
        'account.ats.doc',
        u'Tipo de Comprobante',
        required=True
        )
    partner_id = fields.Many2one(
        'res.partner',
        u'Empresa',
        required=True,
        default=_get_partner
        )
    sequence_id = fields.Many2one(
        'ir.sequence',
        u'Secuencia',
        help='Secuencia Alfanumerica para el documento, se debe registrar cuando pertenece a la compañia',  # noqa
        ondelete='cascade'
        )

    def set_authorisation(cr, uid, ids, context):
        return True

    _sql_constraints = [
        ('number_unique',
         'unique(name,partner_id,serie_entidad,serie_emision,type_id)',
         u'La relación de autorización, serie entidad, serie emisor y tipo, debe ser única.'),  # noqa
        ]

    def is_valid_number(self, cursor, uid, id, number):
        """
        Metodo que verifica si @number esta en el rango
        de [@num_start,@num_end]
        """
        obj = self.browse(cursor, uid, id)
        if obj.num_start <= number <= obj.num_end:
            return True
        return False


class ResPartner(models.Model):
    _inherit = 'res.partner'

    authorisation_ids = fields.One2many(
        'account.authorisation',
        'partner_id',
        u'Autorizaciones'
        )


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    auth_id = fields.Many2one(
        'account.authorisation',
        help=u'Autorización utilizada para Facturas y Liquidaciones de Compra',
        string=u'Autorización',
        domain=[('in_type', '=', 'interno')]
        )
    auth_ret_id = fields.Many2one(
        'account.authorisation',
        domain=[('in_type', '=', 'interno')],
        string=u'Autorización de Ret.',
        help=u'Autorizacion utilizada para Retenciones, facturas y liquidaciones'  # noqa
        )


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res1 = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice,
            payment_term, partner_bank_id,
            company_id
        )
        if 'reference_type' in res1['value']:
            res1['value'].pop('reference_type')
        res = self.env['account.authorisation'].search(
            [('partner_id', '=', partner_id),
             ('in_type', '=', 'externo')],
            limit=1
        )
        if res:
            res1['value']['auth_inv_id'] = res[0]
        return res1

    auth_inv_id = fields.Many2one(
        'account.authorisation',
        string=u'Establecimiento',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help=u'Autorizacion para documento recibido',
        copy=False
    )

    @api.onchange('auth_inv_id')
    def onchange_auth_inv_id(self):
        self.reference = self.auth_inv_id and self.auth_inv_id.name or ""

    @api.onchange(
        'supplier_invoice_number',
        'auth_inv_id'
    )
    def check_invoice_supplier(self):
        if self.supplier_invoice_number:
            res = self.auth_inv_id.is_valid_number(self.supplier_invoice_number)  # noqa
            if res:
                self.supplier_invoice_number = self.supplier_invoice_number.zfill(9)  # noqa
            else:
                self.supplier_invoice_number = ''
                return {
                    'warning': {
                        'title': 'Error',
                        'message': u'El número {0} no es válido'.format(self.supplier_invoice_number)  # noqa
                    }
                }
