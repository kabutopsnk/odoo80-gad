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

import datetime
import calendar

def get_day(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.day

def get_month(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.month

def get_year(fecha):
    time_fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return time_fecha.year

def today():
    time_fecha = datetime.datetime.today()
    return time_fecha

def today_day():
    time_fecha = datetime.datetime.today()
    return time_fecha.day

def today_month():
    time_fecha = datetime.datetime.today()
    return time_fecha.month

def today_year():
    time_fecha = datetime.datetime.today()
    return time_fecha.year

def greater_or_equal_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1>=time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def greater_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1>time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def lower_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1<time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def lower_or_equal_than(fecha1,fecha2):
    resultado = -1
    time_fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    time_fecha2 = datetime.datetime.strptime(fecha2, "%Y-%m-%d")
    if time_fecha1<=time_fecha2:
        resultado = 1
    else:
        resultado = 0
    return resultado

def get_monthrange(year, month):
    return calendar.monthrange(year, month)
