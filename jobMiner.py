#!/usr/bin/env python3
import re

from lxml import html
from urllib.request import urlopen
from urllib.error import URLError
import concurrent.futures
import pickle
import datetime

def getId( url ):
	"""Takes a JobBank URL and extracts the job ID from it"""
	url = url.split('?', 1)[1]
	return int( dict( [pair.split('=') for pair in url.split('&') ] )['OrderNum'] )

def stripStrong( el ):
	"""Removes a <strong> tag and its contents, and returns the remaining text."""
	el.xpath("strong")[0].drop_tree()
	return el.text_content()

def cleanTitle( s ):
	return re.sub( r"(.*)\s+(\(NOC: \d+\))\s+", r"\1 \2", s )

def parseSalary( s ):
	"""Extracts the hourly rate from a salary statement.

	The four main cases that it handles are:
		$xxx to $yyy Hourly
		$xxx Hourly
		$xxx to $yyy Yearly
		$xxx Yearly
	In the latter two cases, it also looks for a statement of how many hours are worked per week.
	It then uses this figure to convert the annual rate to an hourly one, working on the assumption
	of 52.125 weeks per year (produces correct average for working days per year).

	If a number of hours per week is not provided, it assumes 40 hours per week (or 2087 per year).

	This function doesn't take benefits into account.
	"""

	#TODO: Handle 'Monthly'
	match = re.match( r".*for\s+([0-9.,]+)\s+hours\s+per\s+week", s, re.IGNORECASE )
	if match:
		hours = float( match.group(1).replace(',','') )
	else:
		hours = 40
	# Check for hourly first
	match = re.match(r"\$([0123456789,.]+)\s+to\s+\$([0123456789,.]+)\s+Hourly", s, re.IGNORECASE )
	if match:
		return float( match.group(1).replace(',','') ), float( match.group(2).replace(',','') ), hours
	match = re.match(r"\$([0123456789,.]+)\s+Hourly", s, re.IGNORECASE )
	if match:
		return float( match.group(1).replace(',','') ), float( match.group(1).replace(',','') ), hours
	low = high = None
	match = re.match(r"\$([0123456789,.]+)\s+to\s+\$([0123456789,.]+)\s+Yearly", s, re.IGNORECASE )
	if match:
		low, high = float( match.group(1).replace(',','') ), float( match.group(2).replace(',','') )
	else:
		match = re.match(r"\$([0123456789,.]+)\s+Yearly", s, re.IGNORECASE )
		if match:
			low, high = float( match.group(1).replace(',','') ), float( match.group(1).replace(',','') )

	if low:
		weeksPerYear = 52.125 # Average
		low /= (weeksPerYear * hours)
		high /= (weeksPerYear * hours)
		return low, high, hours
		
	# Some jobs don't provide any wage information that we can parse. 
	# For example, jobs that only pay on commission.

	return 0, 0, 0


