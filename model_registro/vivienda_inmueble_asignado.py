from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace
import time
import datetime
from datetime import datetime
from datetime import timedelta
import json
from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_repr, is_html_empty, str2bool


class InmuebleAsignado(models.Model):
    _name = 'vivienda.inmueble_asignado'
    # _table = 'vivienda_solicitud_asignacion'
    _description = 'Solicitud y/o registro de Asignación de Vivienda'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "inmueble_id"
    
    seleccion_estado = [('draft', 'Borrador'), ('por_aprobar', 'Por aprobar'),('asignado', 'Asignado'),('pagado', 'Pagado'), ('aprobado', 'Aprobado'),('anular', 'Anulado'),('llegada', 'Llegada'),('fin', 'Finalizado'),('archivar','Archivar')]
    state = fields.Selection(seleccion_estado, 'Estado Solicitud de Asignación', readonly=True, default='draft', tracking=True)    
    inmueble_id = fields.Many2one(string='Inmueble', comodel_name='vivienda.inmueble', ondelete='restrict', tracking=True, required=True)       
    hora_entrada = fields.Float("Hora de entrada", readonly=True, help = "Campo de tipo fecha" )
    hora_salida = fields.Float("Hora de salida", readonly=True)
    precio = fields.Float(string="Precio", required=True, compute = "_compute_precio_id", readonly=True, store=True)
    personal_id = fields.Many2one(string='Personal', comodel_name='hr.employee', ondelete='restrict', tracking=True, required=True,
                                  default=lambda self: self.env.user.employee_id.id)
    reparto_empleado_id = fields.Many2one('res.company', 'Reparto', compute = "_compute_vivienda_id", readonly=True, store=True,)
    reparto_solicitud_empleado = fields.Many2one(
        'res.company',
        'Reparto Solicitud',
        related='personal_id.company_id',
        readonly=True,
        store=True,
    )
    reparto_id = fields.Many2one(
        'res.company',
        'Reparto Inmueble',
        related='inmueble_id.reparto_id',
        readonly=True,
        store=True,
    )
    sector_id = fields.Many2one(
        'vivienda.sector',
        'Sector',
        related='inmueble_id.sector_id',
        readonly=True,
        store=True,
    )
    politicas_ids = fields.Many2many(
        'vivienda.catalogo_politicas',
        string='Políticas',
        compute='_compute_politicas_ids',
        readonly=True,
    )
       
    user_id = fields.Many2one('res.users', 'Usuario', related='personal_id.user_id', readonly=True, store=True, required=True)     
    inmueble_id_domain = fields.Char ( compute = "_compute_vivienda_id" , readonly = True, store = False, )
    condicion = fields.Selection(
        related='inmueble_id.condicion',
        string='Condición',
        readonly=True,
        store=True,
    )
    email = fields.Char(string='Email', store=True, readonly=True, compute = "_compute_vivienda_id")
    cedula_identidad = fields.Char(string='Cédula de identidad', store=True, readonly=True, compute = "_compute_vivienda_id")
    telefono = fields.Char(string='Teléfono', store=True, readonly=True, compute = "_compute_vivienda_id")  
    direccion = fields.Char(string='Dirección', store=True,  readonly=True, compute = "_compute_vivienda_id") 
    fecha_solicitud = fields.Date(string='Fecha de Solicitud', required=True, default=datetime.today(),readonly=True )  
    fecha_aprobacion = fields.Date('Fecha aprobación',  readonly=True)
    dias_pago = fields.Integer(string='Días disponibles para pagar reserva',)
    dias_transcurridos = fields.Integer(string='Días transcurridos', required=True,default=0)    
    fecha_inicio = fields.Date(string='Fecha de entrada' )
    fecha_fin = fields.Date(string='Fecha de salida' )  
    fecha_alta = fields.Date(string='Fecha de alta' )
    fecha_baja = fields.Date(string='Fecha de baja' )   
    motivo_rechazo = fields.Text('Motivo de anulación')    
    aceptacion_termino = fields.Boolean(string='aceptación terminos',)  
    dependiente_ids = fields.Many2many(string='Dependientes', comodel_name='hr.employee.hijos', relation='vivienda_solicitud_dependientes_rel', column1='solicitud_id', column2='dependiente_id', domain="[('employee_id','=',personal_id)]")
    
    ambiente_ids = fields.One2many(string='Ambientes',  comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)
    ambiente_cliente_ids = fields.One2many(string='Ambientes', comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)
    ambiente_operador_ids = fields.One2many(string='Ambientes', comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)  
   
    archivos_adjuntos= fields.Binary( string='Comprobante:')
    observacion = fields.Text('Observación')
    es_encargado = fields.Boolean(string='Es Encargado',help="Bandera usada para saber si el que creo la solicitud es un solicitante o un encargado de solicitudes encargado = true, solicitante=false")
    band_cobrar = fields.Boolean(string='Cobrado',help="Bandera usada para llevar un control de las solicitudes cobradas true cobradas, false no cobradas")      
    fecha_pago = fields.Datetime('Fecha de pago',  readonly=True)
    fecha_llegada = fields.Datetime('Fecha llegada',  readonly=True)
    fecha_salida = fields.Datetime('Fecha salida',  readonly=True)
    es_archivar = fields.Boolean(string='Archivar',default=False)
    inmueble_ambiente_ids = fields.One2many(
        comodel_name='vivienda.ambiente_caracteristica',
        compute='_compute_inmueble_ambiente_ids',
        string='Ambientes del inmueble',
        readonly=True,
    )
    warning = {
        'title': 'Mensaje de error',
        'message' : ''
         }    

    @api.depends('inmueble_id', 'inmueble_id.politicas_ids')
    def _compute_politicas_ids(self):
        for record in self:
            record.politicas_ids = record.inmueble_id.politicas_ids

    @api.depends('inmueble_id')
    def _compute_inmueble_ambiente_ids(self):
        for record in self:
            if record.inmueble_id:
                record.inmueble_ambiente_ids = self.env['vivienda.ambiente_caracteristica'].search([
                    ('inmueble_id', '=', record.inmueble_id.id)
                ])
            else:
                record.inmueble_ambiente_ids = False
    
    @api.constrains('condicion', 'fecha_inicio', 'fecha_fin')
    def _check_fechas_por_condicion(self):
        for record in self:
            # Solo exigir fechas en temporal
            if record.condicion == 'temporal':
                if not record.fecha_inicio or not record.fecha_fin:
                    raise ValidationError("Debe ingresar fecha de entrada y fecha de salida para inmuebles temporales.")
                if record.fecha_fin < record.fecha_inicio:
                    raise ValidationError("La fecha de salida no puede ser menor a la fecha de entrada.")

    @api.constrains('ambiente_ids','ambiente_operador_ids')
    def _check_habitacion(self):
        for record in self:
            if record.condicion != 'permanente' and not record.ambiente_operador_ids:
                raise ValidationError("Por favor seleccione por lo menos un ambiente.")

            
   
    # @api.model         
    # def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
    #     if 'precio' in fields:
    #         fields.remove('precio')
    #     return super(Solicitud, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'precio' in fields:
            fields.remove('precio')  
        if 'hora_entrada' in fields:
            fields.remove('hora_entrada')  
        if 'hora_salida' in fields:
            fields.remove('hora_salida')                
        res = super(InmuebleAsignado, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        return res
    
   
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Solicitud, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field[@name='fecha_inicio']"):
    #             date = fields.Date.today()
    #             date += timedelta(days=8)
    #             node.set('options', "{'datepicker': {'minDate': '%s'}}" % fields.Date.today())
    #         res['arch'] = etree.tostring(doc)
    #     return res 

    def ver_solicitudes(self):
        _condicion = []
        user = self.env.user
        if user.has_group('vivienda_fiscal.group_vivienda_administrador'):
            _condicion = [(1,'=',1)]
        elif user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id),('state','not in',['draft','anular']),('es_archivar','=', False)]
        diccionario= {
                        'name': ('Solicitudes de inmuebles'),        
                        'domain': _condicion,
                        'res_model': 'vivienda.inmueble_asignado',
                        'views': [(self.env.ref('vivienda_fiscal.view_vivienda_solicitud_tree').id, 'list'),(self.env.ref('vivienda_fiscal.view_vivienda_solicitud_form').id, 'form')],
                        'search_view_id':[self.env.ref('vivienda_fiscal.view_vivienda_solicitud_search').id, 'search'],                           
                        'view_mode': 'list,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_vivienda':1,'search_default_estado':1,'default_es_encargado':True},
                    } 
        return diccionario 
    
    def ver_asignaciones(self):
        _condicion = []
        user = self.env.user
        if user.has_group('vivienda_fiscal.group_vivienda_administrador'):
            _condicion = [(1,'=',1)]
        elif user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id),('state','in',['asignado']),('es_archivar','=', False)]
        diccionario= {
                        'name': ('Asignaciones de inmuebles'),        
                        'domain': _condicion,
                        'res_model': 'vivienda.inmueble_asignado',
                        'views': [(self.env.ref('vivienda_fiscal.view_vivienda_registro_asignacion_tree').id, 'list'),(self.env.ref('vivienda_fiscal.view_vivienda_registro_asignacion_form').id, 'form')],
                        'search_view_id':[self.env.ref('vivienda_fiscal.view_vivienda_registro_asignacion_search').id, 'search'],                           
                        'view_mode': 'list,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_estado':1,'search_default_sector':1,'search_default_inmueble':1},
                    } 
        return diccionario 
    
    @api.depends('personal_id')
    def _compute_vivienda_id(self):
        for record in self:
            record.reparto_empleado_id = record.personal_id.company_id
            record.email = record.personal_id.work_email
            record.cedula_identidad = record.personal_id.identification_id
            record.telefono = record.personal_id.mobile_phone            
            direccion = self.env['hr.employee.domicilio'].search([('estado','=', 'activo')],limit=1) 
            if (direccion):
                record.direccion = direccion[0].state_id.name + "/ " + direccion[0].ciudad_id.name + "/ " + direccion[0].domicilio
            _inmueble = []
            if(record.es_encargado):                
                if(record.personal_id.escalafon_id):                   
                    self.env.cr.execute("select inmueble_id from inmueble_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall()   
                    _inmueble_reparto = []                  
                    for linea in res:                                   
                        _inmueble_reparto.append(linea['inmueble_id'])
                    _inmueble = self.env['vivienda.inmueble'].search([('id','in',_inmueble_reparto),('reparto_id','=',self.env.company.id)]).ids 
                if (record.personal_id.escalafon_id) and self.env.user.has_group('vivienda_fiscal.group_vivienda_administrador'):                    
                    self.env.cr.execute("select inmueble_id from inmueble_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall() 
                    for linea in res:                                   
                        _inmueble.append(linea['inmueble_id'])
            else:    
                if(record.personal_id.escalafon_id):               
                    self.env.cr.execute("select inmueble_id from inmueble_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall() 
                    for linea in res:                                   
                        _inmueble.append(linea['inmueble_id'])
            record.inmueble_id_domain = json.dumps([('id' , 'in' , _inmueble)])       

    

    @api.onchange('inmueble_id')
    def _onchange_inmueble_id(self):
        for record in self:     
            if(record.inmueble_id):   
                dias_anticipacion = self.env['vivienda.inmueble'].browse(self.inmueble_id.id).dia_anticipacion
                date = datetime.now()
                date += timedelta(days=int(dias_anticipacion)) 
                record.fecha_inicio = date                            
                horario = self.env['vivienda.hora_entrada_salida'].search([], limit=1)
                if horario:
                    record.hora_entrada = horario.hora_entrada
                    record.hora_salida = horario.hora_salida
                # Permanente: sin fechas
                if record.condicion == 'permanente':
                    record.fecha_inicio = False
                    record.fecha_fin = False
                else:
                    # Temporal: solo poner valor inicial si está vacío
                    dias_anticipacion = record.inmueble_id.dia_anticipacion or 0
                    fecha_base = (datetime.now() + timedelta(days=int(dias_anticipacion))).date()
                    if not record.fecha_inicio:
                        record.fecha_inicio = fecha_base
                    if not record.fecha_fin:
                        record.fecha_fin = record.fecha_inicio
                     
    def _actualizar_dias_pago(self): 
        registros = self.search([('state','=','asignado')])   
        for registro in registros: 
            dias_transcurridos = (datetime.now().date() - registro.fecha_aprobacion).days 
            if(dias_transcurridos > registro.dias_pago):               
                registro.write({'dias_transcurridos':dias_transcurridos,
                                'state':'anular',
                                'motivo_rechazo':'No realizo el pago en el plazo de {} días'.format(registro.dias_pago)})
            else:                
                registro.write({'dias_transcurridos':int(dias_transcurridos)})
        return True            
                       
    @api.onchange('fecha_inicio')
    def _onchange_fecha_inicio(self):
        for record in self:           
            if record.condicion != 'temporal' or not record.fecha_inicio:
                continue
            if not record.fecha_fin or record.fecha_fin < record.fecha_inicio:
                record.fecha_fin = record.fecha_inicio

                if not (self.env.user.has_group('vivienda_fiscal.group_vivienda_administrador') or self.env.user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud')):
                    anticipacion = record.inmueble_id
                    # Validar rango solo si está configurado
                    minimo = record.inmueble_id.dia_anticipacion or 0
                    maximo = record.inmueble_id.dia_anticipacion_maximo or 0
                   
                    if maximo > 0:
                        hoy = datetime.now().date()
                        fecha_min = hoy + timedelta(days=int(minimo))
                        fecha_max = hoy + timedelta(days=int(maximo))

                        if record.fecha_inicio < fecha_min:
                            record.fecha_inicio = fecha_min
                            return {'warning': {'title': 'Mensaje de error', 'message': f'La fecha de inicio no puede ser menor a {fecha_min}'}}
                        if record.fecha_inicio > fecha_max:
                            record.fecha_inicio = fecha_max
                            return {'warning': {'title': 'Mensaje de error', 'message': f'La fecha de inicio no puede ser mayor a {fecha_max}'}}



    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        for record in self:
            if record.condicion != 'temporal' or not record.fecha_fin:
                continue
            if record.fecha_inicio and record.fecha_fin < record.fecha_inicio:
                record.fecha_fin = record.fecha_inicio
                return {'warning': {'title': 'Mensaje de error', 'message': f'La fecha de salida no puede ser menor a {record.fecha_inicio}'}}
                    
    @api.onchange('personal_id')
    def _onchange_personal_id(self):
        self.inmueble_id = False  

    #accion para vivienda
    def solicitar_inmueble(self):
        self.action_por_aprobar_asignacion()

    #accion para vivienda
    def action_por_aprobar_asignacion(self):
        if not self.aceptacion_termino:
            raise ValidationError("Lee las políticas y acepta los términos para continuar")

        self.write({'state': 'por_aprobar'})
        return True

    def aprobar_solicitud(self):  
        self.band_cobrar = True
        self.action_estado_aprobado()
        
    
    def asignacion_solicitud(self):  
        _cantidad = 0
        for ambiente in self.ambiente_ids:
            _cantidad += ambiente.cantidad
        # raise ValidationError("llego {} - {}".format(_cantidad,len(self.tipo_habitacion_ids.habitacion_ids)))
        #no se valida por tipo de habitación porque ya esta en otra función onchange
        if(_cantidad != len(self.ambiente_ids.ambiente_ids)):
            raise ValidationError("No se cumple con la petición de ambiente(s) del usuario")
        else:  
            self.ambiente_ids.ambiente_ids.state = 'ocupado' 
            self.action_estado_asignado()

    #accion para alojamiento
    def action_estado_por_aprobar(self):
        if(self.aceptacion_termino):
            self.dias_pago = self.inmueble_id.dias_pago
            self.write({'state': 'por_aprobar'})
        return True
    
    def action_estado_pagado(self):  
        # self.tipo_habitacion_ids.habitacion_ids.state = 'ocupado'   
        self.band_cobrar = True   
        self.write({'state': 'pagado'})
        return True


    def action_estado_asignado(self):
        self.write({'state': 'asignado', 'fecha_aprobacion': time.strftime('%Y-%m-%d %H:%M:%S')})
        self.ambiente_operador_ids.mapped('ambiente_ids').write({'state': 'ocupado'})
        return True


    def action_estado_aprobado(self):       
        self.write({'state': 'aprobado', 'fecha_pago': time.strftime('%Y-%m-%d %H:%M:%S')})      
        return True

    def action_llegada(self): 
        self.write({'state': 'llegada', 'fecha_llegada': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    def action_salida(self):  
        self.ambiente_ids.ambiente_ids.state = 'limpieza'
        self.write({'state': 'fin', 'fecha_salida': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True   
    
    def action_archivar(self):       
        self.write({'es_archivar': True})
        return True
    
    
    def action_estado_por_anular(self):
        self.ambiente_ids.ambiente_ids.state = 'libre'
        self.write({'state': 'anular'})
        return True    
    
    # -------------------------
    # COMPUTE PRECIO
    # -------------------------
    @api.depends('ambiente_ids.precio_total')
    def _compute_precio_id(self):
        for record in self:
            record.precio = sum(record.ambiente_ids.mapped('precio_total'))
           
    def _get_estados_bloqueantes(self):
        return ['asignado', 'aprobado', 'pagado', 'llegada']

    @api.constrains('user_id', 'condicion', 'state', 'es_archivar')
    def _check_solicitud_pendiente_misma_condicion(self):
        for record in self:
            if not record.user_id or not record.condicion:
                continue

            # Solo validar cuando la solicitud actual ya está comprometida
            if record.state not in record._get_estados_bloqueantes():
                continue

            duplicada = self.search([
                ('id', '!=', record.id),
                ('user_id', '=', record.user_id.id),
                ('condicion', '=', record.condicion),
                ('state', 'in', record._get_estados_bloqueantes()),
                ('es_archivar', '=', False),
            ], limit=1)

            if duplicada:
                raise ValidationError(
                    f"Ya tiene una solicitud activa con la misma condición ({record.condicion})."
                )

    @api.model
    def create(self, values): 
        result = super().create(values)
        return result
            
class SolicitudTipoAmbiente(models.Model):
    _name = 'vivienda.detalle_solicitud_ambiente'
    _description = 'Ambientes por solicitud'
    _rec_name = "detalle_solicitud_id"
        
    sequence = fields.Integer(string='Sequence', help="Orden de ambiente", index=True)
    solicitud_id = fields.Many2one('vivienda.inmueble_asignado', string="Solicitud", ondelete='restrict')
    state = fields.Selection('Estado Solicitud', related='solicitud_id.state', readonly=True, store=True)     
    cantidad = fields.Integer(string='Cantidad', required=True, tracking=True)
    inmueble_id = fields.Many2one(string='Inmueble', comodel_name='vivienda.inmueble', related='solicitud_id.inmueble_id', readonly=True, store=True)
    detalle_solicitud_id_domain = fields.Char ( compute = "_compute_detalle_solicitud_id" , readonly = True,)     
    detalle_solicitud_id = fields.Many2one('vivienda.ambiente_caracteristica', string="Ambientes", ondelete='restrict', required=True,                                        
                                         domain="[('inmueble_id','=',inmueble_id)]", index=True, ) 
    fecha_inicio = fields.Date(string='Fecha de entrada', related='solicitud_id.fecha_inicio', readonly=True, store=True)
    fecha_fin = fields.Date(string='Fecha de salida', related='solicitud_id.fecha_fin', readonly=True, store=True ) 
    num_personas = fields.Integer(string='# personas', related='detalle_solicitud_id.num_personas', readonly=True, store=True)      
    precio_diario = fields.Float(string="Precio diario",compute = "_compute_vivienda_id", readonly=True, store=True)
    precio_total = fields.Float(string="Precio total", compute = "_compute_vivienda_id", readonly=True, store=True)    
    ambiente_id_domain = fields.Char (compute = "_compute_ambiente_id" , readonly = True, store = False, )     
    ambiente_ids = fields.Many2many(string='Ambientes', comodel_name='vivienda.ambiente', relation='ambiente_asignacion_ambiente_rel', 
                                    column1='detalle_solicitud_id', column2='ambiente_id',)    
    es_encargado = fields.Boolean(string='Es Encargado', related='solicitud_id.es_encargado', readonly=False, store=True)
    condicion = fields.Selection(
        related='solicitud_id.condicion',
        string='Condición',
        readonly=True,
        store=True,
    )
        
    _sql_constraints = [('name_unique', 'UNIQUE(solicitud_id,detalle_solicitud_id)', "No se permite duplicidad de tipos de habitación")]   
    
    def toggle_start(self):
        self.es_encargado = True

    
    @api.constrains('cantidad')
    def check_cantidad(self):
        for record in self:    
            if record.cantidad > 2:
             raise ValidationError("Solo pueden agregar hasta 2 tipos de ambientes por persona")
            
    
   
    @api.depends('inmueble_id','es_encargado')
    def _compute_ambiente_id(self):        
        for record in self:
            record.ambiente_id_domain = json.dumps([('id' , 'in' , [])]) 
            dominio = [('inmueble_id','=',record.inmueble_id.id),('detalle_solicitud_id','=',record.detalle_solicitud_id.id),('state','=','libre')]            
            ambientes = self.env['vivienda.ambiente']
            if(record.es_encargado):
                ambientes = self.env['vivienda.ambiente'].search(dominio)                
            else:   
                numero_ambientes_reservadas = record.inmueble_id.numero_ambiente_reservada
                numero_ambientes = self.env['vivienda.ambiente'].search_count(dominio)
                numero_ambientes_disponibles = numero_ambientes - numero_ambientes_reservadas            
                if(numero_ambientes_disponibles > 0):
                    ambientes = self.env['vivienda.ambiente'].search(dominio,limit=numero_ambientes_disponibles)
            record.ambiente_id_domain = json.dumps([('id' , 'in' , ambientes.ids)])
       
    @api.depends('inmueble_id')
    def _compute_detalle_solicitud_id(self):
      for record in self:             
        if(record.inmueble_id):
            todas_ambientes = self.env['vivienda.ambiente_caracteristica'].search([('inmueble_id','=',record.inmueble_id.id)])         
            ambientes_ingresadas = record.solicitud_id.ambiente_ids.detalle_solicitud_id 
            restantes = todas_ambientes - ambientes_ingresadas   
            record.detalle_solicitud_id_domain = json.dumps([('id' , 'in' , restantes.ids)])
        else:
            record.detalle_solicitud_id_domain = json.dumps([('id' , 'in' , [])])
            
    @api.depends('cantidad','detalle_solicitud_id','fecha_inicio','fecha_fin','condicion')
    def _compute_vivienda_id(self):
        for record in self:
            total = 0.0
            record.precio_diario = 0.0

            if record.detalle_solicitud_id:
                precio_diario = record.detalle_solicitud_id.precio
                record.precio_diario = precio_diario

                if record.condicion == 'permanente':
                    # Sin fechas en permanente
                    total = record.cantidad * precio_diario
                elif record.fecha_inicio and record.fecha_fin:
                    fecha_inicio = fields.Date.from_string(record.fecha_inicio)
                    fecha_fin = fields.Date.from_string(record.fecha_fin)
                    dias = (fecha_fin - fecha_inicio).days

                    if dias < 0:
                        raise ValidationError("La fecha de salida es menor a la fecha de entrada")
                    elif dias == 0:
                        total = record.cantidad * precio_diario
                    else:
                        total = record.cantidad * dias * precio_diario

            record.precio_total = total
    
            
    
    @api.onchange('ambiente_ids')
    def _onchange_ambiente_ids(self):        
        for record in self:
            if(len(record.ambiente_ids) > record.cantidad):
                raise ValidationError("No puede exceder el número de ambientes solicitados por el usuario")
    
    @api.onchange('es_encargado')
    def _onchange_es_encargado(self):  
        for record in self:
            if not(record.es_encargado):
                record.ambiente_ids = False


























