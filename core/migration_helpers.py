"""Small PostgreSQL helpers used by legacy UUID migrations."""

from django.db import migrations


def convert_empty_integer_pk_to_uuid(model_label):
    """Convert a legacy integer PK only when no values would be discarded.

    These legacy migrations are being applied to tables created with bigint IDs
    while the current models use UUID IDs.  Incoming foreign keys are converted
    in the same transaction.  If a table contains data, abort rather than
    silently severing relationships; such a table requires an explicit ID
    mapping migration like Attendance's staged migration.
    """

    app_label, model_name = model_label.split(".")

    def forwards(apps, schema_editor):
        connection = schema_editor.connection
        model = apps.get_model(app_label, model_name)
        table = model._meta.db_table
        quote = connection.ops.quote_name

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM %s" % quote(table),
            )
            if cursor.fetchone()[0]:
                raise RuntimeError(
                    f"{table} contains data; refusing an unmapped bigint-to-UUID conversion"
                )

            cursor.execute(
                """
                SELECT child.relname, child_col.attname, con.conname,
                       pg_get_constraintdef(con.oid)
                FROM pg_constraint con
                JOIN pg_class child ON child.oid = con.conrelid
                JOIN pg_class parent ON parent.oid = con.confrelid
                JOIN pg_attribute child_col
                  ON child_col.attrelid = child.oid
                 AND child_col.attnum = con.conkey[1]
                WHERE con.contype = 'f'
                  AND parent.oid = %s::regclass
                  AND array_length(con.conkey, 1) = 1
                  AND array_length(con.confkey, 1) = 1
                """,
                [table],
            )
            incoming = cursor.fetchall()

            for child_table, child_column, _, _ in incoming:
                cursor.execute(
                    "SELECT COUNT(*) FROM %s WHERE %s IS NOT NULL"
                    % (quote(child_table), quote(child_column))
                )
                if cursor.fetchone()[0]:
                    raise RuntimeError(
                        f"{child_table}.{child_column} contains data; refusing to "
                        "convert it without an ID mapping"
                    )

            for child_table, child_column, constraint_name, _ in incoming:
                cursor.execute(
                    "ALTER TABLE %s DROP CONSTRAINT %s"
                    % (quote(child_table), quote(constraint_name))
                )
                cursor.execute(
                    "ALTER TABLE %s ALTER COLUMN %s TYPE uuid USING NULL::uuid"
                    % (quote(child_table), quote(child_column))
                )

            cursor.execute(
                "ALTER TABLE %s ALTER COLUMN id DROP IDENTITY IF EXISTS"
                % quote(table)
            )
            cursor.execute(
                "ALTER TABLE %s ALTER COLUMN id TYPE uuid USING gen_random_uuid()"
                % quote(table)
            )

            for child_table, child_column, constraint_name, definition in incoming:
                cursor.execute(
                    "ALTER TABLE %s ADD CONSTRAINT %s %s"
                    % (
                        quote(child_table),
                        quote(constraint_name),
                        definition,
                    )
                )

    return forwards


def _constraint_name(cursor, child_table, child_column, parent_table):
    cursor.execute(
        """
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class child ON child.oid = con.conrelid
        JOIN pg_class parent ON parent.oid = con.confrelid
        JOIN pg_attribute child_col
          ON child_col.attrelid = child.oid
         AND child_col.attnum = con.conkey[1]
        WHERE con.contype = 'f'
          AND child.relname = %s
          AND parent.relname = %s
          AND child_col.attname = %s
        LIMIT 1
        """,
        [child_table, parent_table, child_column],
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Foreign-key constraint disappeared during UUID migration")
    return row[0]
