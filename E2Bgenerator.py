# import xml.etree.ElementTree as ET
from lxml import etree as ET

import sys, time, os, inspect, glob, random
from datetime import date, timedelta

# Import spec file
import specfile
from datetime import date

TEMPLATES = []
VERBOSE = True

## UTILITIES ##
def getRoot(template_name=None):
    # Reading XML template
    if not TEMPLATES:
        readTemplates()

    try:
        if not template_name:
            template_name = random.choice(TEMPLATES)

        tree = ET.parse(template_name)
        return template_name[10:-4], tree.getroot()

    except IOError:
        raise IOError("A template wasn't found.  E2Bgenerator cannot continue without a template file to work with.")

def get_val_func_str(value):
    '''
    Checks a value to see if it's a function, genereeator or a string.  If function or generator, it calculates
    the value and returns.  If string, it just returns.

    Parameters:
      value - Can be either a string, generator or a function (without parameters)
    '''
    if str( type(value) ).find("functools.partial") != -1:
        return get_val_func_str( value() )

    elif inspect.isgenerator(value):
        return value.next()

    elif inspect.isfunction(value) or inspect.ismethod(value):
        return value()

    else:
        return str(value)

def readTemplates():
    # Getting template names
    for filename in glob.glob("templates/*.xml"):
        TEMPLATES.append(filename)

def set_xml_value(root, tags_values):
    '''
    Sets XML values

    Parameters:
       root - XML element to be iterated on. If you want to use XPATH format, start the
              string with a # character.

       tags_values - List of tuples that contains a tag and a value. The value
                     can be either a function, generator, or string.  If you're passing
                     a function with parameters, use functools.partial

                     Ex. = [("randomID", random_id_function), ("name", string)]

                     The first element in the list is what is iterated over through
                     root.  Any subsequent items are found directly after the base element. 

                     Note that any subsequent element names can be found using XPATH syntax
                     as opposed to just a tag name
    '''

    # Iterate through the XML tree to find the right tag
    # print "**" + str(tags_values)
    if type(tags_values) != list or tags_values == []:
        raise Exception("Parameter tags_values must have at least one tag-value pair.")

    base_tag, base_value = tags_values.pop(0)

    for e in root.iter( base_tag ):
        e.text = get_val_func_str(base_value)

        e_parent = e.getparent()

        for tag, new_value in tags_values:
            search_results = e_parent.findall(tag)

            # If no end tag found, generate the value anyway so the
            # generator order doesn't get thrown off 
            if not search_results:
                _ = get_val_func_str(new_value)

            else:
                for e2 in search_results:
                    e2.text = get_val_func_str(new_value)

#### ---- E2B Generator Initialization ---- ####

def main():

    print "** E2B Generator"
    print "** Direct any questions to: Ryan Hefner"

    # Creating a new directory for generated cases and templates
    if not os.path.exists("GeneratedCases"):
        os.mkdir("GeneratedCases")

    if not os.path.exists("templates"):
        os.mkdir("templates")

    readTemplates()

    if not TEMPLATES:
        raise Exception("E2Bgenerator must have at least one template to work with.")

    # Getting specification to generate the files
    customer = raw_input("\n\n## What customer profile should be used?   ")

    # Asking for number of copies of the E2B are desired
    copies = int( raw_input("\n## How many cases would you like to generate?   ") )

    for i in range(1, copies+1):
        # Getting root
        template_name, root = getRoot()

        # Generating new spec file
        spec = specfile.Specification(customer=customer)

        # Generating the new name
        new_name = spec.base_case_name + template_name + "-" + str(date.today().year) + "-" + str(i).zfill(6)

        # Printing progress
        print "\nGenerating " + new_name + "..."  

        # Generating a new replacement set
        replacement_set = spec.generate_replacement_set()

        # Adding the new name to the replacement_set
        replacement_set += [ [( "safetyreportid", new_name )],
                             [( "messagenumb", new_name )],
                             [( "companynumb", new_name )]]

        # Looking at the replacements definition in the spec file
        # to replace specific items in the E2B
        for tags_values in replacement_set:

            # Setting the new XML value
            set_xml_value(root, tags_values)

        # Writing file to disk
        xml_contents = ET.tostring(root)
        os.chdir("GeneratedCases")
        
        with open(new_name + ".xml", "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-16"?>')
            f.write('\n<!DOCTYPE ichicsr SYSTEM "http://www.accessdata.fda.gov/xml/icsr-xml-v2.1.dtd">')
            f.write("\n" + xml_contents)
            f.close()
                
        # Moving back to the parent directory
        os.chdir("../")
        print "Done."

    # Process finished
    print "\n\n** E2B generation complete.  All files are in the GeneratedCases folder."
    time.sleep(10)
    sys.exit()

if __name__ == "__main__":
    main()