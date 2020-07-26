from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Type
from dataclasses_json import dataclass_json
DB_ROOT = Path('db_files')

import shelve

@dataclass_json
@dataclass
class DBField:
    name: str
    type: Type


@dataclass_json
@dataclass
class SelectionCriteria:
    field_name: str
    operator: str
    value: Any


@dataclass_json
@dataclass
class DBTable:
    name: str
    fields: List[DBField]
    key_field_name: str

    def count(self) -> int:
        s = shelve.open(f'{self.name}.db')
        try:
            count_rows = len(s[self.name].keys())
        finally:
            s.close()
        return count_rows

    def insert_record(self, values: Dict[str, Any]) -> None:
        if None == values.get(self.key_field_name):
            raise ValueError
        s = shelve.open(f'{self.name}.db')
        try:
            s[self.name][values[self.key_field_name]] = dict
            for dbfield in self.fields:
                field = dbfield.name
                if field == self.key_field_name:
                    continue
                s[self.name][values[self.key_field_name]][field] = values[field] if values.get(field) else None
                values.pop(field)
            if 1 < len(values):
                self.delete_record(values[self.key_field_name])
                s.close()
                raise ValueError
        finally:
            s.close()

    def delete_record(self, key: Any) -> None:
        raise NotImplementedError


@dataclass_json
@dataclass
class DataBase:
    # Put here any instance information needed to support the API
    def create_table(self,
                     table_name: str,
                     fields: List[DBField],
                     key_field_name: str) -> DBTable:
        s = shelve.open(f'{table_name}.db', writeback=True)
        try:
            s[table_name] = dict
        finally:
            s.close()
        return DBTable(table_name, fields, key_field_name)

    def num_tables(self) -> int:
        raise NotImplementedError

    def get_table(self, table_name: str) -> DBTable:
        raise NotImplementedError

    def delete_table(self, table_name: str) -> None:
        raise NotImplementedError

    def get_tables_names(self) -> List[Any]:
        raise NotImplementedError

    def query_multiple_tables(
            self,
            tables: List[str],
            fields_and_values_list: List[List[SelectionCriteria]],
            fields_to_join_by: List[str]
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError
