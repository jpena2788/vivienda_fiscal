from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class DiasAnticipacion(models.Model):
    _name = 'vivienda.numero_habitacion_reservada'
    _description = 'Número de habitaciones reservadas'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "numero_habitacion_reservada"
    
    
    numero_habitacion_reservada = fields.Integer(string='Número de habitaciones reservadas', required=True, tracking=True)
    
    
    
    
    
    
    
  