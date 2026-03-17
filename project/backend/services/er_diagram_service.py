from typing import Optional
import os
import tempfile

from graphviz import Digraph

from backend.database.schema_manager import DatabaseSchema, TableSchema


def generate_er_diagram(schema: Optional[DatabaseSchema]) -> Optional[str]:
    """
    Generate an ER diagram for the given schema and return the path to a PNG file.
    Returns None if there is no schema.
    """
    if schema is None:
        return None

    dot = Digraph(comment=f"ER diagram for {schema.name}", format="png")

    # Tables as nodes
    for table in schema.tables:
        label_lines = [f"<<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\">"]
        label_lines.append(f"<TR><TD BGCOLOR=\"lightgray\"><B>{table.name}</B></TD></TR>")
        for col in table.columns:
            col_label = col.name
            if col.is_primary_key:
                col_label = f"<B>{col_label}</B>"
            label_lines.append(f"<TR><TD ALIGN=\"LEFT\">{col_label} : {col.type}</TD></TR>")
        label_lines.append("</TABLE>>")
        dot.node(table.name, "\n".join(label_lines), shape="plain")

    # Relationships (simple FK notation: references "other_table.column")
    for table in schema.tables:
        for col in table.columns:
            if col.references:
                ref_table = col.references.split(".")[0]
                dot.edge(table.name, ref_table, label=col.name)

    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"er_{schema.name}")
    rendered = dot.render(filename=output_path, cleanup=True)
    return rendered

