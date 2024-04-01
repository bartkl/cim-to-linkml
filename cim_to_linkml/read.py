import sqlite3
import textwrap
from itertools import groupby
from operator import itemgetter

import cim_to_linkml.uml_model as uml_model


def read_uml_relations(conn: sqlite3.Connection) -> sqlite3.Cursor:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        """
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
        FROM t_connector

        ORDER BY Start_Object_ID
        """
    )

    rows = cur.execute(query)

    return rows


def read_uml_packages(conn: sqlite3.Connection) -> dict[uml_model.ObjectID, dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        """
        SELECT
            Package.Package_ID AS id,
            Package.Name AS name,
            Package.Parent_ID AS parent_id,
            Package.CreatedDate AS created_date,
            Package.ModifiedDate AS modified_date,
            -- Package.Notes AS notes, -- TODO: Using `Object.note`, but which one is the better choice?
            Object.author as author,
            Object.Note as note
        FROM t_package AS Package

        LEFT JOIN t_object AS Object
        ON Package.Package_ID = Object.Object_ID
        AND Object.Object_Type = "Package"
        """
    )

    rows = cur.execute(query)

    return {pkg["id"]: dict(pkg) for pkg in rows}


def read_uml_classes(
    conn: sqlite3.Connection,
) -> dict[uml_model.ObjectID, dict[uml_model.AttributeID, dict]]:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = textwrap.dedent(
        """
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
            Attribute.Type AS attr_range,
            Attribute.Notes AS attr_notes,
            Attribute.Stereotype AS attr_stereotype,
            Attribute."Default" AS attr_default
        FROM t_object AS Class

        LEFT JOIN t_attribute AS Attribute
        ON Class.Object_ID = Attribute.Object_ID

        WHERE Class.Object_Type = "Class"
        -- AND Class.Object_ID = 84
        ORDER BY Class.Object_ID, Attribute.ID
        """
    )
    rows = cur.execute(query)

    # return {
    #     class_id: list(map(dict, class_rows))
    #     for class_id, class_rows in groupby(rows, itemgetter("class_id"))
    # }

    # for class_id, class_rows in groupby(rows, itemgetter("class_id")):
    #     print(list(map(dict, class_rows)))

    return {
        class_id: {
            **{k: v for k, v in dict(class_rows[0]).items() if k.startswith("class_")},
            "attributes": {
                attr_id: {k: v for k, v in attr.items() if k.startswith("attr_")}
                for attr_id, attr_ in groupby(class_rows, itemgetter("attr_id"))
                if (attr := dict(next(attr_)))
            },
        }
        for class_id, class_rows_ in groupby(rows, itemgetter("class_id"))
        if (class_rows := list(class_rows_))
    }
