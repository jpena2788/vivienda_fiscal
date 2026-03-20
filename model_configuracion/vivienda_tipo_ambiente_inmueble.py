from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace
import json

class TipoAmbienteInmueble(models.Model):
    _name = 'vivienda.tipo_ambiente_inmueble'
    _description = 'Tipos de ambientes por inmueble'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'tipo_ambiente_id'
    
    
    @api.model
    def _get_inmueble(self): 
        _condicion =[]  
        if self.user_has_groups('vivienda.group_vivienda_administrador_general'):
            _condicion = [(1,'=',1)]
        elif self.user_has_groups('vivienda.group_vivienda_administrador_vivienda'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]          
        return _condicion 
    descripcion = fields.Text(string='Descripción', tracking=True )  
    inmueble_id = fields.Many2one(string='Inmueble', comodel_name='vivienda.inmueble', ondelete='restrict') 
    tipo_ambiente_id_domain = fields.Char ( compute = "_compute_tipo_ambiente_id" , readonly = True, store = False, )
    tipo_ambiente_id = fields.Many2one(string='Tipo de Ambiente', comodel_name='vivienda.tipo_ambiente', ondelete='restrict')    
    precio = fields.Float(string='Precio', required=True)   
    num_personas = fields.Integer(string='Número de personas', required=True, default=1) 
    caracteristicas_ids = fields.One2many('vivienda.detalle_tipo_ambiente', 'tipo_ambiente_id', 'Características de Ambiente', required = True, copy=True) 
    active = fields.Boolean(string='Activo/Inactivo', default='True' )
    
    _sql_constraints = [('name_unique', 'UNIQUE(vivienda_id,tipo_ambiente_id)', "Ya existe el tipo de habitación creado para este vivienda"),]   
    
    @api.constrains('num_personas')
    def _check_num_personas(self):
        for record in self:                    
            if record.num_personas<1:
                raise ValidationError("Número de personas debe ser mayor a 0")


    # def unlink(self):
    #     for record in self:
    #         ambientes = self.env['vivienda.ambiente'].search([('vivienda_id','=',record.vivienda_id.id)])
    #         if not(ambientes):
    #             record.caracteristicas_ids.unlink()
    #         else:
    #             raise ValidationError("No puede eliminar el tipo de habitación, ya existen ambientes creadas con este tipo")            
    #     return super(TipoAmbientevivienda, self).unlink()
    
    @api.depends('inmueble_id')
    def _compute_tipo_ambiente_id(self):
        for record in self:                    
            listado_tipo_ambiente = record.inmueble_id.tipo_ambiente_ids.tipo_ambiente_id 
            record.tipo_ambiente_id_domain = json.dumps([('id' , 'not in' , listado_tipo_ambiente.ids)])
    
    
    # def ver_tipo_ambiente(self):
    #     if self.user_has_groups('vivienda.group_vivienda_administrador_general'):
    #         _condicion = [(1,'=',1)]
    #     else:
    #         _condicion = [('reparto_id','=',self.env.user.company_id.id)]            
    #     diccionario= {
    #                     'name': ('Tipos de habitación por vivienda'),        
    #                     'domain': _condicion,
    #                     'res_model': 'vivienda.tipo_ambiente_vivienda',
    #                     'views': [(self.env.ref('vivienda.view_vivienda_tipo_ambiente_vivienda_tree').id, 'tree'),(self.env.ref('vivienda.view_vivienda_tipo_ambiente_vivienda_form').id, 'form')],
    #                     'search_view_id':[self.env.ref('vivienda.view_vivienda_tipo_ambiente_vivienda_search').id, 'search'],                           
    #                     'view_mode': 'tree,form',
    #                     'type': 'ir.actions.act_window',
    #                     'context': {'search_default_reparto':1,'search_default_vivienda':1,'search_default_tipo_ambiente':1},
    #                 } 
    #     return diccionario   
        
            

class DetalleTipoAmbiente(models.Model):
    _name = "vivienda.detalle_tipo_ambiente"
    _description = 'Detalle tipo ambiente por inmueble' 
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'caracteristica_id'
    
    tipo_ambiente_id = fields.Many2one('vivienda.tipo_ambiente_inmueble', string="Ambiente", ondelete='restrict', required=True, index=True, )  
    caracteristica_id_domain = fields.Char ( compute = "_compute_caracteristica_id_domain" , readonly = True, store = False, )
    caracteristica_id = fields.Many2one('vivienda.catalogo_caracteristica', string="Característica", required=True, ondelete='restrict', tracking=True)       
   
    valor_ids = fields.Many2many(string='Valores', comodel_name='vivienda.caracteristica_valor', relation='vivienda_detallle_tipo_ambiente_caracteristica_valor_rel', 
                                      column1='detalle_tipo_ambiente_id', column2='valor_id',domain="[('caracteristica_id', '=', caracteristica_id)]")
    
    

    @api.depends('caracteristica_id')
    def _compute_caracteristica_id_domain(self):
        for record in self:                  
            listado_caracteristicas = record.tipo_ambiente_id.caracteristicas_ids.caracteristica_id 
            record.caracteristica_id_domain = json.dumps([('id' , 'not in' , listado_caracteristicas.ids)])