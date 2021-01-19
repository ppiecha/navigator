import cx_Oracle

# "localhost/orcl"
dsn = """(DESCRIPTION=
             (FAILOVER=on)
             (ADDRESS_LIST=
               (ADDRESS=(PROTOCOL=tcp)(HOST=sales1-svr)(PORT=1521))
               (ADDRESS=(PROTOCOL=tcp)(HOST=sales2-svr)(PORT=1521)))
             (CONNECT_DATA=(SERVICE_NAME=sales.example.com)))"""
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
print(type(dsn))
user_pwd = "oracle"

with cx_Oracle.connect("hr", user_pwd, dsn, encoding="UTF-8") as connection:
    print("dsn", connection.dsn)
    print("tns", connection.tnsentry)
    print("username", connection.username)
    print("version", connection.version)
    # connection.close()
    # print(connection.ping())
    with connection.cursor() as cursor:
        sql = """
              select owner, table_name from all_tables where owner = 'HR'
              """
        # cursor.parse(sql)
        try:
            cursor.execute(sql)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print("CONTEXT:", error.context)
            print("MESSAGE:", error.message)
            raise
        for col in cursor.description:
            print(col)
        for row in cursor:
            print(row)
        try:
            cursor.execute(sql)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print("CONTEXT:", error.context)
            print("MESSAGE:", error.message)
            raise
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        for row in cursor:
            print(row)

print("connected")