from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ViviendaEntorno(models.Model):
    _name = 'vivienda.entorno'
    _description = 'Entorno Familiar'

    empleado_id = fields.Many2one('hr.employee', string='Persona', required=True)
    name = fields.Char(string='Nombres y Apellidos', required=True)
    relation = fields.Char(string='Relación')
    vivienda_id = fields.Many2one('vivienda.vivienda', string='Asignación de Vivienda')

