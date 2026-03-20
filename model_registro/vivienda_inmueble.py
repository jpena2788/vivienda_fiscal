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
    active = fields.Boolean(string='Activo', default=True)

class Inmueble(models.Model):
    _name = 'vivienda.inmueble'
    _description = 'Inmueble'

    name = fields.Char(string='Código', required=True, )
    description = fields.Char(string='Descripción')
    address = fields.Char(string='Ubicacion Geográfica', required=True)
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
    politicas_ids = fields.Many2many(string='Políticas', comodel_name='vivienda.catalogo_politicas', relation='vivienda_vivienda_politicas_rel',
                                     column1='inmueble_id', column2='politicas_id')  
    tipo_ambiente_ids = fields.One2many(string='Tipos de Ambientes', comodel_name='vivienda.tipo_ambiente_inmueble', inverse_name='inmueble_id',)    
    ambiente_ids = fields.One2many(string='Ambiente', comodel_name='vivienda.ambiente', inverse_name='inmueble_id',)
    
    #alojamiento
    hora_entrada = fields.Float("Hora de entrada", tracking=True)
    hora_salida = fields.Float("Hora de salida", tracking=True)
    dia_anticipacion = fields.Integer(string='Días mínimos de anticipación', tracking=True)
    dia_anticipacion_maximo = fields.Integer(string='Días máximos anticipación', tracking=True)
    # tipo_huesped_ids = fields.Many2many(string='Tipos de huesped', comodel_name='hr.organico.escalafon', relation='hospedaje_escalafon_rel',
    #                                     column1='hospedaje_id', column2='escalafon_id',domain=_get_militar_domain) 
    # tipo_habitacion_ids = fields.One2many(string='Tipos de habitaciones', comodel_name='vivienda.tipo_habitacion_vivienda', inverse_name='inmueble_id',)    
          
    #habitacion_ids = fields.One2many(string='Habitaciones', comodel_name='vivienda.habitacion', inverse_name='inmueble_id',)
    numero_habitacion_reservada = fields.Integer(string='Número de habitaciones reservadas', tracking=True)
    dias_pago = fields.Integer(string='Días disponibles para pagar reserva', tracking=True)   
    habitacion_usuario = fields.Integer(string='Habitación por usuario', tracking=True)
    
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
    
     
    # @api.model
    # def default_get(self, fields):
    #     res = super(Inmueble, self).default_get(fields)
    #     dias = self.env['inmueble.dias_anticipacion'].search([],limit=1)
    #     hora = self.env['inmueble.hora_entrada_salida'].search([],limit=1)
    #     numero_reserva = self.env['inmueble.numero_habitacion_reservada'].search([],limit=1)
    #     dias_pago = self.env['inmueble.dias_pago'].search([],limit=1)
    #     habita = self.env['inmueble.habitacion_por_usuario'].search([],limit=1)
    #     res['dia_anticipacion'] = dias[0].dia_anticipacion
    #     res['dia_anticipacion_maximo'] = dias[0].dia_anticipacion_maximo
    #     res['hora_entrada'] = hora[0].hora_entrada
    #     res['hora_salida'] = hora[0].hora_salida
    #     res['numero_habitacion_reservada'] = numero_reserva[0].numero_habitacion_reservada
    #     res['dias_pago'] = dias_pago[0].dia_pago
    #     res['habitacion_usuario'] = habita[0].habitacion_usuario
    #     return res