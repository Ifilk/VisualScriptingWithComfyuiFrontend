import os
from abc import ABCMeta, abstractmethod

from pydantic import BaseModel

CONNECTION = 'db.CONNECTION'
RESULT = 'db.RESULT'
CONFIG = 'db.CONFIG'
DRIVER = 'db.DRIVER'


class ConnectionConfig(BaseModel):
    username: str
    password: str
    host: str
    database: str
    port: int


class DatabaseDriver(metaclass=ABCMeta):
    @abstractmethod
    def connect(self, cc: ConnectionConfig):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute(self, sql):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def get_result(self):
        pass


class ConnectionConfigNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "user": ("STRING", {"dynamicPrompts": True}),
            "password": ("STRING", {"default": "*", "dynamicPrompts": True}),
            "database": ("STRING", {"dynamicPrompts": True}),
            "host": ("STRING", {"default": "localhost", "dynamicPrompts": True}),
            "port": ("STRING", {"default": "5432", "dynamicPrompts": True}),
        }}

    RETURN_TYPES = (CONFIG,)
    RETURN_NAMES = ('connection',)
    FUNCTION = "connect"
    CATEGORY = "db"

    def connect(self, user, password, database, host="localhost", port="5432"):
        if password == '*':
            password = os.getenv('DB_PSQL_PASSWORD')
        return (ConnectionConfig(username=user,
                                 password=password,
                                 host=host,
                                 database=database,
                                 port=port),)


class DatabaseNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "config": (CONFIG, ),
            "driver": (DRIVER, ),
            "sql": ("STRING", {"multiline": True, "dynamicPrompts": True}),
        }}

    RETURN_TYPES = (RESULT,)
    RETURN_NAMES = ('result',)
    FUNCTION = "exec"
    CATEGORY = "db"

    def exec(self, config: ConnectionConfig, driver: DatabaseDriver, sql):
        driver.connect(config)
        driver.execute(sql)
        driver.commit()
        return (driver.get_result(), )


NODE_CLASS_MAPPINGS = {
    'ConnectionConfigNode': ConnectionConfigNode,
    'DatabaseNode': DatabaseNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'ConnectionConfigNode': 'Connection Configure',
    'DatabaseNode': 'Database'
}
