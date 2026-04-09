from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class TipoInmueble(models.Model):
    _name = 'vivienda.tipo_inmueble'
    _description = 'Tipo de Inmueble'

    name = fields.Char(string='Tipo de Inmueble', required=True)
    active = fields.Boolean(string='Activo', default=True)
    

class Sector(models.Model):
    _name = 'vivienda.sector'
    _description = 'Sector'

    name = fields.Char(string='Sector', required=True)
    reparto_id = fields.Many2one('res.company', string='Reparto', ondelete='restrict')
    active = fields.Boolean(string='Activo', default=True)

class Inmueble(models.Model):
    _name = 'vivienda.inmueble'
    _description = 'Inmueble'

    @api.model
    def _get_militar_domain(self):
        tipo_escalafon = self.env['hr.organico.tipo.grupo.persona'].search([('id','!=',self.env.ref("th_gestion_organico.hr_tipo_grupo_persona0").id)]) 
        _escalafon = []           
        escalafon = self.env['hr.organico.escalafon'].search([('tipo_escalafon_id','in',tipo_escalafon.ids)])      
        return [('id', 'in',escalafon.ids)] 
   
    name = fields.Char(string='Código', required=True, )
    reparto_id = fields.Many2one(string='Reparto', comodel_name='res.company', default=lambda s: s.env.company.id, ondelete='restrict',tracking=True, required=True)    
    description = fields.Char(string='Descripción')
    address = fields.Char(string='Ubicacion Geográfica', required=True)
    tipo_huesped_ids = fields.Many2many(string='Tipos de huesped', comodel_name='hr.organico.escalafon', relation='inmueble_escalafon_rel',
                                        column1='inmueble_id', column2='escalafon_id',domain=_get_militar_domain) 
    tipo_inmueble_id = fields.Many2one('vivienda.tipo_inmueble', string='Tipo de Inmueble')
    sector_id = fields.Many2one('vivienda.sector', string='Sector')
    bloque = fields.Char('Bloque')
    numero = fields.Char('Número Habitación o Departamento')
    active = fields.Boolean(string='Activo', default=True)
    estado = fields.Selection([
        ('disponible','Disponible'),
        ('ocupado','Ocupado'),
        ('mantenimiento','Mantenimiento')
    ], default='disponible')
    condicion= fields.Selection([
        ('permanente','Permanente'),
        ('temporal','Temporal'),
    ], string='Condición del Inmueble',
    default='permanente',
    help='Define si el inmueble es de uso permanente o temporal')
    politicas_ids = fields.Many2many(string='Políticas', comodel_name='vivienda.catalogo_politicas', relation='vivienda_vivienda_politicas_rel',
                                     column1='inmueble_id', column2='politicas_id')  
    ambiente_ids = fields.One2many(string='Ambientes', comodel_name='vivienda.ambiente', inverse_name='inmueble_id',)    
    # ambiente_ids = fields.One2many(string='Ambiente', comodel_name='vivienda.ambiente', inverse_name='inmueble_id',)
    
    #alojamiento
    hora_entrada = fields.Float("Hora de entrada", tracking=True)
    hora_salida = fields.Float("Hora de salida", tracking=True)
    dia_anticipacion = fields.Integer(string='Días mínimos de anticipación', tracking=True)
    dia_anticipacion_maximo = fields.Integer(string='Días máximos anticipación', tracking=True)
    # tipo_huesped_ids = fields.Many2many(string='Tipos de huesped', comodel_name='hr.organico.escalafon', relation='hospedaje_escalafon_rel',
    #                                     column1='hospedaje_id', column2='escalafon_id',domain=_get_militar_domain) 
        
    #habitacion_ids = fields.One2many(string='Habitaciones', comodel_name='vivienda.habitacion', inverse_name='inmueble_id',)
    numero_ambiente_reservada = fields.Integer(string='Número de ambientes reservadas', tracking=True)
    dias_pago = fields.Integer(string='Días disponibles para pagar reserva', tracking=True)   
    ambiente_usuario = fields.Integer(string='Ambiente por usuario', tracking=True)
    
    #vivienda
    # asignacion_ids = fields.One2many(
    #     'vf.vivienda.asignacion',
    #     'inmueble_id'
    # )

    @api.constrains('name')
    def _check_name_marca_insensitive(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Ya existe el registro: %s , no se permiten valores duplicados" % (record.name.upper())) 
    
    def ver_inmueble(self):
        
        if self.env.user.has_groups('vivienda_fiscal.group_vivienda_administrador_general'):
            _condicion = [(1,'=',1)]
        else:
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]
            
        diccionario= {
                        'name': ('Inmuebles'),        
                        'domain': _condicion,
                        'res_model': 'vivienda.inmueble',
                        'views': [(self.env.ref('vivienda_fiscal.view_vivienda_inmueble_list').id, 'list'),(self.env.ref('vivienda_fiscal.view_vivienda_inmueble_form').id, 'form')],
                        'search_view_id': self.env.ref('vivienda_fiscal.view_vivienda_inmueble_search').id,
                        'view_mode': 'list,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_sector':1,'search_default_reparto':1},
                    } 
        return diccionario 
     
    @api.model
    def default_get(self, fields):
        res = super(Inmueble, self).default_get(fields)

        dias = self.env['vivienda.dias_anticipacion'].search([], limit=1)
        hora = self.env['vivienda.hora_entrada_salida'].search([], limit=1)
        numero_reserva = self.env['vivienda.numero_ambiente_reservada'].search([], limit=1)
        dias_pago = self.env['vivienda.dias_pago'].search([], limit=1)
        habita = self.env['vivienda.ambiente_por_usuario'].search([], limit=1)

        # Validaciones seguras
        res['dia_anticipacion'] = dias.dia_anticipacion if dias else 0
        res['dia_anticipacion_maximo'] = dias.dia_anticipacion_maximo if dias else 0

        res['hora_entrada'] = hora.hora_entrada if hora else 0.0
        res['hora_salida'] = hora.hora_salida if hora else 0.0

        res['numero_ambiente_reservada'] = numero_reserva.numero_ambiente_reservada if numero_reserva else 0

        res['dias_pago'] = dias_pago.dia_pago if dias_pago else 0

        res['ambiente_usuario'] = habita.ambiente_usuario if habita else 0

        return res