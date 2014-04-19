from datetime import datetime, timedelta, date
import random, string
from functools import partial

AGE_FLOOR = date(1930, 1, 1)
DATE_FORMAT = "%Y%m%d"
EIGHTEEN_YEARS = timedelta(days=6570)
TWO_DAYS = timedelta(days=2)
THIRTY_YEARS = timedelta(days=10950)

FIRST_NAMES = [
    "Steven",
    "Eloise",
    "Sebastian",
    "Janice",
    "Bill",
    "Jack",
    "Jim",
    "Bonita",
    "Matilda",
    "Anna"
]

LAST_NAMES = [
    "Palmer",
    "Rucker",
    "Moore",
    "Lolley",
    "Gilbert",
    "Patt",
    "Hernandez",
    "Kennedy",
    "Poole",
    "Conner"
]

ORGANIZATIONS = [
    {
        "organization" : "UNC",
        "state" : "NC",
        "postcode" : "2222",
        "country" : "US"
    }
]

def _get_partial_val(val):
    # If a functools.partial instance, return the functional value
    if str( type(val) ).find("functools.partial") != -1:
        return val()

    else:
        return val

# Gives a random date between two given dates
def random_date(start, end, return_date=True):
    # If start, end are functools.partial, compute the values
    start = _get_partial_val(start)
    end = _get_partial_val(end)

    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    
    random_date = start + timedelta(seconds=random_second)

    if return_date:
        return random_date
    else:
        return random_date.strftime(DATE_FORMAT)

def random_date_generator(*args, **kwargs):
    while True:
        yield random_date(*args, **kwargs)

def random_time_delta():
    return timedelta(days=random.randint(14, 3650))

class RandomPatient():
    def __init__(self, case_date):
        self.initials = ""
        for i in range(0,3):
            self.initials += random.choice(string.letters).upper()

        # Make sure that the patient is at least 18 years old - that's why
        # we subtract 18 yrs from case_date
        self.birth_date = random_date(AGE_FLOOR, case_date - EIGHTEEN_YEARS)
        self.sex = random.choice([1, 2])

    @property
    def formatted_birth_date(self):
        return self.birth_date.strftime(DATE_FORMAT)

class RandomReporter():
    def __init__(self, countries):
        self.given_name = random.choice(FIRST_NAMES)
        self.family_name = random.choice(LAST_NAMES)

        # Only choosing organizations which are in the countries set by customer
        available_organizations = [o for o in ORGANIZATIONS if o['country'] in countries]
        random_organization = random.choice(available_organizations)

        self.organization = random_organization['organization']
        self.state = random_organization['state']
        self.postcode = random_organization['postcode']
        self.country = random_organization['country']


class Specification():
    def __init__(self, customer=None):

        self._random_start_end_history = []

        # Setting organization-specific values
        self.customer = customer.lower()

        if self.customer == "customer1":
            self.base_case_name = "CASE-"
            sender_organization = "SENDER01"
            receiver_organization = "RECEIVER01"
            self._countries = ['US', "FR", "DE"]

        elif self.customer == "customer2":
            self.base_case_name = "CASE-"
            sender_organization = "SENDER02"
            receiver_organization = "RECEIVER02"
            self._countries = ['US', "FR", "DE"]

        else:
            raise Exception("Error: Unknown customer.  Please try again with a correct customer name.")

        # Defining the replacement values based on customer settings
        self._base_replacements = [
            [( "primarysourcecountry", random.choice(self._countries) )],
            [( "occurcountry", random.choice(self._countries) )],
            [( "senderorganization", sender_organization )],
            [( "messagesenderidentifier", sender_organization )],
            [( "receiverorganization", receiver_organization )],
            [( "messagereceiveridentifier", receiver_organization )]
        ]

    @property
    def base_replacements(self):
        return self._base_replacements

    def generate_replacement_set(self):
        '''
        Every time this is called, a new replacement list is generated.  This list is
        formatted for entry into E2Bgenerator.set_xml_value().

        Ex. = [("randomID", random_id_function), ("name", string)]
        '''

        transmission_date = random_date( date.today()-THIRTY_YEARS, date.today() )
        receive_date = transmission_date + TWO_DAYS
        self._receive_date = receive_date

        reporter = RandomReporter(self._countries)
        patient = RandomPatient(transmission_date)

        random_se_gen = self.random_start_end_within_lifetime()

        # Generating random values 
        new_values = [
            [( "transmissiondate", transmission_date.strftime(DATE_FORMAT) )],
            [( "receivedate", receive_date.strftime(DATE_FORMAT) )],
            [( "receiptdate", receive_date.strftime(DATE_FORMAT) )],

            [( "reportergivename", reporter.given_name )],
            [( "reporterfamilyname", reporter.family_name )],
            [( "reporterorganization", reporter.organization )],
            [( "reporterstate", reporter.state )],
            [( "reporterpostcode", reporter.postcode )],
            [( "reportercountry", reporter.country )],

            [( "patientinitial", patient.initials )],
            [( "patientbirthdate", patient.birth_date.strftime(DATE_FORMAT) )],
            [( "patientsex", patient.sex )],

            [   ("patientmedicalstartdate", random_se_gen),
                ("patientmedicalenddate", random_se_gen)        ],

            [   ("patientdrugstartdate", random_se_gen),
                ("patientdrugenddate", random_se_gen)        ],

            [   ("drugstartdate", random_se_gen),
                ("drugenddate", random_se_gen)        ],

            [   ("reactionstartdate", random_se_gen),
                ("reactionenddate", random_se_gen),
                ("..//test/testdate", partial(random_date_generator, 
                                            partial(self.random_start_end_history, -2),
                                            partial(self.random_start_end_history, -1),
                                            return_date = False
                                            ))]
        ]

        # Merging above changes with base replacements list
        return new_values + self.base_replacements

    def random_date_within_lifetime(self, return_date=False):
        d = random_date(AGE_FLOOR, self._receive_date)
        
        if return_date:
            return d
        else:
            return d.strftime(DATE_FORMAT)

    def random_start_end_within_lifetime(self):
        i = 0
        date = None
        self._random_start_end_history = []

        while True:
            if i % 2 == 0:
                date = self.random_date_within_lifetime(return_date=True)

            else:
                date += random_time_delta()
            
            # Converting date to readable format
            date_formatted = date.strftime(DATE_FORMAT)

            # Writing date to history array
            self._random_start_end_history.append(date_formatted)

            yield date_formatted

            i += 1

    def random_start_end_history(self, index, return_date=True):
        d = self._random_start_end_history[index]

        if return_date:
            return datetime.strptime(d, DATE_FORMAT)
        else:
            return d
