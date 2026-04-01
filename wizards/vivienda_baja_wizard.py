from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ViviendaBajaWizard(models.TransientModel):
    _name = 'vivienda.baja.wizard'
    _description = 'Wizard de baja de asignacion de vivienda'

    solicitud_id = fields.Many2one(
        'vivienda.inmueble_asignado',
        string='Asignacion',
        required=True,
        readonly=True,
    )
    fecha_baja = fields.Date(
        string='Fecha de baja',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    motivo_baja = fields.Text(
        string='Motivo de baja',
        required=True,
    )

    @api.constrains('fecha_baja')
    def _check_fecha_baja(self):
        for record in self:
            if record.solicitud_id.fecha_alta and record.fecha_baja and record.fecha_baja < record.solicitud_id.fecha_alta:
                raise ValidationError('La fecha de baja no puede ser menor a la fecha de alta.')

    def action_confirmar_baja(self):
        self.ensure_one()
        if self.solicitud_id.state not in ['asignado', 'pagado', 'aprobado', 'llegada']:
            raise ValidationError('Solo se puede dar de baja una asignacion activa.')

        self.solicitud_id.action_estado_baja(
            fecha_baja=self.fecha_baja,
            motivo_baja=self.motivo_baja,
        )
        return {'type': 'ir.actions.act_window_close'}
