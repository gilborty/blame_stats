# -*- coding: utf-8 -*-
"""A simple application that generates statistics for the result of systemd-analyze blame

Example:
        $ python blame_stats --file bootimage.txt --output bootimage_stats.png

Attributes:

Todo:

"""
from __future__ import print_function

import argparse
import re

# Parse the arguments
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", help="Path to the file containing the data", required=True)
parser.add_argument("--output", "-o", help="Where to put the markdown table.")
parser.add_argument("--delimiter", "-d", help="How is the data separated?", default=" ")
parser.add_argument("--tabs", "-t", help="If the data is separated by tabs, let us know",action='store_true')

args = parser.parse_args()

lines = []

# Dump the file into a list
with open(args.file) as data:
        lines = data.readlines()


# Get the header
if args.tabs:
        # Strip the tabs
        headers = lines[0].replace("\t", ',')
        headers = headers.strip().split(',')
else:
        headers = lines[0].strip().split(args.delimiter)

# Open the markdown file
with open(args.output, 'a') as output_file:
        
        # Generate the headers for Markdown
        header_break = []
        for header in headers:
                output_file.write("| %s " % str(header))
                header_break.append("|----")
        # Close the header
        output_file.write("|\n")

        #Write the break from header to data
        for col in header_break:
                output_file.write(col)
        # Close it
        output_file.write("|\n")


        # Now, get the data ready
        lines.pop(0)
        for line in lines:
                #Check for tabs
                if args.tabs:
                        dataline = line.replace("\t", ',')
                        dataline = dataline.strip().split(',')
                else:
                        dataline = line.strip().split(args.delimiter)

                # Format the data
                data_string = ""
                for data in dataline:
                        data_string += "| {0} ".format(data)
                
                # Close the data entry
                data_string += "|\n"
                
                # And write
                output_file.write(data_string)
                
output_file.close()



