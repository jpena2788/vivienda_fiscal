from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ReporteHistorialVivienda(models.AbstractModel):
    _name = 'report.vivienda_fiscal.reporte_historial_vivienda_template'
    _description = 'Datos reporte historial de vivienda'

    _MESES_CORTOS_ES = {
        1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
        7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC',
    }

    @classmethod
    def _format_fecha_corta(cls, fecha):
        if not fecha:
            return '/   /'
        return f"{fecha.day}/{cls._MESES_CORTOS_ES.get(fecha.month, '')}/{fecha.year}"

    @staticmethod
    def _format_tiempo(inicio, fin):
        delta = relativedelta(fin, inicio)
        partes = []
        if delta.years:
            partes.append(f"{delta.years} año(s)")
        if delta.months:
            partes.append(f"{delta.months} mes(es)")
        if delta.days or not partes:
            partes.append(f"{delta.days} día(s)")
        return ", ".join(partes)

    @staticmethod
    def _normalizar_componentes_tiempo(anos, meses, dias):
        # Normaliza acumulados para que dias no crezcan indefinidamente en el total.
        if dias >= 30:
            meses += dias // 30
            dias = dias % 30
        if meses >= 12:
            anos += meses // 12
            meses = meses % 12
        return anos, meses, dias

    @staticmethod
    def _get_fecha_inicio(asignacion):
        return asignacion.fecha_alta or asignacion.fecha_inicio or asignacion.fecha_solicitud

    @staticmethod
    def _get_fecha_fin(asignacion, hoy):
        if asignacion.fecha_baja:
            return asignacion.fecha_baja
        if asignacion.fecha_salida:
            return fields.Date.to_date(asignacion.fecha_salida)
        return hoy

    def _linea_desde_asignacion(self, asignacion, hoy):
        fecha_inicio = self._get_fecha_inicio(asignacion)
        fecha_alta = asignacion.fecha_alta or fecha_inicio
        fecha_fin_real = self._get_fecha_fin(asignacion, hoy)
        if fecha_inicio and fecha_fin_real < fecha_inicio:
            fecha_fin_real = hoy

        # Tiempo para A/M/D calculado hasta la fecha del reporte.
        delta_actual = relativedelta(hoy, fecha_alta) if fecha_alta else relativedelta()
        anos = max(delta_actual.years, 0)
        meses = max(delta_actual.months, 0)
        dias_actuales = max(delta_actual.days, 0)

        # Días calendario totales para referencia adicional.
        dias = max((hoy - fecha_alta).days, 0) if fecha_alta else 0
        return {
            'sector': asignacion.inmueble_id.sector_id.name or '',
            'bloque': asignacion.inmueble_id.bloque or '',
            'departamento': asignacion.inmueble_id.numero or '',
            'fecha_ingreso': self._format_fecha_corta(fecha_inicio),
            'fecha_salida': self._format_fecha_corta(fecha_fin_real) if asignacion.fecha_baja or asignacion.fecha_salida else '/   /',
            'motivo_salida': 'BAJA' if asignacion.fecha_baja or asignacion.fecha_salida else '',
            'anos': anos,
            'meses': meses,
            'dias': dias,
            'dias_actuales': dias_actuales,
        }

    def _build_report_data(self, docs, incoming_data=None):
        incoming_data = incoming_data or {}
        empleado_id = incoming_data.get('empleado_id')
        empleado = self.env['hr.employee'].browse(empleado_id) if empleado_id else self.env['hr.employee']
        usuario_actual = self.env.user
        usuario_texto = (usuario_actual.login or usuario_actual.name or '').upper()

        if empleado and not docs:
            docs = self.env['vivienda.inmueble_asignado'].search([
                ('personal_id', '=', empleado.id),
            ], order='fecha_alta asc, fecha_inicio asc, fecha_solicitud asc')

        hoy = fields.Date.context_today(self)
        docs = docs.filtered(lambda r: self._get_fecha_inicio(r)).sorted(key=lambda r: self._get_fecha_inicio(r))
        lineas = [self._linea_desde_asignacion(asignacion, hoy) for asignacion in docs]

        if not empleado and docs:
            empleado = docs[:1].personal_id

        total_dias = sum(linea.get('dias', 0) for linea in lineas)
        total_anos = sum(linea.get('anos', 0) for linea in lineas)
        total_meses = sum(linea.get('meses', 0) for linea in lineas)
        total_dias_actuales = sum(linea.get('dias_actuales', 0) for linea in lineas)
        total_anos, total_meses, total_dias_actuales = self._normalizar_componentes_tiempo(
            total_anos,
            total_meses,
            total_dias_actuales,
        )

        return {
            'empleado_nombre': empleado.name or '',
            'cedula': empleado.identification_id or '',
            'grado': str(getattr(empleado, 'grado', '') or ''),
            'fecha_reporte': self._format_fecha_corta(hoy),
            'codigo_reporte': usuario_texto,
            'archivo_fuente': usuario_actual.name or usuario_actual.login or '',
            'pagina': 1,
            'lineas': lineas,
            'total_dias': total_dias,
            'total_dias_actuales': total_dias_actuales,
            'total_anos': total_anos,
            'total_meses': total_meses,
            'total_literal': f"{total_anos} a.+ {total_meses} meses y {total_dias_actuales} dias",
        }

    def _get_report_values(self, docids, data=None):
        docs = self.env['vivienda.inmueble_asignado'].browse(docids)
        report_data = self._build_report_data(docs, data)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'vivienda.inmueble_asignado',
            'docs': docs,
            'report_data': report_data,
        }
