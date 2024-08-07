import psycopg2
import comfy_extras.database as database


class PostgreSQLDriver(database.DatabaseDriver):
    connection = None
    cursor = None

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}}

    RETURN_TYPES = (database.DRIVER,)
    RETURN_NAMES = ('driver',)
    FUNCTION = "output"
    CATEGORY = "db"

    def output(self):
        return (self,)

    def connect(self, cc: database.ConnectionConfig):
        params = cc.model_dump()
        params['user'] = params.pop('username')
        self.connection = psycopg2.connect(**params)

    def close(self):
        self.connection.close()

    def execute(self, sql):
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)

    def commit(self):
        self.connection.commit()

    def get_result(self):
        return self.cursor.fetchall()


NODE_CLASS_MAPPINGS = {
    'PostgreSQL Driver': PostgreSQLDriver
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'PostgreSQL Driver': 'PostgreSQL Driver'
}
