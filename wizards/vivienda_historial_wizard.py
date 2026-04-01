from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ViviendaHistorialWizard(models.TransientModel):
    _name = 'vivienda.historial.wizard'
    _description = 'Consulta Historial Vivienda'

    @api.model
    def _is_admin_user(self):
        return (
            self.env.user.has_group('vivienda_fiscal.group_vivienda_administrador_general')
            or self.env.user.has_group('vivienda_fiscal.group_vivienda_administrador')
            or self.env.user.has_group('vivienda_fiscal.group_vivienda_encargado_solicitud')
        )

    @api.model
    def _default_empleado_id(self):
        if self._is_admin_user():
            return False
        return self.env.user.employee_id.id or False

    @api.model
    def _get_empleado_domain(self):
        if self._is_admin_user():
            return []
        if self.env.user.employee_id:
            return [('id', '=', self.env.user.employee_id.id)]
        return [('id', '=', 0)]

    empleado_id = fields.Many2one(
        'hr.employee',
        string='Persona',
        default=_default_empleado_id,
        domain=lambda self: self._get_empleado_domain(),
    )

    cedula = fields.Char(
        string="Cédula"
    )

    def action_generar_reporte(self):
        es_admin = self._is_admin_user()
        empleado_usuario = self.env.user.employee_id
        empleado = self.empleado_id

        if not empleado and self.cedula:
            dominio = [('identification_id', '=', self.cedula)]
            if not es_admin:
                dominio += self._get_empleado_domain()
            empleado = self.env['hr.employee'].search(
                dominio,
                limit=1
            )

        if not es_admin and not empleado:
            empleado = empleado_usuario

        if not empleado:
            raise ValidationError('Debe seleccionar una persona o ingresar una cédula válida.')

        if not es_admin:
            if not empleado_usuario:
                raise ValidationError('Su usuario no tiene un empleado asociado para generar este reporte.')
            if empleado.id != empleado_usuario.id:
                raise ValidationError('Solo puede exportar su propio historial de vivienda.')

        asignaciones = self.env['vivienda.inmueble_asignado'].search([
            ('personal_id', '=', empleado.id),
        ], order='fecha_alta asc, fecha_inicio asc, fecha_solicitud asc')

        return self.env.ref(
            'vivienda_fiscal.action_historial_vivienda'
        ).report_action(asignaciones, data={'empleado_id': empleado.id})