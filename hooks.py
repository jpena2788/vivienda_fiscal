def pre_init_hook(cr):
    # Rename legacy table to the new technical table name if it exists.
    cr.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.vivienda_ambiente_inmueble') IS NOT NULL
               AND to_regclass('public.vivienda_ambiente_caracteristica') IS NULL THEN
                ALTER TABLE vivienda_ambiente_inmueble RENAME TO vivienda_ambiente_caracteristica;
            END IF;
        END
        $$;
    """)

    # Keep sequence naming aligned after table rename when present.
    cr.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.vivienda_ambiente_inmueble_id_seq') IS NOT NULL
               AND to_regclass('public.vivienda_ambiente_caracteristica_id_seq') IS NULL THEN
                ALTER SEQUENCE vivienda_ambiente_inmueble_id_seq RENAME TO vivienda_ambiente_caracteristica_id_seq;
            END IF;
        END
        $$;
    """)