class JobMiner( object ):

	def __init__( self, fname="cached" ):
		self.filename = fname
		try:
			f = open(fname, 'rb')
			self.data = pickle.load( f )
		except:
			self.data = {}

	def save(self):
		f = open(self.filename, 'wb')
		pickle.dump( self.data, f )

	def getJobs( self, searchRegions = [], jobCategories=[], recency=None):

		url = "http://www.jobbank.gc.ca/res-eng.aspx?RchJobType=Reg_jobs"
		if searchRegions:
			url += "&CmmGrp=" + ','.join( searchRegions )
		if jobCategories:
			url += "&Categ=" + ','.join( jobCategories )
		if recency:
			url += "&TmFrm=" + recency
		url += "&OpPage=50&nsrc=1"
		links = []
		pageNum = 1
		while True:

			page = urlopen( url + "&PgNum={}".format( pageNum ) )
		
			tree = html.parse( page )
			# Get all of the links from this page, while also grabbing the URL for the next page.
			jobLinks = tree.xpath( "//div[contains( @class, 'jbBox' )]//strong/a")
			if not jobLinks:
				break
			links += [link.attrib['href'] for link in jobLinks]
			pageNum += 1
		ids = map( getId, links )
		executor = concurrent.futures.ThreadPoolExecutor( max_workers=5 )
		jobs = executor.map( self.getJob, ids )
		# Need to grab subsequent pages too
		return list( jobs )



	def getJob( self, jobId ):
		if jobId in self.data:
			return None
		# Check first if we've retrieved this one before; how often do we need to recheck for changes?
		try:
			page = urlopen( "http://www.jobbank.gc.ca/detail-eng.aspx?OrderNum={}&Source=JobPosting".format( jobId ) )
		except URLError as ex:
			print("Error retrieving job #{}. Error: {}".format( jobId, ex ) )
			return None
		print("Retrieving job #{}".format(jobId))
		tree = html.parse( page )
		entry = {}
		body = tree.xpath("//div[@id='formatCont_en']")[0]
		if body is None:
			print("Invalid job")
			return None
		else:
			title = body.xpath("//span[@class='JobTitle']")[0]
			entry['id'] = jobId
			entry['title'] = cleanTitle( title.text_content() )
			# Need to trim whitespace here

			termsOfEmployment = body.xpath("p[@id='termOfEmployment']")[0]
			entry['termsofemployment'] = stripStrong( termsOfEmployment ).split(', ')

			entry["salary"] = stripStrong( body.xpath("p[@id='salary']")[0] )
			
			entry["salary-low"], entry["salary-high"], entry["hoursperweek"] = parseSalary( entry["salary"] )
			if entry["salary-low"] > 1000:
				# Some people say hourly instead of yearly. Let's correct their mistake and try again.
				entry["salary"] = entry["salary"].replace("Hourly", "Yearly", 1)
				entry["salary-low"], entry["salary-high"], entry["hoursperweek"] = parseSalary( entry["salary"] )
			entry['salaried'] = 'Yearly' in entry["salary"]

			entry["startdate"] = stripStrong( body.xpath("p[@id='anticipatedStartDate']")[0] )
			if entry["startdate"] == 'As soon as possible':
				entry["startdate"] = datetime.datetime.now()
			else:
				try:
					entry["startdate"] = datetime.datetime.strptime( entry['startdate'], "%Y/%m/%d")
				except ValueError:
					# Leave the stored date/time as is.
					pass
			entry["location"] = stripStrong( body.xpath("p[@id='location']")[0] )
			entry["employer"] = stripStrong( body.xpath("p[@id='employer']")[0] )
			entry["expires"] = stripStrong( body.xpath("p[@id='AdvUntil_en']")[0] )
			try:
				entry["expires"] = datetime.datetime.strptime( entry['expires'], "%Y/%m/%d" )
			except:
				# Leave the expiration date as it is
				pass
			entry['requirements'] = requirements = {}
			reqs = body.xpath("div[@id='skillRequirements']/div[@class='indent1']")
			for req in reqs:
				name = req.xpath("strong")[0].text_content()
				name = name.replace("Type of", "")
				name = re.sub( "\W","", name )
				
				value = stripStrong( req )
				requirements[name.lower()] = value

		self.data[jobId] = entry
		if len( self.data ) % 10 == 0:
			self.save()
		return (jobId, entry)

if __name__ == "__main__":
	import argparse
	import sys
	parser = argparse.ArgumentParser( description="Processes JobBank.gc.ca jobs")
	parser.add_argument('--scrape', action="store_true", help='Scrape jobs from the site')
	parser.add_argument('--query', help='Query to run against collected jobs')
	parser.add_argument('--file', type=argparse.FileType('wt'), default=sys.stdout, help="Filename to use for output (defaults to stdout)")
	parser.add_argument('--listreqs', action="store_true", help="List requirement names")
	args = parser.parse_args()
	miner = JobMiner()
	for k,v in miner.data.items():
	 	v["salary-low"], v["salary-high"], v["hoursperweek"] = parseSalary( v["salary"] )
		
	miner.save()
	if args.scrape:
		nJobs = len( miner.data )
		results = miner.getJobs( searchRegions = ["GON008"], recency = "E7Days" )
		skipped = sum( 1 for x in results if x is None)
		newNJobs = len( miner.data )
		print("Retrieved {} jobs; {} jobs total. {} skipped or failed.".format( newNJobs - nJobs, newNJobs, skipped ) )
		# Purge expired jobs
		now = datetime.datetime.now()
		deleted = []
		for jobId, job in miner.data.items():
			if ('expires' not in job or 
				type( job['expires'] ) != datetime.datetime or
				job['expires'] < now ):
				deleted.append( jobId )
		for jobId in deleted:
			del miner.data[ jobId ]
		if deleted:
			print("Removed {} expired jobs.".format( len( deleted ) ) ) 
		miner.save()
	reqs = set()
	from grammar import parse
	if args.query:
		p = parse( args.query )
	else:
		p = lambda x: False
	results = []
	#p = parse("[requirements::*] matches /.*Drug test.*/")
	#p = parse("[requirements::Languages] doesn't contain \"French\"")

	for jobId, job in miner.data.items():
		for req in job['requirements']:
			reqs.add( req )
		if p( job ):
			results.append( job )
	if args.listreqs:
		args.file.write('\n'.join(sorted(reqs)))
		args.file.write("\n")
	if args.query:
		from mako.template import Template
		mytemplate = Template( filename="report.mako" )
		args.file.write( mytemplate.render( results=results, date=datetime.datetime.now(), query=args.query, nJobs = len( miner.data ) ) )
