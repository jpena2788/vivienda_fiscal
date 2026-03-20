from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class DiasPago(models.Model):
    _name = 'vivienda.dias_pago'
    _description = 'Días para realizar el pago'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "dia_pago"
    
    
    dia_pago = fields.Integer(string='Días para pagar la reserva', required=True, tracking=True)
   
    
    
    
    
    
    
  