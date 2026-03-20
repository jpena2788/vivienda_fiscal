from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class Piso(models.Model):
    _name = 'vivienda.piso'
    _description = 'Pisos'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre Piso", required=True,tracking=True)
    descripcion = fields.Text(string='Descripción', tracking=True )  
    active = fields.Boolean(string='Activo/Inactivo', default='True' )
    
    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Nombre del piso debe ser único"),]   
    
    @api.constrains('name')
    def _check_name_insensitive(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Ya existe el piso: %s , no se permiten valores duplicados" % (record.name.upper()))    