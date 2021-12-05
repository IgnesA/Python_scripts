#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Inês Almeida
"""

import os
import sys
import urllib 
import time
import hashlib
import requests, json
import subprocess

base_path = 'https://'
final_path = ''
sample = sys.argv[1]

outdir = f'{sample}/'

outfile1 = outdir + f'{sample}_1.fastq.gz'
outfile2 = outdir + f'{sample}_2.fastq.gz'

def HandleProgress(block_num, block_size, total_size):
        read_data= 0
        # calculating the progress
        # storing a temporary value  to store downloaded bytesso that we can add it later to the overall downloaded data
        temp = block_num * block_size
        read_data = temp + read_data
        #calculating the remaining size
        remaining_size = total_size - read_data
        if(remaining_size<=0):
            downloaded_percentage = 100
            remaining_size = 0
        else:
            downloaded_percentage = int(((total_size-remaining_size) / total_size)*(100))

        if downloaded_percentage == 100:
            print( f'Downloaded: {downloaded_percentage}%  ' , end="\n")
        else:
            print(" ", end="\r")   
            print( f'Downloaded: {downloaded_percentage}%  ' , end="\r")

def checkDownload(download:str, original_hash:str):
    """
        Function to check the integrity of a downloaded file.
    """

    with open(download, 'rb') as infile:
        data = infile.read()
        md5 = hashlib.md5(data).hexdigest()


    if md5 != original_hash:
        print('Hashes do not match')
        return False
    
    return True

def download_ftp(file_url, out_file, original_hash):
    downloaded = False
    while downloaded is False:
        try:
            res = urllib.request.urlretrieve(file_url, out_file, HandleProgress)
        except:
            time.sleep(1)
        if os.path.isfile(out_file) is True:
            if original_hash != '':
                if checkDownload(out_file, original_hash):
                    downloaded = True
            else:
                downloaded = True

    return downloaded

def download_from_ena():
    json_fields = json.loads(requests.get(f'https://www.ebi.ac.uk/ena/portal/api/filereport?accession={sample}&format=JSON&result=read_run&fields=fastq_ftp,fastq_md5').text)[0]
    download_links = json_fields['fastq_ftp'].split(';')
    md5_hashes = json_fields['fastq_md5'].split(';')

    print(download_links)
    print(md5_hashes)

    print('Downloading 1')
    while not download_ftp(f'{base_path}{download_links[0]}', outfile1, md5_hashes[0]):
        continue

    print('Downloading 2')
    while not download_ftp(f'{base_path}{download_links[1]}', outfile2, md5_hashes[1]):
        continue

    # print("Uncompressing files..")
    # res = subprocess.run(["gzip", "-d", outfile1])
    # if (res.returncode != 0):
    #     print("The exit code was: %d" % res.returncode)
    #     print("Something went wrong...")

    # res = subprocess.run(["gzip", "-d", outfile2])
    # if (res.returncode != 0):
    #     print("The exit code was: %d" % res.returncode)
    #     print("Something went wrong...")


def download_from_sra():

    fastq_command = ["fastq-dump", sample, "--split-files", "-v"]
    res = subprocess.run(fastq_command)
    if (res.returncode != 0):
        print("The exit code was: %d" % res.returncode)
        print("Something went wrong...")

    print(f"Moving file 1")
    mv_command = ["mv", f'{sample}_1.fastq', outfile1[:-3]]
    print()
    res = subprocess.run(mv_command)
    if (res.returncode != 0):
        print("The exit code was: %d" % res.returncode)
        print("Something went wrong...")

    print(f"Moving file 2")
    mv_command = ["mv", f'{sample}_2.fastq', outfile2[:-3]]
    res = subprocess.run(mv_command)
    if (res.returncode != 0):
        print("The exit code was: %d" % res.returncode)
        print("Something went wrong...")



def main():

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    check_link = f'https://www.ebi.ac.uk/ena/portal/api/search?dataPortal=ena&format=JSON&includeAccessions={sample}&result=read_run&sortDirection=asc'

    r = requests.get(check_link)
    if (r.status_code == 200):
        download_from_ena()
    elif(r.status_code == 204):
        download_from_sra()
    else:
        print(f'A different status code returned for sample: {sample}')
    
main()

