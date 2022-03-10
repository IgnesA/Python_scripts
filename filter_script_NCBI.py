#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import os
import argparse
import csv
import zipfile
import copy

def checkAndMakeDirectory(outdir: str):
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

def listTSVFile(file: str):
    with open(file, 'r') as table:
        lines_table = list(csv.reader(table, delimiter='\t'))
    return lines_table

def exportListToTSVFile(filename: str, list: list, first_row: list):

    with open(filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile, delimiter='\t') 

        # writing the data rows 
        csvwriter.writerow(first_row) #put the collumn names
        csvwriter.writerows(list)

def singleResultSerobaFilter(result: str, filters: list):
    for filter in filters:
            if filter in result or result == "" or result == " ":
                return True
    return False

def helperSerobaFilter(seroba: str, filters: list):
    results = seroba.split("|")
    if len(results) == 1:
        return singleResultSerobaFilter(results[0], filters)
    for result in results:
        if not singleResultSerobaFilter(result, filters):
            return False
    return True

def isToFilterSeroba(line: list, filters: list):
    if len(line) < 12:
        return True
    if helperSerobaFilter(line[10], filters) or line[10] == "":
        return True
    return False

def isToFilterMLST(line:list):
    if line[1] != "spneumoniae" or (line[2] == "" or line[2] == "-"):
        return True
    else :
        return False
    
def filterAll(line:list, filters: list):
    return isToFilterMLST(line) or isToFilterSeroba(line, filters)

def main(predictions_file: str):
    target_dir = 'Filtered_fastas'
    lines_file = listTSVFile(predictions_file)
    filters =["wciP gene might not be complete", "coverage too low", "untypable"]
    filtered_ids_for_processing = []
    rejected_lines = []
    filtered_lines = []
    first_line_filtered = lines_file[0]
    del lines_file[0]

    for line in lines_file:
        if not filterAll(line, filters):
            filtered_ids_for_processing.append(line[0].replace(" ", "").split(".")[0])
            filtered_lines.append(line)
        else:
            rejected_lines.append(line)

    # exporting 
    exportListToTSVFile(f"Filtered_{predictions_file}", filtered_lines, first_line_filtered)
    exportListToTSVFile(f"Rejected_{predictions_file}", rejected_lines, first_line_filtered)

    # select fasta files 
    checkAndMakeDirectory(target_dir)

    zip_files = [f for f in os.listdir() if ".zip" in f]

    for zip in zip_files:
        with zipfile.ZipFile(zip) as zf:
            files_in_zip = zf.namelist()
            #print("files in zip: ", files_in_zip)
            filtered_fastas = [f for f in files_in_zip if f.split('.')[0] in filtered_ids_for_processing]

            for fasta in filtered_fastas:
                zf.extract(fasta, path=target_dir)
    
    #grouping fasta files
    all_filtered_fastas = os.listdir(target_dir)
    all_filtered_fastas_paths = [os.path.join(target_dir, f) for f in all_filtered_fastas]

    count = 0
    max = 5000
    count_files = 0
    end = max
    number_of_files = len(all_filtered_fastas_paths)

    while count_files < number_of_files:
        count = 0

        if (count_files + max > number_of_files):
            end = number_of_files - count_files

        dirname = os.path.join(target_dir, f'{count_files+1}_{count_files + end}') 

        checkAndMakeDirectory(dirname)

        print(f'Processing directory: {dirname}...')    

        while count < max and count_files < number_of_files:
            new_file_path = os.path.join(dirname, all_filtered_fastas[count_files])
            os.rename(all_filtered_fastas_paths[count_files], new_file_path)
            count += 1
            count_files += 1

def parse_arguments():

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--file', type=str,
                        required=True, dest='predictions_file',
                        help='file with predictions to be filtered.')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_arguments()

    main(**vars(args))