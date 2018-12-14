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

from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import except_orm, Warning, RedirectWarning


class gad_res_partner(models.Model):

    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, uid, [('identifier', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _check_cedula(self, identificador):
        if len(identificador) == 13 and not identificador[10:13] == '001':
            return False
        else:
            if len(identificador) < 10:
                return False
        coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        cedula = identificador[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val-9 or val
        result = 10 - ((suma % 10) != 0 and suma%10 or 10)
        if result == int(identificador[9:10]):
            return True
        else:
            return False

    def _check_ruc(self, partner):
        ruc = partner.identifier
        if not len(ruc) == 13:
            return False
        if ruc[2:3] == '9':
            coef = [4, 3, 2, 7, 6, 5, 4, 3, 2, 0]
            coef.reverse()
            verificador = int(ruc[9:10])
        elif ruc[2:3] == '6':
            coef = [3, 2, 7, 6, 5, 4, 3, 2, 0, 0]
            coef.reverse()
            verificador = int(ruc[8:9])
        else:
            raise osv.except_osv('Error', 'Cambie el tipo de persona')
        suma = 0
        for c in ruc[:10]:
            suma += int(c) * coef.pop()
        result = 11 - (suma > 0 and suma % 11 or 11)
        if result == verificador:
            return True
        else:
            return False

    def _check_identifier(self, cr, uid, ids):
        partners = self.browse(cr, uid, ids)
        for partner in partners:
            if not partner.identifier:
                return True
            if partner.type_identifier == 'pasaporte':
                return True
            elif partner.type_identifier == 'ruc':
                if not len(partner.identifier) == 13:
                    return False
                if partner.type_person == '9':
                    return self._check_ruc(partner)
                else:
                    return self._check_cedula(partner.identifier)
            elif partner.type_identifier == 'cedula':
                if not len(partner.identifier) == 10:
                    return False
                else:
                    return self._check_cedula(partner.identifier)
    
    #def _check_employee(self, cr, uid, ids):
    #    if uid==1:
    #        return True
    #    for partner in self.browse(cr, uid, ids):
    #        if uid!=1 and not partner.employee_id:
    #            return False

    identifier = fields.Char(u'Cedula/ RUC', size=13, required=True, help=u'Identificación o Registro Unico de Contribuyentes')
    type_identifier = fields.Selection([('cedula', 'CEDULA'),('ruc', 'RUC'),('pasaporte', 'PASAPORTE')], u'Tipo ID', required=True)
    type_person = fields.Selection([('6', 'Persona Natural'),('9', 'Persona Juridica')], string=u'Persona', required=True, default='9' )
    inscrito_en = fields.Selection([('ministerio', 'Ministerio'),('superintendencia', 'Superintendencia')], string=u'Inscrito en')
    lugar_inscripcion = fields.Char(u'Lugar inscripción', size=100)
    numero_inscripcion = fields.Char(u'Número acuerdo/registro', size=100)
    fecha_inscripcion = fields.Date(u'Fecha inscripción')
    cedula_rl = fields.Char(u'Cédula representante legal', size=13)
    nombre_rl = fields.Char(u'Nombre representante legal', size=100)
    date_death = fields.Date(u'Fecha de Defunción')
    date_birth = fields.Date(u'Fecha de Nacimiento')
    nacionalidad = fields.Many2one('res.country', u'Nacionalidad')
    personeria_juridica = fields.Selection([('publico', u'Público'),('privado', u'Privado')], u'Personería Jurídica')
    #is_company = fields.Boolean(default=True)
    #employee_id = fields.Many2one('hr.employee', u'Empleado')
    estado_civil = fields.Many2one('hr.marital.status', u'Estado Civil')
    nombre_conyuge = fields.Many2one('res.partner', u'Cónyuge')
    separacion_bienes = fields.Boolean(u'Separación de Bienes')

    _constraints = [
        (_check_identifier, 'Error en su Cedula/RUC/Pasaporte', ['identifier']),
        #(_check_employee, 'Error de usuario, TODO usuario debe estar relacionado a un EMPLEADO', ['employee_id'])
        ]

    _sql_constraints = [
        ('partner_unique', 'unique(identifier,type_identifier,type_person,company_id)', u'El identificador es único.'),
        ]

gad_res_partner()

class gad_res_company(models.Model):
    _inherit = 'res.company'

    accountant_identifier = fields.Char(u'RUC del Contador', size=13)
    cedula_rl = fields.Char(u'Cédula Representante Legal', size=10)
    codigo_ce = fields.Integer(u'Código Contribuyente Especial')
    #tradename = fields.Char(u'Nombre Comercial', size=300)
    canton_id = fields.Many2one('res.country.state.canton', u'Cantón')
    
gad_res_company()
