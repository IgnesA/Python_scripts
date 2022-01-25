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

def getDirectoriesAndFetcherFiles(dir: str):
    directories = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    return directories, files

def getSampleName(path: str):
    return path.split('/')[-1]

def getNumberInterval(name: str):
    return name.split('_')[-2:]

def listTSVFile(file: str):
    with open(file, 'r') as table1:
        lines_table_1 = list(csv.reader(table1, delimiter='\t'))
    return lines_table_1

def dictFromTable(table: list, keyCollumn: int):
    d = {}
    for line in table:
        sra_list = line[keyCollumn].split(',')
        if len(sra_list) > 1:
            for sra in sra_list:
                d[sra] = line
        else:
            d[sra_list[0]] = line

    return d

def getPrediction(filePath:str):
    #check if pred file exists
    if os.path.exists(filePath):
        return listTSVFile(filePath)[0][1]
    else:
        return ""

def getSequencingPlatform(row: list, sample: str):
    sra_list = row[4].split(',')
    platform_list = row[5].split(',')

    for i in range(len(sra_list)):
        if sra_list[i] == sample:
            return platform_list[i]

def getFetcherTable(files: list, substring: str):
    return [f for f in files if substring in f][0]

def exportListToTSVFile(filename: str, list: list, results_dir: str, outdir: str, first_row: list):
    csv_file = f"{filename}_{results_dir.replace('/', '')}.tsv"

    with open(os.path.join(outdir, csv_file), 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile, delimiter='\t') 

        # writing the data rows 
        csvwriter.writerow(first_row) #put the collumn names
        csvwriter.writerows(list)

def main(main_directory: str, output_directory: str):
    no_predictions = []
    final_dict = {}
    first_line_final_table = ["SRA", "Prediction", "Input_ID", "Sequencing_Platform", "SRA_matches"]
    first_line_no_prediction = ["SRA", "Input_ID"]

    checkAndMakeDirectory(output_directory)

    #get all results directories
    results_directories, fetcher_tables = getDirectoriesAndFetcherFiles(main_directory)
     
    for results_directory in results_directories:

        results_directory_path = os.path.join(main_directory, results_directory)

        interval_string = '_'.join(getNumberInterval(results_directory))
        fetcher_table = os.path.join(main_directory, getFetcherTable(fetcher_tables, interval_string))#.replace("\\","/")

        # make dictionary with SRA and Ids correspondences
        fetcher_table_dict = dictFromTable(listTSVFile(fetcher_table), 4)

        # get all sample directories present inside results directory
        directories = [d for d in os.listdir(results_directory_path) if os.path.isdir(os.path.join(results_directory_path, d))]

        for directory in directories:
            sample = getSampleName(directory) 
            prediction = getPrediction(os.path.join(results_directory_path, directory, "seroba/pred.tsv"))
            if prediction == "":
                no_predictions.append([sample, fetcher_table_dict[sample][0]])

            final_dict[sample] = [sample, prediction, fetcher_table_dict[sample][0], getSequencingPlatform(fetcher_table_dict[sample], sample), fetcher_table_dict[sample][4]]

    exportListToTSVFile("No_Predictions", no_predictions, main_directory, output_directory, first_line_no_prediction)
    exportListToTSVFile("Predictions_Table_Info", list(final_dict.values()), main_directory, output_directory, first_line_final_table)

def parse_arguments():

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-md', '--main_directory', type=str,
                        required=True, dest='main_directory',
                        help='directory where the script has to search for the results directories and fetcher files')

    parser.add_argument('-o', '--output_directory', type=str,
                    required=True, dest='output_directory',
                    help='Path to the directory where generated '
                            'files will be stored')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_arguments()

    main(**vars(args))