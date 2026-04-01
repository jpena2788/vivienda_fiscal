from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class NumeroAmbienteReserva(models.Model):
    _name = 'vivienda.numero_ambiente_reservada'
    _description = 'Número de ambientes reservadas'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "numero_ambiente_reservada"
    
    
    numero_ambiente_reservada = fields.Integer(string='Número de ambientes reservadas', required=True, tracking=True)
    
    
    
    
    
    
    
  