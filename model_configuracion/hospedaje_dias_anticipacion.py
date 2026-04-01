from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class DiasAnticipacion(models.Model):
    _name = 'hospedaje.dias_anticipacion'
    _description = 'Días de anticipación'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "dia_anticipacion"
    
    
    dia_anticipacion = fields.Integer(string='Días mínimos de anticipación', required=True, tracking=True)
    dia_anticipacion_maximo = fields.Integer(string='Días máximos de anticipación', required=True, tracking=True)
    
    
    
    
    
    
  