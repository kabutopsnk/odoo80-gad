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


"""class ec_res_country(osv.osv):
    _inherit = 'res.country'
    _columns = {
        'active': fields.boolean(u'Activo'),
        #'code_phone': fields.char(u'Código Telefónico', size=5),
    }
    
    _defaults = {
                'active': True
                }
    
    _order = 'code'

ec_res_country()"""


class l10n_ec_res_country_state_canton(osv.osv):
    _name = 'res.country.state.canton'
    _description = 'Ciudades relacionados a provincias'
    _columns = {
        'country_id': fields.many2one('res.country', u'País', required=True),
        'state_id': fields.many2one('res.country.state', u'Provincia', required=True),
        'name': fields.char(u'Cantón', size=64, required=True),
        'code': fields.char(u'Codigo', size=10, required=True),
    }
    _order = 'code'

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
            name = record.state_id.name + " / " + record.name
            res.append((record.id, name))
        return res

l10n_ec_res_country_state_canton()

class resCountryStateParish(osv.osv):
    _name = 'res.country.state.parish'
    _description = u'Parroquias relacionadas a Cantones'
    
    _columns = dict(
                    country_id =  fields.many2one('res.country', u'País', required=True),
                    state_id =  fields.many2one('res.country.state', u'Provincia', required=True),
                    canton_id = fields.many2one('res.country.state.canton', u'Cantón', required=True),
                    name =  fields.char(u'Parroquia', size=64, required=True),
                    code = fields.char(u'Código',size=10),
                    )
    _order = 'state_id asc, canton_id asc, name asc'
    
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
            name = record.state_id.name + " / " + record.canton_id.name + " / " + record.name
            res.append((record.id, name))
        return res

resCountryStateParish()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
