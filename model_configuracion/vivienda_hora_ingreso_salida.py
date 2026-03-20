from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class HoraEntradaSalida(models.Model):
    _name = 'vivienda.hora_entrada_salida'
    _description = 'Hora de entrada y salida'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
  
    name = fields.Char(string='Hora',default="Hora", store=False)    
    hora_entrada = fields.Float("Hora de entrada", required=True, tracking=True)
    hora_salida = fields.Float("Hora de salida", required=True, tracking=True)
    
    
   
  
  