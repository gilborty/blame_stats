# -*- coding: utf-8 -*-
"""A simple application that generates statistics for the result of systemd-analyze blame

Example:
        $ python blame_stats --file bootimage.txt --output bootimage_stats.png

Attributes:

Todo:

"""
import argparse
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import yaml


class BlameParser(object):
    """Parses the result of systemd-analyze blame, cleans it, and formats it into a list of tuples

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
        self.data = {}

        self._parse(self.input_file)

    @property
    def get_data(self):
        """list: The cleaned data"""
        return self.data

    def _parse(self, input_file):
        """Parses the input file and puts into a dict

        Note:

        Args:
            input (str): The path to the file.

        Returns:
            True if successful, False otherwise.
        """
        # Try to open the file
        time = []
        services = []
        with open(input_file) as data_file:
            for line in data_file:
                # Split by tabs, strip new line
                line = line.strip().split('\t')
                # Remove units for time
                if "ms" in line[0]:
                    line[0] = line[0].replace("ms", "", 1)
                    # Convert to seconds
                    line[0] = float(line[0]) / 1000.0
                else:
                    line[0] = line[0].replace("s", "", 1)

                time.append(line[0])
                services.append(line[1])
        data_file.close()

        self.data = zip(services, time)
        return True


class MarkdownTableGenerator(object):
    """Creates a markdown table from a list of tuples

    Attributes:
        input_data (list): The data to format into a table
        output_path (str): Where to put the table
        header (list, optional): The headers for this table (defaults to [Time (seconds), Service])
    """

    def __init__(self, input_data, output_path,
                 header=["Services", "Time (seconds)"]):
        self.input_data = input_data
        self.output_path = output_path
        self.headers = header

        self._generate()

    def _generate(self):
        """Creates a markdown table

        Note:

        Args:

        Returns:
        """
        # Write the headers
        self._write_headers()

        # And the data
        self._write_data()

    def _write_data(self):
        """Helper function to write data to markdown file

        """
        # Open the file to write to
        with open(self.output_path, 'a') as output:
            for dataline in self.input_data:
                # Format the data
                data_string = ""
                for data in dataline:
                    data_string += "| {0} ".format(data)

                # Close the data entry
                data_string += "|\n"
                output.write(data_string)
        output.close()

    def _write_headers(self):
        """Helper function to write the markdown headers

        """
        # Check to see if this file exists, if not touch it
        if not os.path.isfile(self.output_path):
            open(self.output_path, 'a').close()

        # Open the file to write to
        with open(self.output_path, 'r+') as output:

            # Generate the headers for Markdown
            header_break = []
            for header in self.headers:
                output.write("| %s " % str(header))
                header_break.append("|----")
            # Close the header
            output.write("|\n")

            # Write the break from header to data
            for col in header_break:
                output.write(col)
            # Close it
            output.write("|\n")
        output.close()


def get_max_time(data_in):

    return float(data_in[0][1])


def conditional_autopct(pct):
    return ('%.2f' % pct) if pct > 10 else ''


def generate_color_map(data_in):

    for index in range(len(data_in)):
        pass
    return list(reversed(([(x / 50.0, x / 50.0, 0.75)
                           for x in range(len(data_in))])))


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        "-c",
        help="Path to config file for this script",
        required=True)

    parser.add_argument(
        "--file",
        "-f",
        help="Path to the file containing the data",)

    parser.add_argument(
        "--output",
        "-d",
        help="Path to the output directory to put the results and graphs")
    args = parser.parse_args()

    # Parse the YAML config file
    with open(args.config, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # If there are command line arguments, override the YAML config
    if args.file:
        input_file = args.file
    else:
        input_file = config["input-file"]
    if args.output:
        output_dir = args.output
    else:
        output_dir = config["output-directory"]

    # Setup the output directory
    if not os.path.exists(output_dir):
            # Create the directory
        os.makedirs(output_dir)

    # Parse the input file
    blame_parser = BlameParser(input_file)

    # Create the markdown table
    markdown_output = os.path.join(
        output_dir, config["markdown-table-name"] + ".md")
    markdown_table_gen = MarkdownTableGenerator(
        blame_parser.get_data, markdown_output)

    # Create the graphs
    # Bar graph
    plt.figure(1, figsize=(24, 16), dpi=80)

    # The bar lengths
    bar_values = []
    bar_labels = []
    for value in blame_parser.get_data:
            # Strip .service
        bar_labels.append(value[0].replace(".service", "", 1))
        bar_values.append(value[1])

    bar_labels = list(reversed(bar_labels))
    bar_values = list(reversed(bar_values))

    pos = np.arange(len(bar_labels)) + 0.5

    plt.barh(pos, bar_values, align='center', color=config[
             "bar-graph-options"]["bar-color"])
    plt.yticks(pos, bar_labels)

    plt.title(
        config["bar-graph-options"]["title"] +
        " Image: " +
        config["image"])
    plt.xlabel(config["bar-graph-options"]["xlabel"])
    plt.ylabel(config["bar-graph-options"]["ylabel"])
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            output_dir,
            config["bar-graph-options"]["file-name"] +
            ".png"))

    # Pie Chart
    plt.figure(2, figsize=(24, 16), dpi=80)

    # Matplotlib magic
    labels = bar_labels
    fracs = map(float, bar_values)

    for index in range(0, len(labels)):
        percent = fracs[index] / sum(fracs)
        if percent < 0.1:
            labels[index] = ""

    # Color map
    plt.pie(fracs, labels=labels, startangle=90, autopct=conditional_autopct)
    plt.title(
        config["pie-chart-options"]["title"] +
        " Image: " +
        config["image"])

    plt.savefig(
        os.path.join(
            output_dir,
            config["pie-chart-options"]["file-name"] +
            ".png"))

    plt.show()

if __name__ == "__main__":
    main()
