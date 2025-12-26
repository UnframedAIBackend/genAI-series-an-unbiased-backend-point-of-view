from enum import Enum


class DatabaseEngine(str, Enum):
    NOSQL = "mongodb"
    SQL = "postgres"
