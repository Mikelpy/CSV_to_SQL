__doc__ = """contains 1 class for data migration for .csv to .db
basic-create: migrator=CSVMigrator(Path(example.db), "uesrs", "name VARCHAR(10), about VARCHAR(50)")"""

import sqlite3
from pathlib import Path
import logging
from logging import INFO, WARNING, ERROR
from contextlib import contextmanager
import re
import csv
import os

logging.basicConfig(filename="from_csv_migration.log")

class CSVMigrator:
    """
    Makes and extends database using .csv files
    """
    __SAFE_NAME_PAT = re.compile(r"[A-Za-z][A-Za-z0-9]*")
    def __init__(self, path: Path, table_name: str, create_columns: str, log_enabled: bool = False, log_level: int = INFO):
        self.__validate_name(table_name)

        self.log_enabled = log_enabled
        if self.log_enabled:
            self.logger = logging.getLogger(__class__.__name__)
            self.logger.setLevel(log_level)
        self.path = path
        self.table_name = table_name
        self.create_columns = create_columns

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        self.__init_database()
        self.__try_log(INFO, f"connected to: {self.table_name}, collumns: {self.get_existing_columns()}")
    
    def __init_database(self) -> None:
        query = f"""CREATE TABLE IF NOT EXISTS {self.table_name}
                            ({self.create_columns})"""
        self.cursor.execute(query)
        self.conn.commit()
    
    def __try_log(self, level: int, msg: str) -> None:
        if self.log_enabled and self.logger:
            self.logger.log(level, msg)
    
    def __validate_name(self, name: str) -> None:
        if not re.fullmatch(self.__SAFE_NAME_PAT, name):
            raise ValueError(f"invalid name {name}")
    
    @contextmanager
    def __transaction(self):
        try:
            yield
        except Exception as e:
            self.__try_log(ERROR, f"ROLLBACK: {e}")
            self.conn.rollback()
            raise
    
    def get_existing_columns(self) -> list[str]:
        self.cursor.execute(f"PRAGMA table_info({self.table_name})")
        return [row[1] for row in self.cursor.fetchall()]
    
    def extend(self, csv_path: Path, from_: list[str], target: list[str], batch_size: int = 16, encoding: str = "utf-8") -> dict:
        """
        :return: result migration stats
        """
        stats = {
            "total_rows": 0,
            "inserted": 0,
            "null_cells": 0
            }
        self.__try_log(INFO, f"starting migration from {csv_path.name} to {self.table_name}")
        existing_columns = self.get_existing_columns()

        # valiadation
        if len(from_) != len(target):
            raise (ValueError("len 'from_' argument must be = len 'to' argument"))
        if not csv_path.exists():
            raise (ValueError(f"{csv_path} not exist"))
        missing_in_db = [col_name for col_name in target if col_name not in existing_columns]
        if missing_in_db:
            raise (ValueError(f"columns {missing_in_db} not found in {self.table_name}"))
        
        # migration
        with open(csv_path, "r", encoding=encoding) as file:
            reader = csv.DictReader(file)
            csv_fieldnames = reader.fieldnames
            missing_in_csv = [col_name for col_name in from_ if col_name not in csv_fieldnames]
            if missing_in_csv:
                raise ValueError(f"columns {missing_in_csv} not found in CSV")
            
            placeholders = ", ".join(["?" for _ in target])
            query = f"INSERT INTO {self.table_name} ({", ".join(target)}) VALUES ({placeholders})"
            values = []
            batch = []
            with self.__transaction():
                for row in reader:
                    stats["total_rows"] += 1
                    for from_col in from_:
                        value = row.get(from_col)
                        if value is None or value.strip() == "":
                            stats["null_cells"] += 1
                        values.append(value)
                    batch.append(values)
                    values = []
                    if len(batch) >= batch_size:
                        self.cursor.executemany(query, batch)
                        stats["inserted"] += len(batch)
                        batch.clear()
                # last remaing batch
                if batch:
                    self.cursor.executemany(query, batch)
                    stats["inserted"] += len(batch)
        self.__try_log(INFO, f"Migration complited from {csv_path.name} to {self.table_name} >>> {stats}")
        return stats
    
    def get_total_info(self) -> dict:
        "returns info about database"
        total = {
            "MEMORY-USAGE(MB)": os.path.getsize(self.path)//1024,
            "TABLE": self.table_name,
            "COLLUMNS": self.get_existing_columns(),
        }
        return total
    
    def close(self) -> None:
        self.__try_log(INFO, f"TOTAL: {self.get_total_info()}")
        self.conn.close()
        self.__try_log(INFO, f"close connection: {self.table_name}\n")

    def __str__(self) -> str:
        return f"DBMaker(table={self.table_name}, columns={self.get_existing_columns()}, path={self.path})"

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
