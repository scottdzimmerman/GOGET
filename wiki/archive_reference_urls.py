"""
archive_reference_urls.py

Migrated from Colab notebook: archiveReferenceURLs SZ 2_7_23.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# GEM Internet Archive script
# --
# Create a unique list of reference URLS and produce an Internet Archive URL for each one
#
# Sarah Clark & Mason Inman
# 2021-03-03
#
#
# Notes:
# * Detailed steps are in the file "Going from Spreadsheet References to Wiki Markdown Citations"
# * Assumes columns with references have \[ref\] in the column name
# * Runs one tab at a time, based on the value of 'tabNm' variable
# * Master list building is commented out because you need to do manual QA/QC before running it

# Variables
# ---

# ===== Cell 1 =====

import sys
import shutil
import pandas as pd
import waybackpy
from waybackpy.exceptions import WaybackError
import requests
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import os
from csv import writer
import pygsheets
import config
import requests

# also pip install openpyxl

## Getting URLs ##
# Programmatic retrieval from Google Drive
# Name of the google sheet + specific tab
sheetName = 'GOGET oil & gas extraction sites (main data set)'
tabNm ="Ownership"

## Directories ##
#################
outputDir = r'/Users/jennymartos/Documents/GEM/GRFF/wiki_references/GGPT-References-master'

# Output folder path
archivedDirectory = os.path.join(outputDir, 'output')
if not os.path.exists(archivedDirectory):
    os.mkdir(archivedDirectory)
# Master lists folder
masterDir = os.path.join(outputDir, 'masters')
if not os.path.exists(masterDir):
    os.mkdir(masterDir)
# Master lists back-ups folder
masterBackup = os.path.join(outputDir, r'masters\old')
if not os.path.exists(masterBackup):
    os.mkdir(masterBackup)

## Datasets ##
##############
# Master List of reference URLs
master = os.path.join(masterDir, 'archivedURLs_masterList.xlsx')
if not os.path.exists(master):
    pd.DataFrame(columns=['region', 'originalURL', 'archivedURL', 'batchTime', 'notes']).to_excel(master, index=False)

# Citoid master list
citoidMaster = os.path.join(masterDir, 'citoid_masterList.xlsx')
if not os.path.exists(citoidMaster):
    pd.DataFrame(columns=['title', 'origURL']).to_excel(citoidMaster, index=False)

## URLs w Commas ##
###################
urlsWCommas = {r'https://www.terra.com.br/noticias/dino/mhps-anuncia-sua-primeira-vitoria-em-leilao-brasileiro-de-turbina-a-gas-jac':r'https://www.terra.com.br/noticias/dino/mhps-anuncia-sua-primeira-vitoria-em-leilao-brasileiro-de-turbina-a-gas-jac,c444dffce756b8122081cc5668ea2622a735xh32.html',r'http://gasprocessingnews.com/news/agreement-signed-for-the-development-of-600-mw-gas-power-plant':r'http://gasprocessingnews.com/news/agreement-signed-for-the-development-of-600-mw-gas-power-plant,-lng-terminal-in-indonesia.aspx'}
splitUrlsWCommas = [r'https://www.terra.com.br/noticias/dino/mhps-anuncia-sua-primeira-vitoria-em-leilao-brasileiro-de-turbina-a-gas-jac',r'http://gasprocessingnews.com/news/agreement-signed-for-the-development-of-600-mw-gas-power-plant']


# Function Definitions
# ---

# Fetch tab's reference columns data, building a unique set

# ===== Cell 2 =====
#TODO: build a loop of all tabs so can run weekly
#TODO: hack a QC for URLs with commas by checking for any comma not followed by http?
def getURLs(worksheet, tabNm, archivedDirectory):
    # set of URLs
    theRefs=set()

    # Connect to Google sheet
    # ws = pd.read_excel(worksheet, sheet_name=tabNm, na_filter=False)
    gc = pygsheets.authorize(client_secret=config.pathToSecretFile)
    ss = gc.open(sheetName)
    print(ss.title, '\n')
    print("Tab title: ", tabNm, "\n")

    # empty variables
    refColList = None
    column = None

    try:
        # Get the tab to work on
        ws = ss.worksheet('title', tabNm)
        # Get column names
        header = ws.get_row(row=1, include_tailing_empty=False, returnas="matrix")
        # header = ws.columns.tolist()
        print(header)
        ws_pandas = pd.DataFrame(ws, dtype=str)
        ws_pandas =  ws_pandas.iloc[:, : len(header)]
        ws_pandas.columns=header #have to assign after drop extra columns or throws error
        gas_units= ws_pandas.drop([0])
    except Exception as exception:
        print(exception)
        print ("Pygsheets error, breaking.")
        raise
    try:
        # Get column names that include the reference tag
        refColList = [x for x in header if "source" in x]

        # Get index of every ref col
        # Loop through each column to archive each ref cell
        for columnName in refColList:
            splits = None
            print("Column name: ", columnName)
            column = gas_units[columnName].tolist()

            # unique set
            column = set([x for x in column if 'http' in x]) #unique values (a set) that are URLS

            # Split any cells that have multiple references (assume , or ; separated)
            # skip google maps - often has matching punctuation to split
            skipSplit = [x for x in column if 'google.com/maps' not in x and 'google.co.th/maps' not in x]
            splits  =[x for x in skipSplit if ',' in x or ';' in x]
            if len(splits) > 0:
                print("Splitting cells...")
                # TODO: regex because what if both , and ;
                for txt in splits:
                    # Remove the compound reference from the column dataset
                    column.remove(txt)
                    cellSplit = txt.replace(';',',').split(',')
                    # print(cellSplit)
                    cellSplit = [x.strip() for x in cellSplit]
                    # Add the new split URLS back into the column dataset
                    column.update(cellSplit)
                print("Cells split", "\n")

            # remove any split new shorthand
            column = set([x for x in column if 'http' in x])

            # Remove error-prone URLs --> Mason
            # remove GLEIF, Google Maps (and more?)
            # GLEIF: pages don't archive correctly bc of #
            # Google Maps: not sure how they'd archive, and not relevant to archive
            search_strs = [
                'search.gleif.org',
                'google.com/maps',
                'google.co.th/maps'
            ]
            for search_str in search_strs:
                column = [x for x in column if search_str not in x]
            theRefs.update(column)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit()

    # write out this list before moving on to archiving
    print("Writing refs list out to file", "\n")

    # Drop URLs that we know have commas and will seem new but have been done already after manually fixing, put in full url broken at splits
    theRefs = list(theRefs)
    keys = [x for x in theRefs if x in splitUrlsWCommas]
    theRefs = [x for x in theRefs if x not in splitUrlsWCommas]
    theRefs.extend([urlsWCommas[x] for x in keys])

    # DF
    theRefs_df = pd.DataFrame({"originals": theRefs})

    # Add region column
    theRefs_df["region"] = tabNm

    # To file and return list
    theRefs_df.to_excel(os.path.join(archivedDirectory, "originalRefs_"+tabNm+"_"+str(datetime.now().strftime("%Y-%m-%d %H_%M"))+".xlsx"), index=False)
    return theRefs

# Compare against master list to see if it's already done

# ===== Cell 3 =====
# TODO: store master list of archived URLs online so everyone shares it, minimal duplication
def getNewURLs(ml, newList):
    masterList = pd.read_excel(ml, na_filter=False)
    nlPD = pd.DataFrame(data=newList, columns=["new"])

    # Get the new URLs that aren't yet in the master list of URLs
    newURLs = nlPD[~nlPD["new"].isin(masterList["originalURL"].tolist())]["new"].tolist()

    print("The new URLS ", newURLs)
    return newURLs # remove series name "new"

# Handle HTML encoding

# ===== Cell 4 =====
# occasionally the Wayback API returns currupt HTML encoding
# this function replaces any unexpected character references with proper HTML
# otherwise the URL link won't work (returns empty/wrong page)
# because the browser cannot interpret the character reference
def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&num;", "#")
    s = s.replace('&colon;', ':')
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

# Run a unique set of URLS through the Internet Archive to get back a list of archived URLs

# ===== Cell 5 =====
#TODO: writing out to CSV messes up encoding, figure out pandas row writer

def waybackHandler(listOfRefs, country, fileOutput):
    if len(listOfRefs) == 0:
        print("No new URLs to add.")
        return "cancel"
    print('Starting wayback script', "\n")
    # Variables
    # Path to store archived URL list -- note must be after you define 'tabNm'
    # Store as running in case of error, won't lose everything
    archiveFile = os.path.join(fileOutput, "ArchivedRefs_"+country+"_"+str(datetime.now().strftime("%Y-%m-%d %H_%M"))+".csv")

    # empty file to append, written with column names
    archived_df = pd.DataFrame(columns=['region','originalURL','archivedURL','batchTime', 'notes'])
    archived_df.to_csv(archiveFile, index=False)

    # Archive date cutoff (too old)
    cutoff = date.today() + relativedelta(months=-3)

    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"

    # Loop over URLs and archive each one
    for url in listOfRefs:
        # TODO: could make this a dataframe, add a column for the archived date --> archive.timestamp
        # Currently the Citoid parsing pulls date from url
        archived_ser = pd.Series(dtype=str)
        create_archive = None # initialize
        print(url, "\n")

        # Don't archive already archived pages
        if 'web.archive.org' in url:
            # our reference is to internet archive
            print(f"--- skip; our ref is to IA: {url}")
            archived_ser.loc[url] = 'reference is to Internet Archive'

        # "#" in the URL breaks the wayback function
        elif url.find("#") != -1:
            archived_ser.loc[url] = 'FIX ME: pound/hash symbol in URL, page anchor?'
            print("FIX URL, pound/hash symbol in URL, breaks Wayback API - waybackpy.Url(url, user_agent)")
        else:
            try:
                print('Checking for Internet Archives')
                # check for URL in Archive
                # NOTE: if 'waybackpy.Url' returns nothing, wayback = None
                # but this is not NoneType, just "None" and I have been unable
                # to match it at all, it's a wrapper still, not string or any dictionary
                # at least no strange errors, you don't get empty things back
                # hash symbol breaks this, make github comment? and comment about &?
                wayback = waybackpy.Url(url, user_agent) # <class 'waybackpy.wrapper.Url'>

                # If there aren't any archives it returns 0, no errors
                total_archives = wayback.total_archives()
                if total_archives < 1:
                    print("Zero archive versions")
                    create_archive = True
                else:
                    newest = wayback.newest()
                    newest_dt = newest.timestamp.date()
                    if newest_dt > cutoff:
                        print(f"--- use the already archived version: {newest.archive_url}", "\n")
                        # put into series:
                        archived_ser.loc[url] = unescape(newest.archive_url)
                    else:
                        print('No archives before cutoff')
                        # flag to try to create new archive (below)
                        create_archive = True
            except WaybackError as e:
                print("Unexpected error in initial URL get: ", e)
                create_archive = True
            # catch all remaining/unexpected/unhandled errors
            except:
                print("Unknown error in wayback:", sys.exc_info()[0])
                create_archive = True

            # try to create archive
            if create_archive == True:
                print('Making archive copy')
                try:
                    archive = wayback.save()
                    # put into series:
                    archived_ser.loc[url] = unescape(archive.archive_url)
                    print(f"*** Successfully archived URL at: {archive.archive_url}", "\n")

                except WaybackError as e:
                    print("Wayback Error Message: ", e)
                    print(f"XXX Archive failed for {url}", "\n") # for db
                    archived_ser.loc[url] = 'Archiving failed' # may be overwritten below, if more detail posible

                except AttributeError:
                    print(f"Hit Attribute Error for {url}", "\n")
                    archived_ser.loc[url] = "Attribute Error"

                except:
                    print("Unknown error in wayback:", sys.exc_info()[0])
                    archived_ser.loc[url] = "Unknown Error"

        print('saving')
        save_timestamp = datetime.now()

        # Couldn't figure out how to append a row in a pandas sheet for the life of me
        # using CSV writer to save each link as it loops in case it crashes
        outie = list(archived_ser)
        outie.append(save_timestamp)
        outie.insert(0, country)
        outie.insert(1,url)
        with open(archiveFile, 'a', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(outie)

    print('Wayback done, compiling')
    return archiveFile


# Save a list of URLs that haven't gone through citoid yet to process

# ===== Cell 6 =====
def citoidFile(ml, cl):
    print("Checking for URLs that need to go through Citoid...")
    c = pd.read_excel(cl)
    missing = [x for x in ml if x not in c["origURL"].tolist()]

    if len(missing) > 0:
        ctd = pd.DataFrame(data=missing, columns=["originalURL"])
        ctd["region"] = tabNm
        ctd.to_excel(os.path.join(archivedDirectory, "citoid_TODO_"+tabNm+"_"+str(datetime.now().strftime("%Y-%m-%d %H_%M"))+".xlsx"), index=False)
        print("Done, URLs to process: ", len(missing))
    else:
        print("No new URLs to process with Citoid.")

# Ping each new URL for an HTTP status code, then manually check errors (see info doc)

# ===== Cell 7 =====
# In order to generate the best web citations, need to say if a URL is live or dead
# but to define "live" based on http code, want to look at all numeric responses
# because some sites connect then redirect to an error, and that's dead
# so find all the redirect codes that should be called 'dead' - but then manually check any with errors (non-200)
# Because a permanent redirect is a 300 but should be called 200 IMO

def pingURL(mainDir, region, testMe):
    if len(testMe) == 0:
        print("No new URLs to process with Citoid.")
    else:
        # variables
        today = datetime.now().strftime("%Y-%m-%d %H_%M")
        output = pd.DataFrame(columns=['region','url','code','httpCodeManual','notes'])
        outFilename = 'http_'+region.replace(" ","")+"_"+str(today)+'.csv'
        output.to_csv(os.path.join(mainDir,outFilename), index=False)
        for i in testMe:
            print(i)
            tmp = None
            try:
                # Include 1 minute timeout in request for sites with no error OR response (freezes loop)
                tmp = requests.head(i, timeout=60).status_code
                with open(os.path.join(mainDir,outFilename), 'a', newline='') as write_obj:
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    # Add contents of list as last row in the csv file
                    csv_writer.writerow([region, i, str(tmp)])
                print('success', '\n')
            except requests.exceptions.RequestException as e:
                print('requests error')
                print(e, '\n')
                with open(os.path.join(mainDir,outFilename), 'a', newline='') as write_obj:
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    # Add contents of list as last row in the csv file
                    csv_writer.writerow([region, i, str(e)])
                # setOfCodes.add(str(sys.exc_info()[0]))
            except:
                print('other error')
                print(sys.exc_info()[0], '\n')
                with open(os.path.join(mainDir,outFilename), 'a', newline='') as write_obj:
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    # Add contents of list as last row in the csv file
                    csv_writer.writerow([region, i, str(str(sys.exc_info()[0]))])

        print("Done with HTTP.")

# Run Code
# ---

# Archive the list of URLs using Wayback python library

# ===== Cell 8 =====
# Get all the reference URLs from a tab
listOfRefs = getURLs(sheetName, tabNm, archivedDirectory)

# Hack if need to read in a file, like References tab
#listOfRefs = pd.read_excel(r'/Users/jennymartos/Documents/GEM/GRFF/wiki_references/GGPT-References-master/output/ArchivedRefs_Reserves and Production_2021-06-27 14_45 fails.xlsx')['originalURL'].tolist()

# ===== Cell 9 =====
# Pull out only the ones not already archived
nURLs = getNewURLs(master, listOfRefs)
print(len(nURLs))

# ===== Cell 10 =====
# Archive the new URLs, writing the results to a file
tmpFile = waybackHandler(nURLs, tabNm, archivedDirectory)

# ===== Cell 11 =====
# sanity check
print(tmpFile)

# ===== Cell 12 =====
# Build file of just unprocessed URLs that need to go through Citoid
# Since it's possible archived URLs haven't been through citoid, don't use nURLs
# go back to original URL list from tab
citoidFile(listOfRefs, citoidMaster)

# ===== Cell 13 =====
# Build file of URL http statuses
pingURL(archivedDirectory, tabNm, nURLs)
