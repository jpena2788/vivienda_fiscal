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
    _rec_name = "name"
    # seleccion_estado = [('draft', 'Borrador'), ('por_aprobar', 'Por aprobar'),('asignado', 'Asignado'),('pagado', 'Pagado'), ('aprobado', 'Aprobado'),('anular', 'Anulado'),('llegada', 'Llegada'),('baja', 'De Baja'),('fin', 'Finalizado'),('archivar','Archivar')]
    
    seleccion_estado = [('draft', 'Borrador'), ('anular', 'Anulado'), ('revision', 'Revisión'),('lista_espera', 'Lista de Espera'),('asignado', 'Asignado'),('baja', 'De Baja'), ('por_aprobar', 'Por aprobar'), ('aprobado', 'Aprobado'),('devuelto', 'Devuelto'),('rechazado', 'Rechazado'),('fin', 'Finalizado'),('archivar','Archivar')]
    name = fields.Char(string='Número de Solicitud', copy=False, default='SOLICITUD-DIRVIV-VIF-SIN NUMERO')
    state = fields.Selection(seleccion_estado, 'Estado Solicitud de Asignación', readonly=True, default='draft', tracking=True)    
    inmueble_id = fields.Many2one(string='Inmueble', comodel_name='vivienda.inmueble', ondelete='restrict', tracking=True)       
    hora_entrada = fields.Float("Hora de entrada", readonly=True, help = "Campo de tipo fecha" )
    hora_salida = fields.Float("Hora de salida", readonly=True)
    precio = fields.Float(string="Precio", default=0.0, compute="_compute_precio_id", readonly=True, store=True)
    personal_id = fields.Many2one(string='Personal', comodel_name='hr.employee', ondelete='restrict', tracking=True, required=True,
                                  default=lambda self: self.env.user.employee_id.id)
    personal_permitido_ids = fields.Many2many(
        'hr.employee',
        string='Personal permitido',
        compute='_compute_personal_permitido_ids',
        readonly=True,
    )
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
        string='Sector',
        store=True,
    )
    
    sector_temporal_dominio = fields.Char(compute='_compute_sector_dominio', store=False)
    sector_permanente_dominio = fields.Char(compute='_compute_sector_dominio', store=False)
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
    motivo_baja = fields.Text('Motivo de baja')
    motivo_rechazo = fields.Text('Motivo de anulación')    
    aceptacion_termino = fields.Boolean(string='Aceptación términos',)  
    dependiente_ids = fields.Many2many(string='Dependientes', comodel_name='hr.employee.hijos', relation='vivienda_solicitud_dependientes_rel', column1='solicitud_id', column2='dependiente_id', domain="[('employee_id','=',personal_id)]")
    requisito_line_ids = fields.One2many(
        'vivienda.solicitud.requisito',
        'solicitud_id',
        string='Requisitos',
    )
    
    ambiente_ids = fields.One2many(string='Ambientes',  comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)
    ambiente_cliente_ids = fields.One2many(string='Ambientes', comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)
    ambiente_operador_ids = fields.One2many(string='Ambientes', comodel_name='vivienda.detalle_solicitud_ambiente', inverse_name='solicitud_id',)  
   
    archivos_adjuntos= fields.Binary( string='Comprobante:')
    observacion = fields.Text('Observación')
    es_encargado = fields.Boolean(string='Es Encargado',help="Bandera usada para saber si el que creo la solicitud es un solicitante o un encargado de solicitudes encargado = true, solicitante=false")
    band_pagado = fields.Boolean(string='Pagado',help="Bandera usada para llevar un control de las solicitudes pagadas true pagadas, false no pagadas")      
    fecha_pago = fields.Datetime('Fecha de pago',  readonly=True)
    fecha_llegada = fields.Datetime('Fecha llegada',  readonly=True)
    fecha_salida = fields.Datetime('Fecha salida',  readonly=True)
    es_archivar = fields.Boolean(string='Archivar',default=False)
    es_solicitud_permanente = fields.Boolean(string='Es solicitud permanente', default=False)
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

    @api.depends('condicion', 'es_solicitud_permanente')
    def _compute_politicas_ids(self):
        for record in self:
            condicion_efectiva = record._condicion_efectiva()
            if condicion_efectiva:
                record.politicas_ids = self.env['vivienda.catalogo_politicas'].search([
                    ('condicion', 'in', [condicion_efectiva, 'ambos']),
                    ('active', '=', True),
                ])
            else:
                record.politicas_ids = self.env['vivienda.catalogo_politicas'].browse()

    @api.depends_context('uid')
    def _compute_personal_permitido_ids(self):
        user = self.env.user
        es_privilegiado = user.has_group('vivienda_fiscal.group_vivienda_administrador_general') or \
            user.has_group('vivienda_fiscal.group_vivienda_administrador') or \
            user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud')
        empleado_usuario = user.employee_id

        for record in self:
            if es_privilegiado:
                record.personal_permitido_ids = self.env['hr.employee'].search([])
            elif empleado_usuario:
                record.personal_permitido_ids = empleado_usuario
            else:
                record.personal_permitido_ids = False

    def _usuario_puede_gestionar_todo_el_personal(self):
        self.ensure_one()
        user = self.env.user
        return user.has_group('vivienda_fiscal.group_vivienda_administrador_general') or \
            user.has_group('vivienda_fiscal.group_vivienda_administrador') or \
            user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud')

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

    @api.constrains('personal_id')
    def _check_personal_autorizado(self):
        for record in self:
            if record._usuario_puede_gestionar_todo_el_personal():
                continue

            empleado_usuario = self.env.user.employee_id
            if not empleado_usuario:
                raise ValidationError('Su usuario no tiene empleado asociado. Contacte al administrador.')

            if record.personal_id != empleado_usuario:
                raise ValidationError('No tiene permisos para crear solicitudes a nombre de otro empleado.')

            
   
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
            _condicion = [('reparto_id','=',self.env.user.company_id.id)]
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

    def ver_asignaciones_temporal(self):
        result = self.ver_asignaciones()
        result['name'] = 'Alojamiento Temporal'
        result['domain'] = list(result.get('domain', [])) + [('condicion', '=', 'temporal')]
        return result

    def ver_asignaciones_permanente(self):
        _condicion = []
        user = self.env.user
        if user.has_group('vivienda_fiscal.group_vivienda_administrador_general') or \
                user.has_group('vivienda_fiscal.group_vivienda_administrador'):
            _condicion = [('es_solicitud_permanente', '=', True), ('es_archivar', '=', False)]
        elif user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud'):
            sectores = self.env['vivienda.sector'].search([('reparto_id', '=', user.company_id.id)])
            _condicion = [('es_solicitud_permanente', '=', True), ('es_archivar', '=', False), ('sector_id', 'in', sectores.ids)]
        diccionario= {
                        'name': ('Asignaciones de inmuebles Permanentes'),        
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
            if record.sector_id:
                _inmueble = self.env['vivienda.inmueble'].search([
                    ('id', 'in', _inmueble),
                    ('sector_id', '=', record.sector_id.id),
                ]).ids
            record.inmueble_id_domain = json.dumps([('id', 'in', _inmueble)])

    @api.depends()
    def _compute_sector_dominio(self):
        sectores_temporal = self.env['vivienda.inmueble'].search(
            [('condicion', '=', 'temporal')]
        ).mapped('sector_id').ids
        sectores_permanente = self.env['vivienda.inmueble'].search(
            [('condicion', '=', 'permanente')]
        ).mapped('sector_id').ids
        for record in self:
            record.sector_temporal_dominio = json.dumps([('id', 'in', sectores_temporal)])
            record.sector_permanente_dominio = json.dumps([('id', 'in', sectores_permanente)])

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        for record in self:
            if record.inmueble_id and record.inmueble_id.sector_id != record.sector_id:
                record.inmueble_id = False
            if record.es_solicitud_permanente and not record.inmueble_id:
                record._sync_requisitos_desde_catalogo(reset=False)

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
                record._sync_requisitos_desde_catalogo(reset=True)
            else:
                record._sync_requisitos_desde_catalogo(reset=True)
                     
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

    def _condicion_efectiva(self):
        """Retorna la condición efectiva del registro: usa el campo relacionado
        o 'permanente' si la solicitud fue creada desde la vista permanente."""
        return self.condicion or ('permanente' if self.es_solicitud_permanente else False)

    def _get_requisitos_catalogo(self):
        self.ensure_one()
        condicion = self._condicion_efectiva()
        if not condicion:
            return self.env['vivienda.requisito'].browse()
        return self.env['vivienda.requisito'].search([
            ('active', '=', True),
            ('condicion_aplica', 'in', [condicion, 'ambos']),
        ], order='sequence, id')

    def _sync_requisitos_desde_catalogo(self, reset=False):
        for record in self:
            condicion_efectiva = record._condicion_efectiva()
            # Un registro es "nuevo" si todavía no tiene id real en BD
            is_new = not record._origin.id

            if condicion_efectiva != 'permanente':
                if reset or is_new:
                    record.requisito_line_ids = [(5, 0, 0)]
                elif record.requisito_line_ids:
                    record.requisito_line_ids.unlink()
                continue

            requisitos = record._get_requisitos_catalogo()

            # Para registros nuevos o con reset: siempre reasignar mediante comandos ORM
            if reset or is_new:
                record.requisito_line_ids = [(5, 0, 0)] + [
                    (0, 0, {'requisito_id': req.id}) for req in requisitos
                ]
                continue

            # Registro ya guardado, sincronización incremental
            existentes = {line.requisito_id.id: line for line in record.requisito_line_ids if line.requisito_id}
            ids_catalogo = set(requisitos.ids)
            sobrantes = record.requisito_line_ids.filtered(
                lambda l: not l.requisito_id or l.requisito_id.id not in ids_catalogo
            )
            if sobrantes:
                sobrantes.unlink()
            nuevos = [
                (0, 0, {'requisito_id': req.id})
                for req in requisitos
                if req.id not in existentes
            ]
            if nuevos:
                record.write({'requisito_line_ids': nuevos})

    def _validar_requisitos_permanente(self):
        for record in self:
            if record._condicion_efectiva() != 'permanente':
                continue
            faltantes = []
            for line in record.requisito_line_ids.filtered('obligatorio'):
                if line.tipo_captura == 'archivo' and not line.archivo:
                    faltantes.append(line.requisito_id.name)
                if line.tipo_captura == 'texto' and not line.valor_texto:
                    faltantes.append(line.requisito_id.name)
            if faltantes:
                raise ValidationError(
                    'Complete los requisitos obligatorios antes de solicitar: %s' % ', '.join(faltantes)
                )

    #accion para vivienda
    def solicitar_inmueble(self):
        self._validar_requisitos_permanente()
        if not self.name or self.name == 'SOLICITUD-DIRVIV-VIF-SIN NUMERO':
            seq = self.env['ir.sequence'].next_by_code('vf.solicitud.vivienda') or 'SOLICITUD-DIRVIV-VIF-SIN NUMERO'
            self.write({'name': seq})
        self.action_revision_solicitud()

    #accion para vivienda
    def action_revision_solicitud(self):
        if not self.aceptacion_termino:
            raise ValidationError("Lee las políticas y acepta los términos para continuar")
        if self.state not in ('draft', 'devuelto'):
            raise ValidationError('Solo se puede enviar a revisión desde estado Borrador o Devuelto.')
        self.write({'state': 'revision'})
        return True

    def aprobar_solicitud(self):  
        if self.condicion != 'temporal':
            raise ValidationError('La accion Aprobar aplica solo para inmuebles temporales.')
        if self.state != 'revision':
            raise ValidationError('Solo se puede aprobar una solicitud en estado Revisión.')
        self.band_pagado = True
        self.action_estado_aprobado()
        
    
    def asignacion_solicitud(self):  
        if self.condicion != 'permanente':
            raise ValidationError('La accion Asignar aplica solo para inmuebles permanentes.')
        if self.state != 'revision':
            raise ValidationError('Solo se puede asignar una solicitud en estado Revisión.')
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
            self.write({'state': 'aprobado'})
        return True
    
    def action_estado_pagado(self):  
        # self.tipo_habitacion_ids.habitacion_ids.state = 'ocupado'   
        self.band_pagado = True   
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

    def action_abrir_wizard_baja(self):
        self.ensure_one()
        if self.condicion != 'permanente':
            raise ValidationError('La baja manual aplica solo para asignaciones de inmuebles permanentes.')
        if self.state != 'asignado':
            raise ValidationError('Solo se puede dar de baja una asignacion en estado Asignado.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dar de Baja',
            'res_model': 'vivienda.baja.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_solicitud_id': self.id,
            },
        }

    def action_estado_baja(self, fecha_baja=None, motivo_baja=None):
        for record in self:
            if record.condicion != 'permanente':
                raise ValidationError('La baja manual aplica solo para asignaciones de inmuebles permanentes.')
            fecha = fecha_baja or fields.Date.context_today(record)
            valores = {
                'state': 'baja',
                'fecha_baja': fecha,
                'motivo_baja': motivo_baja or False,
            }
            if not record.fecha_salida:
                valores['fecha_salida'] = fields.Datetime.now()
            record.write(valores)

            ambientes = record.ambiente_operador_ids.mapped('ambiente_ids')
            if not ambientes:
                ambientes = record.ambiente_ids.mapped('ambiente_ids')
            if ambientes:
                ambientes.write({'state': 'libre'})
        return True
    
    def action_salida(self):  
        if self.condicion != 'temporal':
            raise ValidationError('Finalizar aplica solo para asignaciones de inmuebles temporales.')
        if self.state != 'aprobado':
            raise ValidationError('Solo se puede finalizar cuando la asignacion esta Aprobada.')
        self.ambiente_ids.ambiente_ids.state = 'limpieza'
        self.write({'state': 'fin', 'fecha_salida': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True   
    
    def action_archivar(self):       
        self.write({'es_archivar': True})
        return True

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(
                    'Solo puede eliminar solicitudes en estado Borrador.'
                )
        return super().unlink()

    def action_eliminar(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError('Solo puede eliminar solicitudes en estado Borrador.')
        self.unlink()
        return {'type': 'ir.actions.act_window_close'}

    def action_lista_espera(self):
        for record in self:
            if record.state != 'revision':
                raise ValidationError('Solo se puede pasar a Lista de Espera desde estado Revisión.')
            record.write({'state': 'lista_espera'})
        return True

    def action_devolver(self):
        for record in self:
            if record.state != 'revision':
                raise ValidationError('Solo se puede devolver una solicitud en estado Revisión.')
            record.write({'state': 'devuelto'})
        return True

    def action_rechazar(self):
        for record in self:
            if record.state != 'revision':
                raise ValidationError('Solo se puede rechazar una solicitud en estado Revisión.')
            record.write({'state': 'rechazado'})
        return True

    def action_estado_por_anular(self):
        for record in self:
            if record.state not in ['draft', 'por_aprobar']:
                raise ValidationError('Solo se puede anular antes de aprobar (Borrador o Por aprobar).')
            record.ambiente_ids.ambiente_ids.state = 'libre'
            record.write({'state': 'anular'})
        return True    
    
    # -------------------------
    # COMPUTE PRECIO
    # -------------------------
    @api.depends('ambiente_ids.precio_total')
    def _compute_precio_id(self):
        for record in self:
            record.precio = sum(record.ambiente_ids.mapped('precio_total'))
           
    def _get_estados_bloqueantes(self):
        return ['por_aprobar', 'asignado', 'aprobado']

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
        if 'requisito_line_ids' in values:
            values['requisito_line_ids'] = [
                cmd for cmd in values['requisito_line_ids']
                if not (isinstance(cmd, (list, tuple)) and len(cmd) >= 3
                        and cmd[0] == 0 and not cmd[2].get('requisito_id'))
            ]
        result = super().create(values)
        if result._condicion_efectiva() == 'permanente':
            result._sync_requisitos_desde_catalogo(reset=False)
        return result

    def write(self, values):
        if 'requisito_line_ids' in values:
            values['requisito_line_ids'] = [
                cmd for cmd in values['requisito_line_ids']
                if not (isinstance(cmd, (list, tuple)) and len(cmd) >= 3
                        and cmd[0] == 0 and not cmd[2].get('requisito_id'))
            ]
        result = super().write(values)
        if 'inmueble_id' in values:
            self._sync_requisitos_desde_catalogo(reset=False)
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
                                         domain="[('inmueble_id','=',inmueble_id),('ambiente_id.cobro','=',True)]", index=True, ) 
    fecha_inicio = fields.Date(string='Fecha de entrada', related='solicitud_id.fecha_inicio',  store=True)
    fecha_fin = fields.Date(string='Fecha de salida', related='solicitud_id.fecha_fin',  store=True ) 
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

    @api.constrains('ambiente_ids', 'inmueble_id', 'detalle_solicitud_id')
    def _check_ambientes_existentes_y_validos(self):
        for record in self:
            if not record.ambiente_ids:
                continue

            if any(amb.inmueble_id != record.inmueble_id for amb in record.ambiente_ids):
                raise ValidationError("Solo puede seleccionar ambientes existentes del inmueble indicado.")

            ambiente_caracteristica = record.detalle_solicitud_id.ambiente_id
            if ambiente_caracteristica and any(amb.id != ambiente_caracteristica.id for amb in record.ambiente_ids):
                raise ValidationError("Los ambientes seleccionados deben corresponder al ambiente definido en la línea.")
            
    
   
    @api.depends('inmueble_id', 'detalle_solicitud_id', 'es_encargado')
    def _compute_ambiente_id(self):        
        for record in self:
            record.ambiente_id_domain = json.dumps([('id', 'in', [])])

            if not record.inmueble_id or not record.detalle_solicitud_id or not record.detalle_solicitud_id.ambiente_id:
                continue

            dominio = [
                ('inmueble_id', '=', record.inmueble_id.id),
                ('id', '=', record.detalle_solicitud_id.ambiente_id.id),
                ('cobro', '=', True),
                ('state', '=', 'libre'),
            ]
            ambientes = self.env['vivienda.ambiente']
            if(record.es_encargado):
                ambientes = self.env['vivienda.ambiente'].search(dominio)
            else:
                numero_ambientes_reservadas = record.inmueble_id.numero_ambiente_reservada
                numero_ambientes = self.env['vivienda.ambiente'].search_count(dominio)
                numero_ambientes_disponibles = numero_ambientes - numero_ambientes_reservadas
                if(numero_ambientes_disponibles > 0):
                    ambientes = self.env['vivienda.ambiente'].search(dominio, limit=numero_ambientes_disponibles)

            record.ambiente_id_domain = json.dumps([('id', 'in', ambientes.ids)])
       
    @api.depends('inmueble_id', 'solicitud_id.ambiente_ids.detalle_solicitud_id')
    def _compute_detalle_solicitud_id(self):
        for record in self:
            if record.inmueble_id:
                todas_ambientes = self.env['vivienda.ambiente_caracteristica'].search([
                    ('inmueble_id', '=', record.inmueble_id.id),
                    ('ambiente_id.cobro', '=', True),
                ])
                ambientes_ingresadas = record.solicitud_id.ambiente_ids.filtered(
                    lambda l: l.id != record.id
                ).mapped('detalle_solicitud_id')
                restantes = todas_ambientes - ambientes_ingresadas
                record.detalle_solicitud_id_domain = json.dumps([('id', 'in', restantes.ids)])
            else:
                record.detalle_solicitud_id_domain = json.dumps([('id', 'in', [])])
            
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

    @api.onchange('cantidad', 'detalle_solicitud_id', 'fecha_inicio', 'fecha_fin', 'condicion')
    def _onchange_recalcular_precios(self):
        self._compute_vivienda_id()
    
            
    
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


























