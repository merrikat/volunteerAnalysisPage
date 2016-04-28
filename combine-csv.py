"""
Combine .csv files into a single .csv file with all fields

2013-Nov-25 by Robert Woodhead, trebor@animeigo.com

Usage:

	python combine-csv.py {csv folder} {output file} [{optional count field name}]

Where:

	{csv folder} is a folder containing .csv files.
	{output file} is the destination file.
	{optional count field name} if present, is added to the list of fields; only unique lines
		are output, with a count of how many occurrences.

		IMPORTANT: If NOT PRESENT, then an additional field with the source file name of the line is appended.
		If you are outputting field counts, the source file name line is not emitted because the same line
		could be present in multiple files.
 
Output:

	Reads all the .csv files in the csv folder. Compiles a list of all the
	header fields that are present. Rereads the files, and outputs a single
	.csv containing all the records, shuffling fields to match the global
	header fields. Combines contents of duplicate fields using a | delimiter.

	Adds either a source file field or a count field (with definable name) to each line.

"""

import sys
import os
import glob
import csv
import copy

#
# Globals
#

error_count = 0				# number of errors encountered during processing

#
# Error reporting
#

def add_error(desc):

	global error_count
	
	error_count += 1
	sys.stderr.write(desc + '\n')

def optional(caption,value):

	if value == '':
		return ''
	else:
		return caption + value + '\n'

def cleanup(str):

	while str.rfind('  ') != -1:
		str = str.replace('	 ',' ')

	return str

#
# process command line arguments and execute
#


if __name__ == '__main__':

	if not (3 <= len(sys.argv) <= 4):
		print 'usage: python combine-csv.py {thread folder} {output file} [{optional count field name}]'
		sys.exit(1)

	hdrList = []
	hdrLen = []
	
	doCount = (len(sys.argv) == 4)
	counts = {}

	# get the headers
	
	for filename in glob.iglob(os.path.join(sys.argv[1],'*.csv')):
		with open(filename,'rb') as f:
			csvIn = csv.reader(f)
			hdr = csvIn.next()
			hdr[0] = hdr[0].replace('\xef\xbb\xbf','')
			hdrList.append((len(hdr),hdr))
	
	# construct the list of unique headers
	
	hdrList.sort(reverse=True)

	hdrs = []
	template = []
	
	for t in hdrList:
		for f in t[1]:
			if not (f in hdrs):
				hdrs.append(f)
				template.append('')
		
	if doCount:
		hdrs.append(sys.argv[3])
	else:
		hdrs.append('Source File')
	
	# output the combined file
	
	with open(sys.argv[2],'wb') as of:
		csvOut = csv.writer(of)
		csvOut.writerow(hdrs)
		for filename in glob.iglob(os.path.join(sys.argv[1],'*.csv')):
			with open(filename,'rb') as f:
				csvIn = csv.reader(f)
				hdr = csvIn.next()
				hdr[0] = hdr[0].replace('\xef\xbb\xbf','')
				for row in csvIn:
					newRow = list(template)
					for i,v in enumerate(row):
						j = hdrs.index(hdr[i])
						if newRow[j] == '':
							newRow[j] = v
						else:
							newRow[j] = newRow[j] + '|' + v
					if doCount:
						newRow = tuple(newRow)
						if newRow in counts:
							counts[newRow] += 1
						else:
							counts[newRow] = 1
					else:
						newRow.append(filename)
						csvOut.writerow(newRow)

		# if doing counts, output newRow

		print counts

		for k,v in counts.iteritems():
			k = list(k)
			k.append(v)
			csvOut.writerow(k)
