from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class AmbienteUsuario(models.Model):
    _name = 'vivienda.ambiente_por_usuario'
    _description = 'Número de ambientes por usuario'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "ambiente_usuario"
    
    
    ambiente_usuario = fields.Integer(string='Ambiente por usuario', required=True, tracking=True)    
    