#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import os
import argparse
import csv

def checkAndMakeDirectory(outdir: str):
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

def listTSVFile(file: str):
    with open(file, 'r') as table1:
        lines_table_1 = list(csv.reader(table1, delimiter='\t'))
    return lines_table_1

def getFetcherTable(files: list, substring: str):
    return [f for f in files if substring in f][0]

def getTxtAndFetcherFiles(dir: str):
    txtFiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(".txt")]
    fetcherFiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(".tsv")]
    return txtFiles, fetcherFiles

def getNumberInterval(name: str):
    l = name.split('_')
    print([e for e in l if e.isdigit()])
    return [e for e in l if e.isdigit()]

def dictFromTable(table: list, keyCollumn: int):
    d = {}
    for line in table:
        d[line[keyCollumn]] = line[keyCollumn]

    return d

def exportListToTSVFile(filename: str, list: list, subname: str, outdir: str, first_row: list):
    csv_file = f"{filename}_{subname.replace('/', '')}.tsv"

    with open(os.path.join(outdir, csv_file), 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile, delimiter='\t') 

        # writing the data rows 
        csvwriter.writerow(first_row) #put the collumn names
        csvwriter.writerows(list)

def main(main_directory: str, output_directory: str = ""):

    if output_directory:
        checkAndMakeDirectory(output_directory)

    txtFiles, fetcherFiles = getTxtAndFetcherFiles(main_directory)

    for txtFile in txtFiles:
        not_in_fetcher = []

        txtFile_path = os.path.join(main_directory, txtFile)

        interval_string = '_'.join(getNumberInterval(txtFile))

        fetcher_table = os.path.join(main_directory, getFetcherTable(fetcherFiles, interval_string))

        # make dictionary with SRA and Ids correspondences
        fetcher_table_dict = dictFromTable(listTSVFile(fetcher_table), 0)

        txtFile_table = listTSVFile(txtFile_path)

        for idList in txtFile_table:
            id = idList[0] 

            if id not in fetcher_table_dict.keys():
                not_in_fetcher.append([id])

        exportListToTSVFile("Not_in_fetcher", not_in_fetcher, interval_string, output_directory, ["Input_Ids"])
        
def parse_arguments():

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-md', '--main_directory', type=str,
                        required=True, dest='main_directory',
                        help='directory where the script has to search for the results directories and fetcher files')

    parser.add_argument('-o', '--output_directory', type=str,
                    required=False, dest='output_directory',
                    help='Path to the directory where generated '
                            'files will be stored')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_arguments()

    main(**vars(args))