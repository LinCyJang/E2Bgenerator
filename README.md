E2Bgenerator
============
This program is designed to generate randomized case data in the E2B format (set forth by the US Food and Drug Administration).  Its primary use is to generate test cases to be imported into the Oracle Argus Safety platform so that new users can experiment in a sandbox environment.

It does this by using one or more "perfect" E2B files and replaces certain XML values to make it unique to the system.

### Structure
- `specfile.py` contains the code to generate random data as well as specific organization preferences.
- `E2Bgenerator.py` reads the perfect E2B files, substitutes values from the specification file, and outputs the desired number of test cases.  This also handles user interaction.

Please contact Ryan Hefner if you have any questions.
