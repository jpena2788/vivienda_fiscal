from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class CuentasBancarias(models.Model):
    _name = 'vivienda.cuentas_bancarias'
    _description = 'Cuentas bancarias'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _rec_name = "banco"


    cuentas = fields.Selection(
        [('ahorro', 'AHORRO'),
         ('corriente', 'CORRIENTE')],
        string='Tipo de cuenta', required=True)


    # tipo_cuenta = fields.Selection(
    #     selection='_get_cuentas', 
    #     string='Tipo de cuenta seleccionada'  
    #       )
    reparto_id = fields.Many2one(string='Reparto', comodel_name='res.company', default=lambda s: s.env.company.id, ondelete='restrict',tracking=True, required=True, 
    readonly=False 
    )    
    banco = fields.Char('Entidad bancaria', required=True, tracking=True)  
    numero_de_cuenta = fields.Char('Número de cuenta', required=True, tracking=True)  
    cedula = fields.Char('Número de cédula', required=True, tracking=True)  
    nombre = fields.Char('Nombre', required=True, tracking=True)  
    observacion = fields.Char('Observación', required=True, tracking=True)  

    # def _get_cuentas(self):
    #     cuentas = []
    #     if self.cuentas:
    #         cuentas = [(cuenta, cuenta) for cuenta in self.cuentas.split(',')]
    #     return cuentas


