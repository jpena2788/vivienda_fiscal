from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ViviendaPagos(models.Model):
    _name = 'vf.vivienda.pagos'
    _description = 'Pagos de Vivienda'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nuevo'))
    vivienda_id = fields.Many2one('vf.vivienda.fiscal', string='Vivienda')
    alojamiento_id = fields.Many2one('vf.alojamiento.naval', string='Alojamiento')
    fecha = fields.Date(string='Fecha de pago', required=True)
    monto = fields.Monetary(string='Monto', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True,
                                  default=lambda self: self.env.company.currency_id)
    description = fields.Text(string='Descripción')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vf.vivienda.pagos') or _('Nuevo')
        return super().create(vals)

