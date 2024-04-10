import sqlite3
import textwrap


NON_NORMATIVE_PACKAGE_IDS = [
    5,
    27,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    80,
    81,
    82,
    85,
    88,
    89,
    90,
    91,
    92,
    94,
    96,
    98,
    99,
    100,
    101,
    105,
    106,
    107,
    110,
    112,
    113,
    114,
    116,
    117,
    118,
    121,
    122,
    124,
    125,
    129,
    130,
    131,
    138,
    139,
    144,
    150,
    151,
    155,
    157,
    158,
    160,
    162,
    164,
    167,
    168,
    171,
]

NON_NORMATIVE_PACKAGE_IDS_SQL_LIST = ", ".join(map(str, NON_NORMATIVE_PACKAGE_IDS))


def read_uml_project(
    conn: sqlite3.Connection,
) -> tuple[sqlite3.Cursor, sqlite3.Cursor, sqlite3.Cursor]:
    uml_package_results = read_uml_packages(conn)
    uml_class_results = read_uml_classes(conn)
    uml_relation_results = read_uml_relations(conn)

    return uml_package_results, uml_class_results, uml_relation_results


def read_uml_relations(conn: sqlite3.Connection) -> sqlite3.Cursor:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        f"""
        SELECT
            Connector_ID AS id,
            Connector_Type AS type,
            Start_Object_ID AS start_object_id,
            End_Object_ID AS end_object_id,
            Direction AS direction,
            SubType AS sub_type,
            SourceCard AS source_card,
            SourceRole AS source_role,
            SourceRoleNote AS source_role_note,
            DestCard AS dest_card,
            DestRole AS dest_role,
            DestRoleNote AS dest_role_note
        FROM t_connector AS Relation

        INNER JOIN t_object AS FromClass
        ON start_object_id = FromClass.Object_ID

        INNER JOIN t_object AS ToClass
        ON end_object_id = ToClass.Object_ID


        WHERE type  NOT IN ("Dependency", "NoteLink")
        AND FromClass.Package_ID NOT IN ({NON_NORMATIVE_PACKAGE_IDS_SQL_LIST})
        AND ToClass.Package_ID NOT IN ({NON_NORMATIVE_PACKAGE_IDS_SQL_LIST})

        ORDER BY id
        """
    )
    rows = cur.execute(query)

    return rows


def read_uml_packages(conn: sqlite3.Connection) -> sqlite3.Cursor:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        f"""
        SELECT
            Package.Package_ID AS id,
            Package.Name AS name,
            Package.Parent_ID AS parent_id,
            Package.CreatedDate AS created_date,
            Package.ModifiedDate AS modified_date,
            Object.Author as author,
            Object.Note as note
        FROM t_package AS Package

        LEFT JOIN t_object AS Object
        ON Package.Package_ID = Object.Object_ID

        WHERE Package.Package_ID NOT IN ({NON_NORMATIVE_PACKAGE_IDS_SQL_LIST})


        ORDER BY id
        """
    )
    rows = cur.execute(query)

    return rows


def read_uml_classes(conn: sqlite3.Connection) -> sqlite3.Cursor:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        f"""
        SELECT
            Class.Object_ID AS class_id,
            Class.Name AS class_name,
            Class.Author AS class_author,
            Class.Package_ID AS class_package_id,
            Class.CreatedDate AS class_created_date,
            Class.ModifiedDate AS class_modified_date,
            Class.Stereotype AS class_stereotype,
            Class.Note AS class_note,
            Attribute.ID AS attr_id,
            Attribute.Name AS attr_name,
            Attribute.LowerBound AS attr_lower_bound,
            Attribute.UpperBound AS attr_upper_bound,
            Attribute.Type AS attr_type,
            Attribute.Notes AS attr_notes,
            Attribute.Stereotype AS attr_stereotype,
            Attribute."Default" AS attr_default
        FROM t_object AS Class

        LEFT JOIN t_attribute AS Attribute
        ON Class.Object_ID = Attribute.Object_ID

        LEFT JOIN t_object AS TypeClass
        ON Attribute.Classifier = TypeClass.Object_ID

        WHERE Class.Object_Type = "Class"
        AND Class.Package_ID NOT IN ({NON_NORMATIVE_PACKAGE_IDS_SQL_LIST})
        AND TypeClass.Package_ID NOT IN ({NON_NORMATIVE_PACKAGE_IDS_SQL_LIST})

        ORDER BY Class.Object_ID, Attribute.Name
        """
    )
    rows = cur.execute(query)

    return rows
