from scripts.server import faculty_signup
from scripts.server import student_signup
from scripts.server import select_appointment
from scripts.server import select_dict
from scripts.server import create_appointment

from pymongo.objectid import ObjectId
from pymongo import Connection

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import forget
from pyramid.security import remember
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from mongauth import Mongauth
from secret import MONGO_URL

import pprint

def view_model(context, request):
    return {'item':context, 'project':'liondine'}

@view_config(route_name="home", renderer="templates/home.pt")
def home(request):
    return redirect_authenticated({}, request)

@view_config(route_name="faculty", renderer="templates/faculty.pt")
def faculty(request):
    ret = {}
    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        if pop[0]["msg"] == "err":
            ret["err"] = "err"
        elif pop[0]["msg"] == "dup":
            ret["dup"] = "dup"
    return redirect_authenticated(ret, request)

@view_config(route_name="faculty_register", renderer="templates/faculty_reg.pt")
def faculty_register(request):
    mixed = request.POST.mixed()
    try:
        bool = faculty_signup(mixed["firstname"],mixed["lastname"],mixed["uni"],mixed["email"])
    except ValueError: 
        request.session.flash({"msg":"dup"})
        return HTTPFound(location="../faculty")
    if bool:
        register(mixed["uni"],mixed["pw"])
        headers = remember(request,mixed["uni"])
        return HTTPFound(location="../create", headers=headers)
    else:
        request.session.flash({"msg":"err"})
        return HTTPFound(location="../faculty")

@view_config(route_name="student", renderer="templates/student.pt")
def student(request):
    ret = {}
    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        if pop[0]["msg"] == "err":
            ret["err"] = "err"
        elif pop[0]["msg"] == "dup":
            ret["dup"] = "dup"
    return redirect_authenticated(ret, request)

@view_config(route_name="student_register", renderer="templates/student_reg.pt")
def student_register(request):
    mixed = request.POST.mixed()
    
    try:
        my_bool = student_signup(mixed["firstname"],mixed["lastname"],mixed["uni"], mixed["email"])
    except ValueError: 
        register(mixed["uni"],mixed["pw"])
        headers = remember(request,mixed["uni"])
        request.session.flash({"msg":"dup"})
        return HTTPFound(location="../student")
    if my_bool:
        return HTTPFound(location="../appts", headers=headers)
    else:
        request.session.flash({"msg":"err"})
        return HTTPFound(location="../student")

@view_config(route_name="appts", renderer="templates/appts.pt", permission="register")
def appointment_view(request):
    connection = Connection(MONGO_URL)
    db = connection.liondine
    apptment_collection = db.appts
    appt_cursor = apptment_collection.find({"num":{"$gt":0}})
    collection = db.users
    faculty_cursor = collection.find({"type":"faculty"})
    dicty = {}
    for faculty in faculty_cursor:
        dicty[faculty["uni"]] = (faculty["firstname"], faculty["lastname"])
    
    appts = [appt for appt in appt_cursor]
    appts = [appt for appt in appts if appt["prof_uni"] in dicty]
    
    ret = {"appts":appts, "faculty":dicty}

    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        if pop[0]["msg"] == "ok":
            ret["ok"] = "ok"
        else:
            ret["fail"] = "fail"

    if len(appts) == 0:
        ret["empty"] = True

    return ret

@view_config(route_name="fac_appts", renderer="templates/fac_appts.pt", permission="create")
def faculty_appointments(request):
    connection = Connection(MONGO_URL)
    db = connection.liondine
    apptment_collection = db.appts
    appt_cursor = apptment_collection.find({"prof_uni":authenticated_userid(request)})
    collection = db.users
    faculty_cursor = collection.find({"type":"faculty"})
    dicty = {}
    for faculty in faculty_cursor:
        dicty[faculty["uni"]] = (faculty["firstname"], faculty["lastname"])
    
    appts = [appt for appt in appt_cursor]
    appts = [appt for appt in appts if appt["prof_uni"] in dicty]
    
    ret = {"appts":appts, "faculty":dicty}

    if len(appts) == 0:
        ret["empty"] = True

    return ret

