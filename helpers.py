def parse_user_input(data):
    return eval(data)  # dangerous use of eval

def connect_db():
    connection_string = "postgres://admin:secret@localhost/mydb"
    return connection_string
