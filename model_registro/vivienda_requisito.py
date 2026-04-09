from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ViviendaRequisito(models.Model):
    _name = 'vivienda.requisito'
    _description = 'Requisito de Vivienda'
    _order = 'sequence, id'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    tipo_captura = fields.Selection([
        ('archivo', 'Carga de archivo'),
        ('texto', 'Llenado por campo'),
    ], string='Tipo de captura', required=True, default='archivo')
    obligatorio = fields.Boolean(string='Obligatorio', default=True)
    condicion_aplica = fields.Selection([
        ('permanente', 'Permanente'),
        ('temporal', 'Temporal'),
        ('ambos', 'Ambos'),
    ], string='Aplica a', required=True, default='permanente')
    descripcion = fields.Text(string='Descripción / Ayuda')
    active = fields.Boolean(string='Activo', default=True)


class ViviendaSolicitudRequisito(models.Model):
    _name = 'vivienda.solicitud.requisito'
    _description = 'Requisito por Solicitud'
    _order = 'sequence, id'

    solicitud_id = fields.Many2one(
        'vivienda.inmueble_asignado',
        string='Solicitud',
        required=True,
        ondelete='cascade',
    )
    requisito_id = fields.Many2one(
        'vivienda.requisito',
        string='Requisito',
        ondelete='restrict',
    )
    sequence = fields.Integer(related='requisito_id.sequence', store=True, readonly=True)
    tipo_captura = fields.Selection(related='requisito_id.tipo_captura', store=True, readonly=True)
    obligatorio = fields.Boolean(related='requisito_id.obligatorio', store=True, readonly=True)
    state = fields.Selection(related='solicitud_id.state', string='Estado Solicitud', store=False, readonly=True)
    valor_texto = fields.Text(string='Valor')
    archivo = fields.Binary(string='Archivo')
    archivo_nombre = fields.Char(string='Nombre de archivo')
    aprobado = fields.Boolean(string='Aprobado', default=False)
    observacion_revision = fields.Text(string='Observación de revisión')

    _sql_constraints = [
        (
            'uniq_requisito_por_solicitud',
            'unique(solicitud_id, requisito_id)',
            'No puede repetir el mismo requisito en la solicitud.',
        ),
    ]


