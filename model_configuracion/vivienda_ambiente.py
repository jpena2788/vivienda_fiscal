from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace
import json
from odoo.tools.misc import file_path
import base64

class ViviendaAmbiente(models.Model):
    _name = 'vivienda.ambiente'
    _description = 'Ambientes del inmueble'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_image(self):
        try:
            image_path = file_path('vivienda_fiscal/static/src/img/default_image.png')
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read())
        except Exception:
            return False
      
    foto_ambiente = fields.Image(string='Foto habitación', default=_default_image)
    seleccion_estado = [('libre', 'Libre'), ('mantenimiento', 'Mantenimiento'),('no_op', 'No operativo'),('limpieza', 'Limpieza'),('ocupado', 'Ocupado')]
    state = fields.Selection(seleccion_estado, 'Estado Solicitud', readonly=True, default='libre')  
    name = fields.Char(string="Nombre Ambiente", required=True )    

    inmueble_id = fields.Many2one(
        'vivienda.inmueble',
        string="Inmueble",
        ondelete='restrict'        
    )
    
    tipo_ambiente_id = fields.Many2one(string='Tipo de ambiente', comodel_name='vivienda.tipo_ambiente_inmueble', domain="[('inmueble_id','=',inmueble_id)]", 
                                         ondelete='restrict',required=True)  
       
    
    piso_id = fields.Many2one(string='Piso', comodel_name='vivienda.piso', ondelete='restrict', required=True) 
    active = fields.Boolean(string='Activo/Inactivo', default='True' )

    # _sql_constraints = [('name_unique', 'UNIQUE(inmueble_id,name)', "Nombre del ambiente debe ser único en el mismo inmueble"),]   
    # @api.constrains('inmueble_id','name')
    # def _check_name_marca_insensitive(self):
    #     for record in self:
    #         model_ids = record.search([('id', '!=',record.id),('inmueble_id', '=',record.inmueble_id.id)])        
    #         list_names = [x.name.upper() for x in model_ids if x.name]        
    #         if record.name.upper() in list_names:
    #             raise ValidationError("Ya existe ambiente: %s , no se permiten valores duplicados en el mismo inmueble" % (record.name.upper()))  
    
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
    
    # def ver_ambiente(self):
    #     if self.user_has_groups('vivienda_fiscal.group_vf_admin'):
    #         _condicion = [(1,'=',1)]
    #     elif self.user_has_groups('vivienda_fiscal.group_vf_admin'):
    #         _condicion = [('reparto_id','=',self.env.user.company_id.id)]            
    #     diccionario= {
    #                     'name': ('Ambientes'),        
    #                     'domain': _condicion,
    #                     'res_model': 'vivienda.ambiente',
    #                     'views': [(self.env.ref('vivienda.view_vivienda_ambiente_tree').id, 'tree'),(self.env.ref('vivienda_fiscal.view_vivienda_ambiente_form').id, 'form')],
    #                     'search_view_id':[self.env.ref('vivienda.view_vivienda_ambiente_search').id, 'search'],                           
    #                     'view_mode': 'list,form',
    #                     'type': 'ir.actions.act_window',
    #                     'context': {'search_default_reparto':1,'search_default_vivienda':1,'search_default_estado':1},
    #                 } 
    #     return diccionario 