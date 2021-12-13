#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import sys
import csv
import os
import subprocess

sample = sys.argv[1]

def read_table(file_path, delimiter='\t'):
    """ Reads a tabular file.

        Parameters
        ----------
        file_path : str
            Path to the tabular file.
        delimiter : str
            Field delimiter.

        Returns
        -------
        lines : list
            List that contains one sublist per
            line in the input tabular file.
    """

    with open(file_path, 'r') as infile:
        lines = list(csv.reader(infile, delimiter=delimiter))

    return lines

def download_from_ena(sample, output_directory):

    enaTools_command = ["/mnt/beegfs/scratch/ONEIDA/ines.almeida/enaBrowserTools-0.0.3/python3/enaDataGet", "-f", "fastq", "-d", output_directory, sample]
    res = subprocess.run(enaTools_command)
    if (res.returncode != 0):
        print("The exit code was: %d" % res.returncode)
        print(f"Something went wrong downloading {sample} with enaBrowserTools...")
        return sample
    
    return ""


def main():

    not_downloaded = []

    output_directory = "downloads"
    files = []
    file1 = ""
    file2 = ""

    res = download_from_ena(sample, output_directory)

    dir_exists = os.path.exists(output_directory + f"/{sample}")

    if dir_exists:
        files = os.listdir(output_directory + f"/{sample}")

        file1 = [file for file in files if "_1" in file]
        file2 = [file for file in files if "_2" in file]

    if res == sample or not (file1 and file2):
        not_downloaded.append(sample + '\n')

    if len(not_downloaded) != 0:
        with open("not_downloaded.txt", "a") as file:
            file.writelines(not_downloaded)



if __name__ == "__main__":

    main()
