#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import os
import argparse
import csv
import zipfile

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

def isBadPrediction(filters: list, pred: str):
    for f in filters:
        if f in pred:
            return True
    return False

def badSerotypePrediction(line: list, filters: list):
    serotype_results = line[8].split('|')
    for result in serotype_results:
        if not isBadPrediction(filters, result) and result not in ['', ' ', '  ']:
            return False

    if line[4] == 'Complete':
        return False
    return True

def hasNoST(line: list):
    return line[9] in ['-', '', ' ']

def tooManyContigs(line: list):
    if line[1] in ['', ' '] or int(line[1]) > 150:
        return True
    else:
        return False

def intervalTotalAssemblyLen(line: list):
    if line[4] in ['', ' ']:
        return True
    if float(line[4]) >= 1600000.0 or float(line[4]) <= 2400000.0:
        return False
    else:
        return True

def putObservationForExclusion(line: list, observation: str):
    if line[10] != 'X':
        line[10] = 'X'
    if len(line[11]) > 0: 
        line[11] += ' | '
    line[11] += observation

#################################################

def main(predictions_file: str):
    target_dir = 'Filtered_fastas'
    lines_file = listTSVFile(predictions_file)
    filters =["wciP gene might not be complete", "coverage too low", "18B/18C/18F, contamination", "untypable"]
    filtered_ids_for_processing = []
    first_row = lines_file[0]
    del lines_file[0]

    for line in lines_file:
        if len(line) < 12:
            line += ['', '']
        if badSerotypePrediction(line, filters): 
            putObservationForExclusion(line, "Bad serotype prediction")
        if hasNoST(line):
            putObservationForExclusion(line, "Does not have ST")
        if tooManyContigs(line):
            putObservationForExclusion(line, "More than 150 contigs")
        if intervalTotalAssemblyLen(line):
            putObservationForExclusion(line, "Outside total assembly length")
        if line[10] != 'X':
            filtered_ids_for_processing.append(line[0].split('.')[0])
        

    exportListToTSVFile(f'Updated_{predictions_file}', lines_file, first_row)

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
    max = 10000
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