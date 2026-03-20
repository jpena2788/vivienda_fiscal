from odoo import models, fields


class ViviendaHistorialWizard(models.TransientModel):
    _name = 'vf.historial.wizard'
    _description = 'Consulta Historial Vivienda'

    empleado_id = fields.Many2one(
        'hr.employee',
        string='Persona'
    )

    cedula = fields.Char(
        string="Cédula"
    )

    def action_generar_reporte(self):

        empleado = self.empleado_id

        if not empleado and self.cedula:
            empleado = self.env['hr.employee'].search(
                [('identification_id', '=', self.cedula)],
                limit=1
            )

        if not empleado:
            return

        asignaciones = self.env['vf.vivienda.asignacion'].search([
            ('empleado_id', '=', empleado.id)
        ])

        return self.env.ref(
            'vivienda_fiscal.action_historial_vivienda'
        ).report_action(asignaciones)