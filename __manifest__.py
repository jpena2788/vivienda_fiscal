{
    'name': 'Gestión de Vivienda Fiscal ARE',
    'version': '1.0',
    'summary': 'Sistema de gestión de viviendas fiscales',
    'author': 'DIRVIV',
    'category': 'Human Resources',
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': ['base', 'hr', 'th_gestion_organico', 'contacts'],
    'data': [
        'security/vf_security.xml',
        # 'security/security_vivienda_especificos.xml',
       
        'security/ir.model.access.csv',
        'data/vf_sequences.xml',
        'data/sector_tipo_inmueble_vivienda.xml',
        'data/inmuebles.xml',

        #menu
        'views/vivienda_menu_view.xml',
        #configuracion
        'views/configuracion/vivienda_catalogo_politicas_view.xml',
        'views/configuracion/vivienda_catalogo_caracteristica_view.xml',
        'views/configuracion/vivienda_sector_view.xml',
        'views/configuracion/vivienda_catalogo_piso_view.xml',
        'views/configuracion/vivienda_tipo_inmueble_view.xml',
        'views/configuracion/vivienda_hora_ingreso_salida_view.xml',
        'views/configuracion/vivienda_tipo_ambiente_view.xml',
        'views/configuracion/vivienda_requisito_view.xml',

        #reportes
        'views/reportes/reporte_historial_vivienda_template.xml',

        #wizards
        # 'wizard/inmueble_solicitud_politicas_wizard_view.xml', 
        # 'wizard/inmueble_solicitud_anulacion_wizard_view.xml',        
        'wizards/inmueble_informacion_ambiente_wizard_view.xml', 
        # 'wizard/inmueble_subir_comprobante_wizard_view.xml',  
        'wizards/vivienda_historial_wizard_view.xml',
        'wizards/vivienda_baja_wizard_view.xml',

        #registro
        'views/registro/vivienda_ambiente_inmueble_view.xml',
        
        'views/registro/vivienda_ambiente_caracteristica_view.xml',
        'views/registro/vivienda_inmueble_view.xml',
        'views/registro/vivienda_registro_asignacion_view.xml',
        

        #solicitud
        # 'views/solicitud/vivienda_solicitud_asignacion_view.xml',
        'views/solicitud/vivienda_mis_solicitudes_permanente_view.xml',
        'views/solicitud/vivienda_mis_solicitudes_temporal_view.xml',
        #'views/alojamiento_views.xml',
        # 'views/asignacion_vivienda_views.xml',
        # 'views/entorno_views.xml',
        #'views/mantenimiento_views.xml',
        #'views/pagos_views.xml',

        # 'reports/vivienda_report_templates.xml',
        # 'reports/vivienda_reports.xml',
       
        # 'views/dashboard_views.xml',
    
        
        

        
       
        
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
    'assets': {
        'web.assets_backend': [
            'vivienda_fiscal/static/src/css/vivienda.css',
        ],
    },
    'license': 'LGPL-3',
}
