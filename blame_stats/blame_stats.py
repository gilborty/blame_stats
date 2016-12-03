# -*- coding: utf-8 -*-
"""A simple application that generates statistics for the result of systemd-analyze blame

Example:
        $ python blame_stats --file bootimage.txt --output bootimage_stats.png

Attributes:

Todo:

"""
# from __future__ import print_function

# import argparse
# import re



# lines = []

# # Dump the file into a list
# with open(args.file) as data:
#         lines = data.readlines()


# # Get the header
# if args.tabs:
#         # Strip the tabs
#         headers = lines[0].replace("\t", ',')
#         headers = headers.strip().split(',')
# else:
#         headers = lines[0].strip().split(args.delimiter)

# # Open the markdown file
# with open(args.output, 'a') as output_file:
        
#         # Generate the headers for Markdown
#         header_break = []
#         for header in headers:
#                 output_file.write("| %s " % str(header))
#                 header_break.append("|----")
#         # Close the header
#         output_file.write("|\n")

#         #Write the break from header to data
#         for col in header_break:
#                 output_file.write(col)
#         # Close it
#         output_file.write("|\n")


#         # Now, get the data ready
#         lines.pop(0)
#         for line in lines:
#                 #Check for tabs
#                 if args.tabs:
#                         dataline = line.replace("\t", ',')
#                         dataline = dataline.strip().split(',')
#                 else:
#                         dataline = line.strip().split(args.delimiter)

#                 # Format the data
#                 data_string = ""
#                 for data in dataline:
#                         data_string += "| {0} ".format(data)
                
#                 # Close the data entry
#                 data_string += "|\n"
                
#                 # And write
#                 output_file.write(data_string)
                
# output_file.close()

import argparse


class BlameParser(object):
    """Parses the result of systemd-analyze blame, cleans it, and formats it into a dict data structure

    Attributes:
        input_file (str): Path to the file containing the results of systemd-analyze blame
    """

    def __init__(self, input_file):
        """
        Note:

        Args:
            input_file (str): Path to the file containing the results of systemd-analyze blame

        """
        self.input_file = input_file
        self.data = dict()

        self._parse(self.input_file)

    @property
    def get_data(self):
        """dict: The cleaned data"""
        return self.data

    def _parse(self, input):
        """Parses the input file and puts into a dict

        Note:

        Args:
            input (str): The path to the file.

        Returns:
            True if successful, False otherwise.
        """
        # Try to open the file
        cleaned_lines = []
        with open(input) as data_file:
            for line in data_file:
                # Split by tabs, strip new line
                line = line.strip().split('\t')
                # Remove units for time
                if "ms" in line[0]:
                        line[0] = line[0].replace("ms", "", 1)
                        # Convert to seconds 
                        line[0] = float(line[0])/1000.0
                else:
                        line[0] = line[0].replace("s", "", 1)

                cleaned_lines.append(line)
        data_file.close()

        self.data = {key: value for (value, key) in cleaned_lines}
        return True



# Parse the arguments
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", help="Path to the file containing the data", required=True)

args = parser.parse_args()


p = BlameParser(args.file)
print(p.get_data)










