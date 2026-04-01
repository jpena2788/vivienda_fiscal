from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace
import json

class AmbienteCaracteristica(models.Model):
    _name = 'vivienda.ambiente_caracteristica'
    _description = 'Características de Ambientes por Inmueble'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'ambiente_id'
    
    
    @api.model
    def _get_inmueble(self): 
        _condicion =[]  
        if self.env.user.has_groups('vivienda_fiscal.group_vivienda_administrador_general'):
            _condicion = [(1,'=',1)]
        elif self.env.user.has_groups('vivienda_fiscal.group_vivienda_administrador'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]          
        return _condicion 
    sequence = fields.Integer(string='Sequence', help="Orden de Ambientes", index=True)
    descripcion = fields.Text(string='Descripción', tracking=True )  
    inmueble_id = fields.Many2one(string='Inmueble', comodel_name='vivienda.inmueble', ondelete='restrict') 
    reparto_id = fields.Many2one(
        string='Reparto',
        comodel_name='res.company',
        related='inmueble_id.reparto_id',
        readonly=True,
        store=True,
    )
    
    ambiente_id_domain = fields.Char ( compute = "_compute_ambiente_id" , readonly = True, store = False, )
    ambiente_id = fields.Many2one(string='Ambiente', comodel_name='vivienda.ambiente', ondelete='restrict')    
    
    
    precio = fields.Float(string='Precio', required=True)   
    num_personas = fields.Integer(string='Número de personas', required=True, default=1) 
    caracteristicas_ids = fields.One2many('vivienda.detalle_ambiente', 'ambiente_id', 'Características de Ambiente', copy=True) 
    active = fields.Boolean(string='Activo/Inactivo', default=True )
    
    _sql_constraints = [('name_unique', 'UNIQUE(inmueble_id,ambiente_id)', "Ya existe el ambiente creado para este inmueble"),]   

    def _get_ambiente_domain_values(self):
        self.ensure_one()
        if not self.inmueble_id:
            return [('id', 'in', [])]

        ambientes_usados = self.search([
            ('inmueble_id', '=', self.inmueble_id.id),
            ('id', '!=', self.id),
        ]).mapped('ambiente_id').ids
        return [
            ('inmueble_id', '=', self.inmueble_id.id),
            ('id', 'not in', ambientes_usados),
        ]
    
    @api.constrains('num_personas')
    def _check_num_personas(self):
        for record in self:                    
            if record.num_personas<1:
                raise ValidationError("Número de personas debe ser mayor a 0")

    @api.constrains('inmueble_id', 'ambiente_id')
    def _check_ambiente_inmueble(self):
        for record in self:
            if not record.inmueble_id or not record.ambiente_id:
                continue

            if record.ambiente_id.inmueble_id != record.inmueble_id:
                raise ValidationError("El ambiente seleccionado no pertenece al inmueble indicado.")

            duplicado = self.search([
                ('inmueble_id', '=', record.inmueble_id.id),
                ('ambiente_id', '=', record.ambiente_id.id),
                ('id', '!=', record.id),
            ], limit=1)
            if duplicado:
                raise ValidationError("Ya existe un registro de características para ese ambiente en este inmueble.")


    # def unlink(self):
    #     for record in self:
    #         ambientes = self.env['vivienda.ambiente'].search([('vivienda_id','=',record.vivienda_id.id)])
    #         if not(ambientes):
    #             record.caracteristicas_ids.unlink()
    #         else:
    #             raise ValidationError("No puede eliminar el tipo de habitación, ya existen ambientes creadas con este tipo")            
    #     return super(TipoAmbientevivienda, self).unlink()
    
    @api.depends('inmueble_id')
    def _compute_ambiente_id(self):
        for record in self:      
            record.ambiente_id_domain = json.dumps(record._get_ambiente_domain_values())

    @api.onchange('inmueble_id')
    def _onchange_inmueble_id(self):
        self.ambiente_id = False
        return {
            'domain': {
                'ambiente_id': self._get_ambiente_domain_values(),
            }
        }
 
    def ver_ambientes(self):
        if self.env.user.has_groups('vivienda.privilegio_vivienda_administrador_general'):
            _condicion = [(1,'=',1)]
        else:
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]            
        diccionario= {
                        'name': ('Características de Ambientes'),        
                        'domain': _condicion,
                        'res_model': 'vivienda.ambiente_caracteristica',
                        'views': [(self.env.ref('vivienda_fiscal.view_vivienda_ambiente_caracteristica_tree').id, 'list'),(self.env.ref('vivienda_fiscal.view_vivienda_ambiente_caracteristica_form').id, 'form')],
                        'search_view_id':[self.env.ref('vivienda_fiscal.view_vivienda_ambiente_caracteristica_search').id, 'search'],                           
                        'view_mode': 'list,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_reparto':1,'search_default_inmueble':1,'search_default_ambiente':1},
                    } 
        return diccionario   
        
      

class DetalleTipoAmbiente(models.Model):
    _name = "vivienda.detalle_ambiente"
    _description = 'Detalle  ambiente por inmueble' 
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'caracteristica_id'
    
    ambiente_id = fields.Many2one('vivienda.ambiente_caracteristica', string="Ambiente", ondelete='restrict', required=True, index=True, )  
    caracteristica_id_domain = fields.Char ( compute = "_compute_caracteristica_id_domain" , readonly = True, store = False, )
    caracteristica_id = fields.Many2one('vivienda.catalogo_caracteristica', string="Característica", required=True, ondelete='restrict', tracking=True)       
   
    valor_ids = fields.Many2many(string='Valores', comodel_name='vivienda.caracteristica_valor', relation='vivienda_detalle_ambiente_caracteristica_valor_rel', 
                                      column1='detalle_ambiente_id', column2='valor_id',domain="[('caracteristica_id', '=', caracteristica_id)]")
    
    

    @api.depends('ambiente_id.caracteristicas_ids.caracteristica_id')
    def _compute_caracteristica_id_domain(self):
        for record in self:
            if record.ambiente_id:
                usados = record.ambiente_id.caracteristicas_ids.mapped('caracteristica_id').ids

                # MUY IMPORTANTE: excluir el mismo registro en edición
                if record.caracteristica_id:
                    usados = [x for x in usados if x != record.caracteristica_id.id]

                record.caracteristica_id_domain = json.dumps([
                    ('id', 'not in', usados)
                ])
            else:
                record.caracteristica_id_domain = json.dumps([])
    
    @api.constrains('caracteristica_id', 'ambiente_id')
    def _check_duplicados(self):
        for record in self:
            if not record.ambiente_id or not record.caracteristica_id:
                continue

            duplicados = self.search([
                ('ambiente_id', '=', record.ambiente_id.id),
                ('caracteristica_id', '=', record.caracteristica_id.id),
                ('id', '!=', record.id)
            ])

            if duplicados:
                raise ValidationError("Esta característica ya fue agregada a este ambiente")