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


class report_contrato_hoja_garantia(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_contrato_hoja_garantia, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
class wrapped_report_contrato_hoja_garantia(osv.AbstractModel):
    _name = 'report.gad_project.report_contrato_hoja_garantia'
    _inherit = 'report.abstract_report'
    _template = 'gad_project.report_contrato_hoja_garantia'
    _wrapped_report_class = report_contrato_hoja_garantia



class report_contrato_garantia_oficio_renovacion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(report_contrato_garantia_oficio_renovacion, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

class wrapped_report_contrato_garantia_oficio_renovacion(osv.AbstractModel):
    _name = 'report.gad_project.report_contrato_garantia_oficio_renovacion'
    _inherit = 'report.abstract_report'
    _template = 'gad_project.report_contrato_garantia_oficio_renovacion'
    _wrapped_report_class = report_contrato_garantia_oficio_renovacion



class report_contrato_garantia_oficio_ejecucion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(report_contrato_garantia_oficio_ejecucion, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

class wrapped_report_contrato_garantia_oficio_ejecucion(osv.AbstractModel):
    _name = 'report.gad_project.report_contrato_garantia_oficio_ejecucion'
    _inherit = 'report.abstract_report'
    _template = 'gad_project.report_contrato_garantia_oficio_ejecucion'
    _wrapped_report_class = report_contrato_garantia_oficio_ejecucion


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
