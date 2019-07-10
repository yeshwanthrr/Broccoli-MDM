from flask import render_template, request
from broccoli_mdm import app, manager
from broccoli_mdm.init_models import *
from sqlalchemy.inspection import inspect
from broccoli_mdm.models import tables, connections, users, permissions
from flask_login import current_user, login_required, login_user, logout_user
import flask_restless
from sqlalchemy import func

def admin_access(**kw):
    if current_user.sysadmin != 1:
        raise flask_restless.ProcessingException(code=401) # Unauthorized


def check_permissions(**kw):
    if current_user.sysadmin == 1:
        print("A")
        return 1
    table_name = request.path.split("/")[-1:][0] #extracting tablename from URL
    curr_user = current_user.id if hasattr(current_user, "id") else None
    table = tables.query.filter(func.lower(tables.name) == table_name).first()
    permission = permissions.query.filter_by(table_id=table.id,user_id=curr_user).first()
    if permission is None:
        raise flask_restless.ProcessingException(code=401) 
    if request.method == "GET" and permission.read_flag == 1:
        pass
    elif request.method == "PUT" and permission.edit_flag == 1:
        pass
    elif request.method == "POST" and permission.edit_flag == 1:
        pass
    elif request.method == "DELETE" and permission.delete_flag == 1:
        pass
    else:
        raise flask_restless.ProcessingException(code=401) 

#Generate API for list of taybles
for obj in d:
    manager.create_api(d[obj], 
                        methods=['GET', 'POST', 'PUT', 'DELETE'], 
                        preprocessors={
                            'GET_MANY': [check_permissions],
                            'PUT': [check_permissions],
                            "DELETE" : [check_permissions]})


manager.create_api(tables, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], preprocessors={'GET_MANY': [admin_access],'PUT': [admin_access],"DELETE" : [admin_access]})

manager.create_api(connections, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],preprocessors={'GET_MANY': [admin_access],'PUT': [admin_access],"DELETE" : [admin_access]})

manager.create_api(users, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], exclude_columns=["password_md5", "salt"], preprocessors={'GET_MANY': [admin_access],'PUT': [admin_access],"DELETE" : [admin_access]})

manager.create_api(permissions, methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], preprocessors={'GET_MANY': [admin_access],'PUT': [admin_access],"DELETE" : [admin_access]})


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