{
    'name': 'Gestión de Vivienda Fiscal ARE',
    'version': '1.0',
    'summary': 'Sistema de gestión de viviendas fiscales',
    'author': 'DIRVIV',
    'category': 'Human Resources',
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': ['base', 'hr', 'contacts'],
    'data': [
        'security/vf_security.xml',
        'security/ir.model.access.csv',
        'data/vf_sequences.xml',

        'views/vivienda_menu_view.xml',
        #configuracion
        'views/configuracion/vivienda_catalogo_politicas_view.xml',
        'views/configuracion/vivienda_catalogo_caracteristica_view.xml',
        'views/configuracion/vivienda_sector_view.xml',
        'views/configuracion/vivienda_catalogo_piso_view.xml',
        'views/configuracion/vivienda_tipo_inmueble_view.xml',
        #registro
        'views/registro/vivienda_ambiente_view.xml',
        'views/registro/vivienda_tipo_ambiente_view.xml',
        'views/registro/vivienda_tipo_ambiente_inmueble_view.xml',
        'views/registro/vivienda_inmueble_view.xml',

        #solicitud
        'views/solicitud/vivienda_solicitud_asignacion_view.xml',
        #'views/alojamiento_views.xml',
        # 'views/asignacion_vivienda_views.xml',
        # 'views/entorno_views.xml',
        #'views/mantenimiento_views.xml',
        #'views/pagos_views.xml',

        # 'reports/vivienda_report_templates.xml',
        # 'reports/vivienda_reports.xml',
       
        # 'views/dashboard_views.xml',
    
        
        # 'reports/reporte_historial_vivienda_template.xml',
        # 'wizards/vivienda_historial_wizard_view.xml',

        
       
        
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'vivienda_fiscal/static/src/css/vivienda.css',
        ],
    },
    'license': 'LGPL-3',
}
