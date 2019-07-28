from flask import render_template, request, Response
from broccoli_mdm import app, manager
from broccoli_mdm.init_models import *
from sqlalchemy.inspection import inspect
from broccoli_mdm.models import tables, connections, users, permissions
from flask_login import current_user, login_required, login_user, logout_user
import flask_restless
from sqlalchemy import func


def check_permissions(**kw):
    if current_user.sysadmin == 1:
        return
    table_name = request.path.split("/")[-1:][0] #extracting tablename from URL
    curr_user = current_user.id if hasattr(current_user, "id") else None
    table = tables.query.filter(func.lower(tables.name) == table_name).first()
    permission = permissions.query.filter_by(table_id=table.id,user_id=curr_user).first()
    if permission is None:
        raise flask_restless.ProcessingException(code=401) 
    if request.method == "GET" and permission.read_flag == 1:
        return
    elif request.method == "PUT" and permission.edit_flag == 1:
        return
    elif request.method == "POST" and permission.edit_flag == 1:
        return
    elif request.method == "DELETE" and permission.delete_flag == 1:
        return
    else:
        raise flask_restless.ProcessingException(code=401) 

preprocessors=dict(GET_MANY=[check_permissions],
                    GET_SINGLE=[check_permissions], 
                    POST_SINGLE=[check_permissions],
                    PUT_SINGLE=[check_permissions], 
                    PUT_MANY=[check_permissions], 
                    DELETE_MANY=[check_permissions],
                    DELETE_SINGLE=[check_permissions])

tables_prepr=dict(PUT_SINGLE=[check_permissions], 
                    PUT_MANY=[check_permissions], 
                    DELETE_MANY=[check_permissions],
                    DELETE_SINGLE=[check_permissions])


#Generate API for list of taybles
for obj in d:
    manager.create_api(d[obj], 
                        methods=['GET', 'POST', 'PATCH', 'DELETE'], 
                        preprocessors=preprocessors,
                        results_per_page=0)


manager.create_api(tables, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], preprocessors=tables_prepr)

manager.create_api(connections, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],preprocessors=preprocessors)

manager.create_api(users, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], exclude_columns=["password_md5", "salt"], preprocessors=preprocessors)

manager.create_api(permissions, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], preprocessors=preprocessors)


@app.route('/api_service/pk/<class_name>')
def api_tech_pk(class_name):
    return inspect(eval(class_name)).primary_key[0].name

@app.route('/api_service/attributes/<class_name>')
def api_tech_attributes(class_name):
    return eval(class_name).getAttributes()


@app.route('/api_service/create_new_user', methods=["POST"])
def api_tech_create_new_user():
    input = request.get_json()
    if input["user_name"] != "" and input["email"] != "" and input["user_name"] != "":
        users.create_new_user(user_name=input["user_name"], email=input["email"],password=input["password"])
        return "success"

@app.route('/api_service/check_connection', methods=["POST"])
def api_tech_check_connection(connection_string=None):
    input = request.get_json()
    connection_string = input.get("connection_string") or connection_string
    try:
        from sqlalchemy import create_engine
        engine = create_engine(connection_string)
        con = engine.connect()
        con.execute("select 1")
        return Response("Connection success",status=200)
    except Exception as e:
        print(e)
        return Response("Can't connect to database: "+ str(e) ,status=400)
