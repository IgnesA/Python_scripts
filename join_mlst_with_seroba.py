#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import os
import argparse
import csv


def listTSVFile(file: str):
    with open(file, 'r') as table1:
        lines_table_1 = list(csv.reader(table1, delimiter='\t'))
    return lines_table_1

def getIdFromMlst(s: str):
    return s.split('.')[0]

def exportListToTSVFile(filename: str, list: list, first_row: list):

    with open(filename, 'w') as csvfile:
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile, delimiter='\t') 

        # writing the data rows 
        csvwriter.writerow(first_row) #put the collumn names
        csvwriter.writerows(list)

def main(predictions: str, mlst:str):

    predictions_table = listTSVFile(predictions)
    mlst_table = listTSVFile(mlst)

    mlst_table_first_row = mlst_table[0]
    del mlst_table[0]
    mlst_table_first_row += ["Serotipo", "SRA's"] #10, 11

    for row in mlst_table:
        id_mlst = getIdFromMlst(row[0]).replace(" ", "")
        for line in predictions_table:
            id_predictions = getIdFromMlst(line[2]).replace(" ", "")
            if id_predictions == id_mlst:
                if len(row) > 10:
                    row[10] += f" | {line[1]}"
                    row[11] += f" | {line[0]}"
                else:
                    row.append(line[1])
                    row.append(line[0])

    exportListToTSVFile("Joined_mlst_with_ena.tsv", mlst_table, mlst_table_first_row)

def parse_arguments():

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-p', '--predictions', type=str,
                        required=True, dest='predictions',
                        help='directory where the script has to search for the results directories and fetcher files')

    parser.add_argument('-m', '--mlst', type=str,
                    required=True, dest='mlst',
                    help='Path to the directory where generated '
                            'files will be stored')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_arguments()

    main(**vars(args))