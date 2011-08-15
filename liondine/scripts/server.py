from pymongo import Connection
#from sendgmail import 
import pymongo
connection = Connection()
db = connection.liondine

def faculty_signup(firstname="",lastname="",uni=""):
    if firstname and lastname and uni:
        faculty_collection = db.faculty
        dup = faculty_collection.find_one({"uni":uni})
        if dup:
                #already in DB
                #TODO
            raise ValueError("Duplicate uni!")
        else:
                #new uni
            try:
                faculty_collection.insert({"firstname":firstname,"lastname":lastname,"uni":uni},safe=True)
                return True
            except pymongo.errors.OperationFailure:
                    #pymongo problem
                return False
            except:
                    #other problem
                return False
    else:
            #redirect to registration
            #TODO
        return False
        
def student_signup(firstname="",lastname="",uni=""):
    if firstname and lastname and uni:
        student_collection = db.student
        dup = student_collection.find_one({"uni":uni})
        if dup == None:
                #new uni
            try:
                student_collection.insert({"firstname":firstname,"lastname":lastname,"uni":uni},safe=True)
                return True
            except pymongo.errors.OperationFailure:
                    #pymongo problem
                return False
            except:
                    #other problem
                return False
        else:
                #already in DB
                #error is not the best way to handle
                #TODO
            raise ValueError("duplicate uni found--already in DB")
        
    else:
            #redirect to registration
            #TODO
        return False

def create_appointment( date = 0, month = 0, year = 0, num=0, time = 0, dur = 0):
        #time is military, in minute e.g. 2PM would be 1400
        #duration is in minutes
        #TODO: Ensure that only professor can create appointment, and set prof_uni to it
        #TODO: Make sure professor exists
    DEFAULT = "mnn2104"

    prof_uni = DEFAULT
    if num > 0 and date > 0 and month > 0 and year > 0 and len(prof_uni) > 0:
        apptment_collection = db.appts
        faculty_collection = db.faculty
        query = {"date":date, "month":month, "year":year, "prof_uni" : prof_uni}
        appts = apptment_collection.find(query)
        bad_appts = []
        dur_hours = dur / 60
        dur_minutes = dur - dur_hours * 60
        for appt in appts:
            appt_time = appt["time"]
            appt_dur = appt["dur"]
            appt_dur_hours = appt_dur / 60
            appt_dur_minutes = dur - appt_dur_hours * 60

            this_appt_in_other_appt = (appt_time < time + dur_hours * 100 + dur_minutes and time <= appt_time)
            other_appt_in_this_appt = (time < appt_time + appt_dur_hours * 100 + appt_dur_minutes and  appt_time <= time)
            if this_appt_in_other_appt or other_appt_in_this_appt:
                bad_appts.append(appt)
        if bad_appts:
                #duplicate found
                #TODO should be handled more gracefully
                #redirect to registration
            raise ValueError("already have a date at this time")

        faculty = faculty_collection.find_one()
        if not faculty:
                #TODO should be handled more gracefully
                #redirect to registration
            raise ValueError("already have a date at this time")

        db_obj = {"date":date, "month":month, "year":year, "num":num, "prof_uni" : prof_uni}
        try:
            insertion = {"date":date, "month":month, "year":year, "prof_uni" : prof_uni, "time":time, "dur":dur, "num": num}
            apptment_collection.insert(insertion, safe=True)
            return True
        except pymongo.errors.OperationFailure:
                #pymongo problem
            return False
        except:
                #other problem
            return False        
    else:
            #TODO
            #redirect to registration
            #input error
        return False

def select_dict( dicty):
    return select_appointment(dicty["date"],dicty["month"],dicty["year"],dicty["prof_uni"], dicty["time"])

def select_appointment( date = 0, month = 0, year = 0, prof_uni = "", time = 0):
        #time is military, in minute e.g. 2PM would be 1400
        #duration is in minutes
        #TODO: pull in student uni from cookie
        #TODO: make sure student exists
    DEFAULT = "mnn2104"
    student_uni = DEFAULT
    if date > 0 and month > 0 and year > 0 and len(prof_uni) and len(student_uni) > 0:
        apptment_collection = db.appts
        student_collection = db.student
        query = {"date":date, "month":month, "year":year, "prof_uni" : prof_uni, "time": time}
        appt = apptment_collection.find_one(query)
        student = student_collection.find_one({"uni":student_uni})
        if not student or not appt or appt["num"] == 0:
                #appointment invalid
                #TODO should be handled more gracefully
                #redirect to registration
            raise ValueError("invalid appointment")
        try:
            update = {"$push": {"students":student_uni}, "$inc":{"num" : -1}}
            apptment_collection.update(query, update, safe=True)
            return True
        except pymongo.errors.OperationFailure:
                #pymongo problem
            pass
        except:
                #other problem
            pass                
    else:
            #TODO
            #input error
            #redirect to registration
        pass

def display_faculty():
    faculty_collection = db.faculty
    fac_lst = faculty_collection.find()
    stri = ""
    for fac in fac_lst:
        stri += str(fac)
    if stri:
        print "Contents of faculty collection: " + stri
    else:
        print "Faculty collection empty"

def display_students():
    student_collection = db.student
    stu_lst = student_collection.find()
    stri = ""
    for stu in stu_lst:
        stri += str(stu)
    if stri:
        print "Contents of student collection: " + stri
    else:
        print "Student collection empty"

def clear():
    db.faculty.drop()
    db.student.drop()
    db.appts.drop()

def user_finder(uni,collection):
    if collection.find_one({"uni":uni}):
        return True
    else:
        return False

def display_apptments():
    apptment_collection = db.appts
    appt_lst = apptment_collection.find()
    stri = ""
    for appt in appt_lst:
        stri += str(appt)
    print "Contents of appointment collection: " + stri
