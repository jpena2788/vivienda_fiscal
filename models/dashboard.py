from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

class ViviendaDashboard(models.Model):
    _name = 'vivienda.dashboard'
    _description = 'Panel de Control de Vivienda'
    _auto = False

    name = fields.Char(string='Nombre', readonly=True)
    occupied_houses = fields.Integer(string='Viviendas Ocupadas')
    available_houses = fields.Integer(string='Viviendas Disponibles')
    occupied_beds = fields.Integer(string='Camas Ocupadas')
    available_beds = fields.Integer(string='Camas Disponibles')

    def init(self):

        tools.drop_view_if_exists(self.env.cr, 'vf_dashboard')

        self.env.cr.execute("""
            CREATE OR REPLACE VIEW vf_dashboard AS (

                SELECT
                    1 as id,
                    'Estado General' as name,

                    (
                        SELECT COUNT(*)
                        FROM vf_inmueble v
                        WHERE EXISTS (
                            SELECT 1
                            FROM vivienda_vivienda a
                            WHERE a.inmueble_id = v.id
                            AND a.active = true
                        )
                    ) as occupied_houses,

                    (
                        SELECT COUNT(*)
                        FROM vf_inmueble v
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM vivienda_vivienda a
                            WHERE a.inmueble_id = v.id
                            AND a.active = true
                        )
                    ) as available_houses,

                    0 as occupied_beds,
                    0 as available_beds

            )
        """)