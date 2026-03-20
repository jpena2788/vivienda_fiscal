from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ViviendaMantenimiento(models.Model):
    _name = 'vivienda.mantenimiento'
    _description = 'Mantenimiento de Vivienda/Alojamiento'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    descripcion = fields.Text(string='Descripción', required=True)
    inmueble_id = fields.Many2one('vf.inmueble', string='Inmueble')
    alojamiento_id = fields.Many2one('vf.alojamiento.naval', string='Alojamiento')
    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_finalizacion = fields.Date(string='Fecha de finalización')
    estado = fields.Selection([('pending', 'Pendiente'), ('in_progress', 'En Proceso'), ('done', 'Finalizado')], string='Estado', default='pending')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vivienda.mantenimiento') or _('Nuevo')
        return super().create(vals)