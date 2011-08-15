import unittest
from pymongo import Connection
from server import faculty_signup
from server import student_signup
from server import clear
from server import user_finder
from server import create_appointment
from server import select_appointment

connection = Connection()
db = connection.liondine

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        clear()

    def test_afaculty_join(self):
        faculty_signup("Moses","Nakamura","mnn2104")
        faculty_collection = db.faculty
        self.assertTrue(user_finder("mnn2104",faculty_collection))
        faculty_collection.remove({"uni":"mnn2104"})
        self.assertFalse(user_finder("mnn2104",faculty_collection))

    def test_bstudent_join(self):
        student_signup("Moses","Nakamura","mnn2104")
        
        student_collection = db.student
        self.assertTrue(user_finder("mnn2104",student_collection))
        student_collection.remove({"uni":"mnn2104"})
        self.assertFalse(user_finder("mnn2104",student_collection))

    def test_cduplicate_faculty(self):
        faculty_signup("Moses","Nakamura","mnn2104")
        with self.assertRaises(ValueError):
            faculty_signup("Moses","Nakamura","mnn2104")

    def test_dduplicate_student(self):
        student_signup("Moses","Nakamura","mnn2104")
        with self.assertRaises(ValueError):
            student_signup("Moses","Nakamura","mnn2104")

    def test_enew_appointment(self):
        self.assertTrue(create_appointment(1, 1, 1, 1, 1200, 62))

    def test_fappointment_failure(self):
        with self.assertRaises(ValueError):
            create_appointment(1, 1, 1, 1, 1300, 62)

    def test_gappointment_selection(self):
        self.assertTrue(select_appointment(1, 1, 1, "mnn2104", 1200))

    def test_happointment_reselection(self):
        with self.assertRaises(ValueError):
            select_appointment(1, 1, 1, "mnn2104", 1200)

    def test_itrivial_appointment(self):
        with self.assertRaises(ValueError):
            select_appointment(2, 1, 1, "mnn2104", 1200)

if __name__ == '__main__':
    unittest.main()
