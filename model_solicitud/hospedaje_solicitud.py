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


class Solicitud(models.Model):
    _name = 'hospedaje.solicitud'
    _description = 'Solucitud'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "hospedaje_id"
    
    seleccion_estado = [('draft', 'Borrador'), ('por_aprobar', 'Por aprobar'),('asignado', 'Asignado'),('pagado', 'Pagado'), ('aprobar', 'Aprobado'),('anular', 'Anulado'),('llegada', 'Llegada'),('fin', 'Finalizado')]
    state = fields.Selection(seleccion_estado, 'Estado Solicitud', readonly=True, default='draft', tracking=True)    
    hospedaje_id = fields.Many2one(string='Lugar de hospedaje', comodel_name='hospedaje.hospedaje', ondelete='restrict', tracking=True, required=True)       
    hora_entrada = fields.Float("Hora de entrada", required=True, readonly=True, help = "Campo de tipo fecha" )
    hora_salida = fields.Float("Hora de salida", required=True, readonly=True)
    precio = fields.Float(string="Precio", required=True, compute = "_compute_precio_id", readonly=True, store=True)
    personal_id = fields.Many2one(string='Personal', comodel_name='hr.employee', ondelete='restrict', tracking=True, required=True,
                                  default=lambda self: self.env.user.employee_id.id)
    reparto_id = fields.Many2one('res.company', 'Reparto', compute = "_compute_hospedaje_id", readonly=True, store=True,)
    user_id = fields.Many2one('res.users', 'Usuario', related='personal_id.user_id', readonly=True, store=True, required=True)     
    hospedaje_id_domain = fields.Char ( compute = "_compute_hospedaje_id" , readonly = True, store = False, )
    email = fields.Char(string='Email', store=True, readonly=True, compute = "_compute_hospedaje_id")
    cedula_identidad = fields.Char(string='Cédula de identidad', store=True, readonly=True, compute = "_compute_hospedaje_id")
    telefono = fields.Char(string='Teléfono', store=True, readonly=True, compute = "_compute_hospedaje_id")  
    direccion = fields.Char(string='Dirección', store=True,  readonly=True, compute = "_compute_hospedaje_id") 
    fecha_solicitud = fields.Date(string='Fecha de Solicitud', required=True, default=datetime.today(),readonly=True )  
    fecha_aprobacion = fields.Date('Fecha aprobación',  readonly=True)
    dias_pago = fields.Integer(string='Días disponibles para pagar reserva',)
    dias_transcurridos = fields.Integer(string='Días transcurridos', required=True,default=0)    
    fecha_inicio = fields.Date(string='Fecha de entrada', required=True )
    fecha_fin = fields.Date(string='Fecha de salida', required=True )    
    observacion = fields.Text(string='Observación', )    
    motivo_rechazo = fields.Text('Motivo de anulación')    
    aceptacion_termino = fields.Boolean(string='aceptación terminos',)  
    dependiente_ids = fields.Many2many(string='Dependientes', comodel_name='hr.employee.padres', relation='hospedaje_solicitud_dependientes_rel',
                                       column1='solicitud_id', column2='dependiente_id', domain="[('employee_id','=',personal_id)]")
    tipo_habitacion_ids = fields.One2many(string='Tipos de habitaciones', comodel_name='hospedaje.solicitud_tipo_habitacion', inverse_name='solicitud_id',)
    tipo_habitacion_cliente_ids = fields.One2many(string='Tipos de habitaciones', comodel_name='hospedaje.solicitud_tipo_habitacion', inverse_name='solicitud_id',)
    tipo_habitacion_operador_ids = fields.One2many(string='Tipos de habitaciones', comodel_name='hospedaje.solicitud_tipo_habitacion', inverse_name='solicitud_id',)  
    archivos_adjuntos= fields.Binary( string='Comprobante:')
    observacion = fields.Text('Observación')
    es_encargado = fields.Boolean(string='Es Encargado',help="Bandera usada para saber si el que creo la solicitud es un solicitante o un encargado de solicitudes encargado = true, solicitante=false")
    band_cobrar = fields.Boolean(string='Cobrado',help="Bandera usada para llevar un control de las solicitudes cobradas true cobradas, false no cobradas")      
    fecha_pago = fields.Datetime('Fecha de pago',  readonly=True)
    fecha_llegada = fields.Datetime('Fecha llegada',  readonly=True)
    fecha_salida = fields.Datetime('Fecha salida',  readonly=True)
    es_archivar = fields.Boolean(string='Archivar',default=False)
    
    warning = {
        'title': 'Mensaje de error',
        'message' : ''
         }    
    
    @api.constrains('tipo_habitacion_ids','tipo_habitacion_operador_ids')
    def _check_habitacion(self):
        for record in self:
            if(len(record.tipo_habitacion_ids)==0):
                raise ValidationError("Por favor seleccione por lo menos un tipo de habitación")   
            
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
        res = super(Solicitud, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
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
        if self.user_has_groups('hospedaje.group_hospedaje_administrador_general'):
            _condicion = [(1,'=',1)]
        elif self.user_has_groups('hospedaje.group_hospedaje_encargado_solicitud'):
            _condicion = [('reparto_id','=',self.env.user.company_id.id),('state','not in',['draft','anular']),('es_archivar','=', False)]
        diccionario= {
                        'name': ('Solicitudes de hospedaje'),        
                        'domain': _condicion,
                        'res_model': 'hospedaje.solicitud',
                        'views': [(self.env.ref('hospedaje.view_hospedaje_solicitud_tree').id, 'tree'),(self.env.ref('hospedaje.view_hospedaje_solicitud_form').id, 'form')],
                        'search_view_id':[self.env.ref('hospedaje.view_hospedaje_solicitud_search').id, 'search'],                           
                        'view_mode': 'tree,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_hospedaje':1,'search_default_estado':1,'default_es_encargado':True},
                    } 
        return diccionario 
    
    @api.depends('personal_id')
    def _compute_hospedaje_id(self):
        for record in self:
            record.reparto_id = record.hospedaje_id.reparto_id
            record.email = record.personal_id.work_email
            record.cedula_identidad = record.personal_id.identification_id
            record.telefono = record.personal_id.mobile_phone            
            direccion = self.env['hr.employee.domicilio'].search([('estado','=', 'activo')],limit=1) 
            if (direccion):
                record.direccion = direccion[0].state_id.name + "/ " + direccion[0].ciudad_id.name + "/ " + direccion[0].domicilio
            _hospedaje = []
            if(record.es_encargado):                
                if(record.personal_id.escalafon_id):                   
                    self.env.cr.execute("select hospedaje_id from hospedaje_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall()   
                    _hospedaje_reparto = []                  
                    for linea in res:                                   
                        _hospedaje_reparto.append(linea['hospedaje_id'])
                    _hospedaje = self.env['hospedaje.hospedaje'].search([('id','in',_hospedaje_reparto),('reparto_id','=',self.env.company.id)]).ids 
                if (record.personal_id.escalafon_id) and self.user_has_groups('hospedaje.group_hospedaje_administrador'):                    
                    self.env.cr.execute("select hospedaje_id from hospedaje_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall() 
                    for linea in res:                                   
                        _hospedaje.append(linea['hospedaje_id'])
            else:    
                if(record.personal_id.escalafon_id):               
                    self.env.cr.execute("select hospedaje_id from hospedaje_escalafon_rel where escalafon_id = {}".format(str(record.personal_id.escalafon_id.id)))
                    res = self.env.cr.dictfetchall() 
                    for linea in res:                                   
                        _hospedaje.append(linea['hospedaje_id'])
            record.hospedaje_id_domain = json.dumps([('id' , 'in' , _hospedaje)])       
     
    @api.onchange('hospedaje_id')
    def _onchange_hospedaje_id(self):
        for record in self:     
            if(record.hospedaje_id):                
                dias_anticipacion = self.env['hospedaje.hospedaje'].browse(self.hospedaje_id.id).dia_anticipacion
                date = datetime.now()
                date += timedelta(days=int(dias_anticipacion)) 
                record.fecha_inicio = date                                
                horario = self.env['hospedaje.hora_entrada_salida'].search([],limit=1) 
                for tiempo in horario:                    
                    record.hora_entrada = tiempo.hora_entrada
                    record.hora_salida = tiempo.hora_salida  
                     
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
            if record.fecha_inicio:
                record.fecha_fin = record.fecha_inicio
                if not (self.user_has_groups('hospedaje.group_hospedaje_administrador_general') or self.user_has_groups('hospedaje.group_hospedaje_encargado_solicitud')):
                    anticipacion = self.env['hospedaje.hospedaje'].browse(self.hospedaje_id.id)
                    minimo_anticipacion = anticipacion.dia_anticipacion
                    maximo_anticipacion = anticipacion.dia_anticipacion_maximo
                    date = datetime.now()
                    date_min = date + timedelta(days=int(minimo_anticipacion)) 
                    date_max = date + timedelta(days=int(maximo_anticipacion))                    
                    if(record.fecha_inicio < date_min.date()):
                        record.fecha_inicio = date_min.date()   
                        record.warning['message'] ="La fecha de inicio no puede ser menor a {}".format(date_min.date())                      
                        return {'warning': self.warning}                      
                    if(record.fecha_inicio > date_max.date()): 
                        record.fecha_inicio = date_min.date()                          
                        record.warning['message'] ="La fecha de inicio no puede ser mayor a {}".format(date_max.date()) 
                        return {'warning': self.warning}     
                    if(record.fecha_fin < record.fecha_inicio):  
                        record.fecha_inicio = date_min.date()                        
                        record.warning['message'] ="La fecha de entrada no puede ser mayor a la fecha de salida"  
                        return {'warning': self.warning} 


    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        for record in self:
            if record.fecha_fin:
                if(record.fecha_fin < record.fecha_inicio): 
                    record.fecha_fin = record.fecha_inicio                 
                    self.warning['message'] ="La fecha de salida no puede ser menor a fecha de entrada {}".format(record.fecha_inicio)                   
                    return {'warning': self.warning} 
                                
    @api.onchange('personal_id')
    def _onchange_personal_id(self):
        self.hospedaje_id = False  
    
    def aprobar_solicitud(self):  
        self.band_cobrar = True
        self.action_estado_aprobado()


    def asignacion_solicitud(self):  
        _cantidad = 0
        for habitacion in self.tipo_habitacion_ids:
            _cantidad += habitacion.cantidad
        # raise ValidationError("llego {} - {}".format(_cantidad,len(self.tipo_habitacion_ids.habitacion_ids)))
        #no se valida por tipo de habitación porque ya esta en otra función onchange
        if(_cantidad != len(self.tipo_habitacion_ids.habitacion_ids)):
            raise ValidationError("No se cumple con la petición de habitacion(es) del usuario")
        else:  
            self.tipo_habitacion_ids.habitacion_ids.state = 'ocupado' 
            self.action_estado_asignado()
            
    
        
         
            
    def action_estado_por_aprobar(self):
        if(self.aceptacion_termino):
            self.dias_pago = self.hospedaje_id.dias_pago
            self.write({'state': 'por_aprobar'})
        return True
    
    def action_estado_pagado(self):  
        # self.tipo_habitacion_ids.habitacion_ids.state = 'ocupado'   
        self.band_cobrar = True   
        self.write({'state': 'pagado'})
        return True


    def action_estado_asignado(self):       
        self.write({'state': 'asignado', 'fecha_aprobacion': time.strftime('%Y-%m-%d %H:%M:%S')})  
        self.tipo_habitacion_ids.habitacion_ids.state = 'ocupado'       
        return True
    
    
    def action_estado_aprobado(self):       
        self.write({'state': 'aprobar', 'fecha_pago': time.strftime('%Y-%m-%d %H:%M:%S')})      
        return True

    def action_llegada(self): 
        self.write({'state': 'llegada', 'fecha_llegada': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    def action_salida(self):  
        self.tipo_habitacion_ids.habitacion_ids.state = 'limpieza'
        self.write({'state': 'fin', 'fecha_salida': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True   
    
    def action_archivar(self):       
        self.write({'es_archivar': True})
        return True
    
    
    def action_estado_por_anular(self):
        self.tipo_habitacion_ids.habitacion_ids.state = 'libre'
        self.write({'state': 'anular'})
        return True    
   
    @api.depends('tipo_habitacion_ids.precio_total')
    def _compute_precio_id(self):
        for habitacion in self:            
            total = 0.0
            for line in habitacion.tipo_habitacion_ids:
                total += line.precio_total
            habitacion.update({'precio': total})            
    
    @api.model
    def create(self, values):                 
        result = super(Solicitud, self).create(values)
        #  seleccion_estado = [('draft', 'Borrador'), ('por_aprobar', 'Por aprobar'),('pagado', 'Pagado'), ('aprobar', 'Aprobado'),('anular', 'Anulado'),('llegada', 'Llegada'),('fin', 'Finalizado'),('archivar','Archivar')]    
        solicitudes = self.env['hospedaje.solicitud'].search([('user_id','=',result.user_id.id),('id','!=',result.id),('state','in',['draft','por_aprobar','asignado','aprobar','pagado','llegada'])])            
        if solicitudes:
            raise ValidationError("Tiene solicitudes pendientes de procesar!!") 
        return result    
            
class SolicitudTipoHabitacion(models.Model):
    _name = 'hospedaje.solicitud_tipo_habitacion'
    _description = 'tipos de habitaciones por solicitud'
    _rec_name = "tipo_habitacion_id"
        
    sequence = fields.Integer(string='Sequence', help="Orden de habitación", index=True)
    solicitud_id = fields.Many2one('hospedaje.solicitud', string="Solicitud", ondelete='restrict')
    state = fields.Selection('Estado Solicitud', related='solicitud_id.state', readonly=True, store=True)     
    cantidad = fields.Integer(string='Cantidad', required=True, tracking=True)
    hospedaje_id = fields.Many2one(string='Lugar de hospedaje', comodel_name='hospedaje.hospedaje', ondelete='restrict', tracking=True, required=True)  
    tipo_habitacion_id_domain = fields.Char ( compute = "_compute_tipo_habitacion_id" , readonly = True,)     
    tipo_habitacion_id = fields.Many2one('hospedaje.tipo_habitacion_hospedaje', string="Tipo de habitación", ondelete='restrict', required=True,                                        
                                         domain="[('hospedaje_id','=',hospedaje_id)]", index=True, ) 
    fecha_inicio = fields.Date(string='Fecha de entrada', related='solicitud_id.fecha_inicio', readonly=True, store=True)
    fecha_fin = fields.Date(string='Fecha de salida', related='solicitud_id.fecha_fin', readonly=True, store=True ) 
    num_personas = fields.Integer(string='# personas', related='tipo_habitacion_id.num_personas', readonly=True, store=True)      
    precio_diario = fields.Float(string="Precio diario",compute = "_compute_hospedaje_id", readonly=True, store=True)
    precio_total = fields.Float(string="Precio total", compute = "_compute_hospedaje_id", readonly=True, store=True)    
    habitacion_id_domain = fields.Char (compute = "_compute_habitacion_id" , readonly = True, store = False, )     
    habitacion_ids = fields.Many2many(string='Habitaciones', comodel_name='hospedaje.habitacion', relation='tipo_habitacion_asignacion_habitacion_rel',
                                      column1='tipo_habitacion_id', column2='habitacion_id',)    
    es_encargado = fields.Boolean(string='Es Encargado', related='solicitud_id.es_encargado', readonly=False, store=True)
    
        
    _sql_constraints = [('name_unique', 'UNIQUE(solicitud_id,tipo_habitacion_id)', "No se permite duplicidad de tipos de habitación")]   
    
    def toggle_start(self):
        self.es_encargado = True

    
    @api.constrains('cantidad')
    def check_cantidad(self):
        for record in self:    
            if self.cantidad > 2:
             raise ValidationError("Solo pueden agregar hasta 2 tipos de habitaciones por persona")
            
    



    
    @api.depends('hospedaje_id','es_encargado')
    def _compute_habitacion_id(self):        
        for record in self:
            record.habitacion_id_domain = json.dumps([('id' , 'in' , [])]) 
            dominio = [('hospedaje_id','=',record.hospedaje_id.id),('tipo_habitacion_id','=',record.tipo_habitacion_id.id),('state','=','libre')]            
            habitaciones = self.env['hospedaje.habitacion']
            if(record.es_encargado):
                habitaciones = self.env['hospedaje.habitacion'].search(dominio)                
            else:   
                numero_habitaciones_reservadas = record.hospedaje_id.numero_habitacion_reservada
                numero_habitaciones = self.env['hospedaje.habitacion'].search_count(dominio)
                numero_habitaciones_disponibles = numero_habitaciones - numero_habitaciones_reservadas            
                if(numero_habitaciones_disponibles > 0):
                    habitaciones = self.env['hospedaje.habitacion'].search(dominio,limit=numero_habitaciones_disponibles)
            record.habitacion_id_domain = json.dumps([('id' , 'in' , habitaciones.ids)])
       
    @api.depends('hospedaje_id')
    def _compute_tipo_habitacion_id(self):
      for record in self:             
        if(record.hospedaje_id):
            todas_habitaciones = self.env['hospedaje.tipo_habitacion_hospedaje'].search([('hospedaje_id','=',record.hospedaje_id.id)])         
            habitaciones_ingresadas = record.solicitud_id.tipo_habitacion_ids.tipo_habitacion_id 
            restantes = todas_habitaciones - habitaciones_ingresadas   
            record.tipo_habitacion_id_domain = json.dumps([('id' , 'in' , restantes.ids)])
        else:
            record.tipo_habitacion_id_domain = json.dumps([('id' , 'in' , [])])
            
    @api.depends('cantidad','tipo_habitacion_id','fecha_inicio','fecha_fin')
    def _compute_hospedaje_id(self):
        for record in self:
            _precio = 0
            if (record.tipo_habitacion_id):
                dias = (record.fecha_fin - record.fecha_inicio).days
                record.precio_diario = self.env['hospedaje.tipo_habitacion_hospedaje'].browse(record.tipo_habitacion_id.id).precio                
                if(dias < 0):
                    raise ValidationError("La fecha de salida es menor a la fecha de entrada")
                elif(dias == 0):
                    _precio = record.cantidad * record.precio_diario
                else:
                    _precio = record.cantidad * dias * record.precio_diario                                    
            record.precio_total = _precio
            
    
    @api.onchange('habitacion_ids')
    def _onchange_habitacion_ids(self):        
        for record in self:
            if(len(record.habitacion_ids) > record.cantidad):
                raise ValidationError("No puede exceder el número de habitaciones solicitadas por el usuario")
    
    @api.onchange('es_encargado')
    def _onchange_es_encargado(self):  
        for record in self:
            if not(record.es_encargado):
                record.habitacion_ids = False
            
                
    
    
   
            
    
    
    
    
    
    
    
    
    
    
    
            
    
    
            
    
            
    
    
   
                