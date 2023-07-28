import re
from os import PathLike
from typing import Any, Optional

from more_itertools import chunked
from psycopg import sql, Connection
from psycopg.errors import Error as PgError
from psycopg.types.json import Jsonb


class ValuesTemplate:
    def __init__(self, template: str):
        if (not isinstance(template, str)) or (not template):
            raise Exception('Template cannot be empty')

        prep_template = re.sub(r'\)(\s*\))+', ')', template)

        self._mapped = False
        self._template = None

        if elements := (
                re.findall('\{(\w+)}(?:(::.+)(?:,|$))?', prep_template)
                or re.findall('%\((\w+)\)s(?:(::.+)(?:,|$))?', prep_template)
        ):
            self._mapped = True
        elif elements := re.findall('(%s)(?:(::.+)(?:,|$))?', prep_template):
            pass

        self._pattern_elements = elements

    @property
    def is_valid(self):
        return bool(self._pattern_elements)

    @property
    def is_mapped(self):
        return self._mapped

    @property
    def template(self):
        if self.is_valid:
            if self._mapped:
                return '(' + ', '.join(
                    '{%s}%s' % elem for elem in self._pattern_elements
                ) + ')'
            else:
                return '(' + ', '.join(
                    '{}%s' % elem for _, elem in self._pattern_elements
                ) + ')'


def adapt(elem: dict | list):
    if isinstance(elem, dict):
        for key, val in elem.items():
            if isinstance(val, dict):
                elem[key] = Jsonb(val)
    else:
        for i in range(len(elem)):
            val = elem[i]
            if isinstance(val, dict):
                elem[i] = Jsonb(val)

    return elem


def prepare_values(values: list[Any], vt: ValuesTemplate):
    if vt.is_mapped:
        return sql.SQL(',').join(
            [
                sql.SQL(vt.template).format(**item) for item in map(adapt, values)
            ]
        )
    else:
        return sql.SQL(',').join(
            [
                sql.SQL(vt.template).format(*item) for item in map(adapt, values)
            ]
        )


def execute_values(
        conn: Connection,
        /,
        query: str,
        data: list | tuple,
        template: str,
        *,
        page_size: Optional[int] = None,
        fetch: bool = False,
        debug: bool = False,
        dump_to: Optional[PathLike | str] = None
):
    template_obj = ValuesTemplate(
        template
    )
    assert template_obj.is_valid, 'Wrong template format'

    if page_size is None:
        page_size = len(data)

    prepared_query = re.sub(
        r'(?<=values)\s*\(\s*%s\s*\)',
        ' {}',
        query
    )

    fetched_data = []

    with conn.cursor() as cur:
        for part in chunked(data, page_size):
            query = sql.SQL(
                prepared_query
            ).format(
                prepare_values(part, template_obj)
            )
            try:
                cur.execute(query)
                if fetch:
                    fetched_data += cur.fetchall() or []

            except PgError as exc:
                conn.rollback()
                if debug:
                    query_string = query.as_string(conn)

                    if dump_to is not None:
                        with open(dump_to, 'w', encoding='utf-8') as f:
                            f.write(
                                query_string
                            )
                    else:
                        print(query_string)
                raise exc
        else:
            conn.commit()
    if fetched_data:
        return fetched_data
