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

def view_root(context, request):
    return {'items':list(context), 'project':'liondine'}

def view_model(context, request):
    return {'item':context, 'project':'liondine'}

@view_config(route_name="faculty", renderer="templates/faculty.pt")
def faculty(request):
    return {}

@view_config(route_name="faculty_register", renderer="templates/faculty_reg.pt")
def faculty_register(request):
    mixed = request.POST.mixed()
    try:
        bool = faculty_signup(mixed["firstname"],mixed["lastname"],mixed["uni"])
    except ValueError: 
        return HTTPFound(location="../faculty")
    if bool:
        return {"msg":"ok"}
    else:
        return HTTPFound(location="../faculty")

@view_config(route_name="student", renderer="templates/student.pt")
def student(request):
    return {}

@view_config(route_name="student_register", renderer="templates/student_reg.pt")
def student_register(request):
    mixed = request.POST.mixed()
    try:
        my_bool = student_signup(mixed["firstname"],mixed["lastname"],mixed["uni"])
    except ValueError: 
        return HTTPFound(location="../student")
    if my_bool:
        return {"msg":"ok"}
    else:
        return HTTPFound(location="../student")

@view_config(route_name="appts", renderer="templates/appts.pt")
def appointment_view(request):
    connection = Connection()
    db = connection.liondine
    apptment_collection = db.appts
    appt_cursor = apptment_collection.find()

    faculty_collection = db.faculty
    faculty_cursor = faculty_collection.find()
    dicty = {}
    for faculty in faculty_cursor:
        dicty[faculty["uni"]] = (faculty["firstname"], faculty["lastname"])
    
    return {"appts":appt_cursor, "faculty":dicty}

@view_config(route_name="signup", renderer="templates/signup.pt")
def signup(request):
    mixed = request.POST.mixed()
    match = request.matchdict
    event_id = match["mongoid"]

    connection = Connection()
    db = connection.liondine
    apptment_collection = db.appts
    query = apptment_collection.find_one({"_id": ObjectId(event_id)})
    print query
    try:
        my_bool = select_dict(query)
    except ValueError: 
        return HTTPFound(location="../appts")
    if my_bool:
        return {"msg":"ok"}
    else:
        return HTTPFound(location="../appts")

@view_config(route_name="create", renderer="templates/create.pt")
def create(request):
    return {}

@view_config(route_name="create_conf", renderer="templates/create_conf.pt")
def create_conf(request):
    mixed = request.POST.mixed()
    
    try:
        my_bool = create_appointment(int(mixed["date"]), int(mixed["month"]), int(mixed["year"]), int(mixed["num"]), int(mixed["time"]), int(mixed["dur"]))
    except ValueError: 
        return HTTPFound(location="../appts")
    if my_bool:
        return {"msg":"ok"}
    else:
        return HTTPFound(location="../appts")
