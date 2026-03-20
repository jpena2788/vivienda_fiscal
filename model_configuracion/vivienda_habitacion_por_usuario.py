from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class HabitacionUsuario(models.Model):
    _name = 'vivienda.habitacion_por_usuario'
    _description = 'Número de habitaciones por usuario'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "habitacion_usuario"
    
    
    habitacion_usuario = fields.Integer(string='Habitación por usuario', required=True, tracking=True)    
    