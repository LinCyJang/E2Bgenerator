import unittest
from datetime import date
import specfile

class TestSpecifications(unittest.TestCase):
	def testPatient(self):
		random_date = date(2014, 1, 1)
		patient = specfile.RandomPatient(random_date)

		self.assertTrue( len(patient.initials) == 3 )
		self.assertTrue( patient.birth_date < random_date )
		self.assertTrue( patient.birth_date > specfile.AGE_FLOOR )
		self.assertTrue( patient.sex in [1, 2] )

	def testRandomDate(self):
		start_date = date(2012, 1, 1)
		end_date = date(2014, 1, 1)
		random_date = specfile.random_date(start_date, end_date)

		self.assertTrue( random_date > start_date and random_date < end_date)

	def testReporter(self):
		countries = ['US', 'GB']
		reporter = specfile.RandomReporter(countries)

		self.assertTrue( type(reporter.organization) == str )
		self.assertTrue( reporter.country in countries )

	def testSpecification(self):
		spec = specfile.Specification(customer="customer1")

		self.assertTrue( spec.base_case_name == "CASE-" )
		self.assertTrue( spec.customer )
		self.assertTrue( type( spec.generate_replacement_set() ) == list )

if __name__ == "__main__":
    unittest.main()   
