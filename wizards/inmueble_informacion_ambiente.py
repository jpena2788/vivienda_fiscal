from odoo import api, fields, models
from odoo import netsvc
from odoo.exceptions import ValidationError

class InformacionAmbiente(models.TransientModel):
    _name = 'vivienda.informacion_ambiente'
    _description = 'Información de ambiente'

   
    @api.model
    def _get_tipo_ambiente(self): 
      return self._context.get('active_id')  
    
    
    solicitud_ambiente_id = fields.Many2one('vivienda.detalle_solicitud_ambiente', string="Solicitud Tipo de ambiente", ondelete='restrict', default=_get_tipo_ambiente )  
    tipo_ambiente_id = fields.Many2one('vivienda.ambiente_caracteristica', string="Tipo de ambiente", related='solicitud_ambiente_id.detalle_solicitud_id',
                       readonly=True, store=True) 
    num_personas = fields.Integer(string='Número de personas', related='tipo_ambiente_id.num_personas', readonly=True, store=True)     
    caracteristicas_ids = fields.One2many('vivienda.detalle_ambiente', 'ambiente_id', related='tipo_ambiente_id.caracteristicas_ids', 
                                          readonly=True, store=True) 
       
   
    
