from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class TipoHuesped(models.Model):
    _name = 'hospedaje.tipo_huesped'
    _description = 'Tipo de Huesped'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Tipo de huesped", required=True,tracking=True )
    descripcion = fields.Text(string='Descripción', tracking=True )  
    active = fields.Boolean(string='Activo/Inactivo', default='True' )
    
    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Nombre del tipo de huesped debe ser único"),]   
    
    @api.constrains('name')
    def _check_name_marca_insensitive(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Ya existe el huesped: %s , no se permiten valores duplicados" % (record.name.upper()))    