@view_config(route_name="st_appts", renderer="templates/st_appts.pt", permission="register")
def student_appointments(request):
    connection = Connection(MONGO_URL)
    db = connection.liondine
    apptment_collection = db.appts
    appt_cursor = apptment_collection.find({"students":authenticated_userid(request)})
    collection = db.users
    faculty_cursor = collection.find({"type":"faculty"})
    dicty = {}
    for faculty in faculty_cursor:
        dicty[faculty["uni"]] = (faculty["firstname"], faculty["lastname"])
    
    appts = [appt for appt in appt_cursor]
    appts = [appt for appt in appts if appt["prof_uni"] in dicty]
    
    ret = {"appts":appts, "faculty":dicty}

    if len(appts) == 0:
        ret["empty"] = True

    return ret

@view_config(route_name="logout")
def logout(request):
    headers = forget(request)
    return HTTPFound(location="../", headers=headers)

@view_config(route_name="signup", renderer="templates/signup.pt", permission="register")
def signup(request):
    mixed = request.POST.mixed()
    match = request.matchdict
    event_id = match["mongoid"]

    connection = Connection(MONGO_URL)
    db = connection.liondine
    apptment_collection = db.appts
    query = apptment_collection.find_one({"_id": ObjectId(event_id)})
    try:
        my_bool = select_dict(authenticated_userid(request), query)
    except ValueError: 
        request.session.flash({"msg":"error"})
        return HTTPFound(location="../appts")
    if my_bool:
        request.session.flash({"msg":"ok"})
    else:
        request.session.flash({"msg":"fail"})
    return HTTPFound(location="../appts")

@view_config(route_name="create", renderer="templates/create.pt", permission = "create")
def create(request):
    ret_val = {}
    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        msg = pop[0]["msg"]
        if msg == "ok":
            ret_val["ok"] = "ok"
        else:
            ret_val["fail"] = "fail"
    return ret_val

@view_config(route_name="create_conf", permission="create")
def create_conf(request):
    mixed = request.POST.mixed()
    try:
        uni = authenticated_userid(request)
        my_bool = create_appointment(uni,int(mixed["date"]), int(mixed["month"]), int(mixed["year"]), int(mixed["num"]), int(mixed["time"]), int(mixed["dur"]))
    except ValueError: 
        peek = request.session.flash({"msg":"error"})
        return HTTPFound(location="../create")
    if my_bool:
        peek = request.session.flash({"msg":"ok"})
        return HTTPFound(location="../create")
    else:
        peek = request.session.flash({"msg":"fail"})
        return HTTPFound(location="../create")

@view_config(route_name="fac_login", renderer="templates/fac_login.pt")
def fac_login(request):
    ret = {}
    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        if pop[0]["msg"] == "err":
            ret["err"] = "err"
    return redirect_authenticated(ret, request)

@view_config(route_name="fac_auth")
def fac_auth(request):
    mixed = request.POST.mixed()
    if auth(mixed["uni"],mixed["pw"]):
        headers = remember(request,mixed["uni"])
        return HTTPFound(location="../fac_appts", headers=headers)
    else:
        request.session.flash({"msg":"err"})
        return HTTPFound(location="../fac_login")

@view_config(route_name="st_login", renderer="templates/st_login.pt")
def st_login(request):
    ret = {}
    peek = request.session.peek_flash()
    if peek:
        pop = request.session.pop_flash()
        if pop[0]["msg"] == "err":
            ret["err"] = "err"
    return redirect_authenticated(ret, request)

@view_config(route_name="st_auth")
def st_auth(request):
    mixed = request.POST.mixed()
    if auth(mixed["uni"],mixed["pw"]):
        headers = remember(request,mixed["uni"])
        return HTTPFound(location="../st_appts", headers=headers)
    else:
        request.session.flash({"msg":"err"})
        return HTTPFound(location="../st_login")

def auth(username, pw):
    auth = Mongauth(Connection(MONGO_URL).liondine.auth)
    return auth.auth(username,pw)

def register(username, pw):
    auth_coll = Connection(MONGO_URL).liondine.auth
    auth = Mongauth(auth_coll)
    return auth.new(username,pw)

def redirect_authenticated(other, request):
    user = authenticated_userid(request)
    if user:
        user_type = Connection(MONGO_URL).liondine.users.find_one({"uni":user})["type"]
        if user_type == "faculty":
            return HTTPFound(location="../fac_appts")
        elif user_type == "student":
            return HTTPFound(location="../st_appts")
        else:
            return other
    else:
        return other
