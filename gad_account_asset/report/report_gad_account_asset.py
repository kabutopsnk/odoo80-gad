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


class account_asset_activo(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_asset_activo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_account_asset_activo(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_activo'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_activo'
    _wrapped_report_class = account_asset_activo



class account_asset_transfer(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_asset_transfer, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_account_asset_transfer(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_transfer'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_transfer'
    _wrapped_report_class = account_asset_transfer



class account_asset_baja(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_asset_baja, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_account_asset_baja(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_baja'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_baja'
    _wrapped_report_class = account_asset_baja



class account_asset_ingreso(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_asset_ingreso, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

class wrapped_account_asset_ingreso(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_ingreso'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_ingreso'
    _wrapped_report_class = account_asset_ingreso



class account_asset_tarjeta(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_asset_tarjeta, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

class wrapped_account_asset_tarjeta(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_tarjeta'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_tarjeta'
    _wrapped_report_class = account_asset_tarjeta



class account_asset_certificado_no(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_asset_certificado_no, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

class wrapped_account_asset_certificado_no(osv.AbstractModel):
    _name = 'report.gad_account_asset.account_asset_certificado_no'
    _inherit = 'report.abstract_report'
    _template = 'gad_account_asset.account_asset_certificado_no'
    _wrapped_report_class = account_asset_certificado_no


#class account_asset_ingreso(report_sxw.rml_parse):
#    def __init__(self, cr, uid, name, context):
#        super(account_asset_ingreso, self).__init__(cr, uid, name, context=context)
#        self.localcontext.update({
#            'time': time,
#            'cr':cr,
#            'uid': uid,
#        })
      
#class wrapped_account_asset_ingreso(osv.AbstractModel):
#    _name = 'report.gad_account_asset.account_asset_ingreso'
#    _inherit = 'report.abstract_report'
#    _template = 'gad_account_asset.account_asset_ingreso'
#    _wrapped_report_class = account_asset_ingreso



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
