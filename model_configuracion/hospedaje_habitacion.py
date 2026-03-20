from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace
import json
from odoo.tools.misc import file_path
import base64

class Habitacion(models.Model):
    _name = 'hospedaje.habitacion'
    _description = 'Catálogo Habitación'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    
    
    @api.model
    def _default_image(self):
        image_path = file_path(
            'hospedaje', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())
    
    
    @api.model
    def _get_hospedaje(self): 
        _condicion =[]  
        if self.user_has_groups('hospedaje.group_hospedaje_administrador_general'):
            _condicion = [(1,'=',1)]
        elif self.user_has_groups('hospedaje.group_hospedaje_administrador_hospedaje'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]          
        return _condicion
    
    
    foto_habitacion = fields.Image(string='Foto habitación', default=_default_image)
    seleccion_estado = [('libre', 'Libre'), ('mantenimiento', 'Mantenimiento'),('no_op', 'No operativo'),('limpieza', 'Limpieza'),('ocupado', 'Ocupado')]
    state = fields.Selection(seleccion_estado, 'Estado Solicitud', readonly=True, default='libre')  
    name = fields.Char(string="Nombre Habitación", required=True )    
    hospedaje_id = fields.Many2one(string='Hospedaje', comodel_name='hospedaje.hospedaje', ondelete='restrict', domain=_get_hospedaje)    
    reparto_id = fields.Many2one(string='Reparto', comodel_name='res.company', related='hospedaje_id.reparto_id', readonly=True, store=True)  
    piso_id = fields.Many2one(string='Piso', comodel_name='hospedaje.piso', ondelete='restrict', required=True)         
    tipo_habitacion_id = fields.Many2one(string='Tipo de habitación', comodel_name='hospedaje.tipo_habitacion_hospedaje', domain="[('hospedaje_id','=',hospedaje_id)]", 
                                         ondelete='restrict',required=True)  
       
    active = fields.Boolean(string='Activo/Inactivo', default='True' )
    
    _sql_constraints = [('name_unique', 'UNIQUE(hospedaje_id,name)', "Nombre del habitación debe ser único en el mismo hospedaje"),]   
    
    @api.constrains('hospedaje_id','name')
    def _check_name_marca_insensitive(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id),('hospedaje_id', '=',record.hospedaje_id.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Ya existe habitación: %s , no se permiten valores duplicados en el mismo hospedaje" % (record.name.upper()))  
            
    def copy(self, default=None):
            if default is None:
                default = {}
            if self.name:
                default.update({
                    'name': self.name + ('(_nuevo)'),
                })
            return super(Habitacion, self).copy(default)
    
    def ver_habitacion(self):
        if self.user_has_groups('hospedaje.group_hospedaje_administrador_general'):
            _condicion = [(1,'=',1)]
        elif self.user_has_groups('hospedaje.group_hospedaje_administrador_hospedaje'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]            
        diccionario= {
                        'name': ('Habitaciones'),        
                        'domain': _condicion,
                        'res_model': 'hospedaje.habitacion',
                        'views': [(self.env.ref('hospedaje.view_hospedaje_habitacion_tree').id, 'tree'),(self.env.ref('hospedaje.view_hospedaje_habitacion_form').id, 'form')],
                        'search_view_id':[self.env.ref('hospedaje.view_hospedaje_habitacion_search').id, 'search'],                           
                        'view_mode': 'tree,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_reparto':1,'search_default_hospedaje':1,'search_default_estado':1},
                    } 
        return diccionario 


    def action_libre(self):
        self.write({'state': 'libre'})
        return True
        
    
    def action_mantenimiento(self):
        self.write({'state': 'mantenimiento'})
        return True
        
        
    def action_ocupado(self):
        self.write({'state': 'ocupado'})
        return True
    
    def action_no_operativo(self):
        self.write({'state': 'no_op'})
        return True
        
    
    
            
