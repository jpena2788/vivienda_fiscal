from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class Vivienda(models.Model):
    _name = 'vivienda.vivienda'
    _description = 'Vivienda Fiscal'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nuevo'))
    reparto_id = fields.Many2one(string='Reparto', comodel_name='res.company', default=lambda s: s.env.company.id, ondelete='restrict',tracking=True, required=True)    
    descripcion = fields.Text(string='Descripción', tracking=True )  
    tipo_inmueble_id = fields.Many2one('vivienda.tipo_inmueble', string='Tipo de Inmueble', required=True)

    inmueble_id = fields.Many2one('vivienda.inmueble', string='Inmueble', required=True)
    empleado_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True
    )

    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de fin')

    active = fields.Boolean(string='Asignación activa', default=True)

    estado = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('done', 'Finalizada')
    ], string='Estado', default='draft')

    
    motivo_salida = fields.Selection([
        ('baja','Baja'),
        ('traslado','Traslado'),
        ('renuncia','Renuncia'),
        ('otro','Otro')
    ],string='Motivo salida')

    tiempo_anios = fields.Integer(
        string="Años",
        compute="_compute_tiempo"
    )

    tiempo_meses = fields.Integer(
        string="Meses",
        compute="_compute_tiempo"
    )

    def _compute_tiempo(self):

        for rec in self:

            if rec.fecha_inicio:

                fecha_fin = rec.fecha_fin or date.today()

                diff = relativedelta(fecha_fin, rec.fecha_inicio)

                rec.tiempo_anios = diff.years
                rec.tiempo_meses = diff.months

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get('name','Nuevo') == 'Nuevo':

                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'vivienda.vivienda'
                )

        return super().create(vals_list)

    @api.constrains('inmueble_id','active')
    def _check_single_active(self):

        for rec in self:

            if not rec.active:
                continue

            existing = self.search([
                ('inmueble_id','=',rec.inmueble_id.id),
                ('active','=',True),
                ('id','!=',rec.id)
            ], limit=1)

            if existing:
                raise ValidationError(
                    "El inmueble ya tiene una asignación activa"
                )
            
    def action_activate(self):
        for rec in self:
            if rec.inmueble_id.current_vivienda_id and rec.inmueble_id.current_vivienda_id != rec:
                raise ValidationError(_('Actualmente hay otra asignación activa para este inmueble.'))

            rec.active = True
            rec.estado = 'active'

    def action_finish(self):
        for rec in self:
            rec.active = False
            rec.estado = 'done'
