import cherrypy
from pymongo import Connection
import pymongo
connection = Connection()
db = connection.liondine

class Index(object):
    def faculty_signup(self,firstname="",lastname="",uni=""):
        if firstname and lastname and uni:
            faculty_collection = db.faculty
            dup = faculty_collection.find_one({"uni":uni})
            if dup:
                #already in DB
                pass
            else:
                #new uni
                try:
                    faculty_collection.insert({"firstname":firstname,"lastname":lastname,"uni":uni},safe=True)
                except pymongo.errors.OperationFailure:
                    #pymongo problem
                    pass
                except:
                    #other problem
                    pass
        else:
            #redirect to registration
            pass
        
    faculty_signup.exposed = True

    def student_signup(self,firstname="",lastname="",uni=""):
        if firstname and lastname and uni:
            student_collection = db.student
            dup = student_collection.find_one({"uni":uni})
            if dup == None:
                #new uni
                try:
                    student_collection.insert({"firstname":firstname,"lastname":lastname,"uni":uni},safe=True)
                except pymongo.errors.OperationFailure:
                    #pymongo problem
                    pass
                except:
                    #other problem
                    pass                
            else:
                #already in DB
                #error is not the best way to handle
                raise ValueError("duplicate uni found--already in DB")
            
        else:
            #redirect to registration
            pass
    student_signup.exposed = True

    def test1(self):
        print "Interprets correctly"

    def test2(self):
        faculty_collection = db.faculty
        fac_lst = faculty_collection.find()
        stri = ""
        for fac in fac_lst:
            stri += str(fac)
        print "Contents of faculty collection: " + stri

    def test3(self):
        student_collection = db.student
        stu_lst = student_collection.find()
        stri = ""
        for stu in stu_lst:
            stri += str(stu)
        print "Contents of student collection: " + stri

    def test4(self):
        print "faculty join test"
        self.faculty_signup("Moses","Nakamura","mnn2104")
        
        faculty_collection = db.faculty
        self.user_finder("mnn2104",faculty_collection)
        faculty_collection.remove({"uni":"mnn2104"})
        self.user_finder("mnn2104",faculty_collection)

    def test5(self):
        print "student join test"
        self.student_signup("Moses","Nakamura","mnn2104")
        
        student_collection = db.student
        self.user_finder("mnn2104",student_collection)
        student_collection.remove({"uni":"mnn2104"})
        self.user_finder("mnn2104",student_collection)

    def test6(self):
        print "faculty already in db test"
        self.faculty_signup("Moses","Nakamura","mnn2104")
        try:
            self.faculty_signup("Moses","Nakamura","mnn2104")
            print "Should have thrown an exception"
        except ValueError:
            print "Success!"
        except:
            print "Something else is failing test 6"

    def clear(self):
        db.faculty.drop()
        db.student.drop()

    def user_finder(self,uni,collection):
        if collection.find_one({"uni":uni}):
            print "found user"
        else:
            print "didn't find user"

    def testSuite(self):
        self.test1()
        self.test2()
        self.test3()
        self.test4()
        self.test5()
        self.test6()
        self.test2()
        self.clear()

index = Index()    
index.testSuite()
