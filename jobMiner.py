import re

from lxml import html
from urllib.request import urlopen
import concurrent.futures
import pickle

def getId( url ):
	url = url.split('?', 1)[1]
	return int( dict( [pair.split('=') for pair in url.split('&') ] )['OrderNum'] )

def stripStrong( el ):
	el.xpath("strong")[0].drop_tree()
	return el.text_content()

class JobMiner( object ):

	def __init__( self ):
		try:
			f = open("cached", 'rb')
			self.data = pickle.load( f )
		except:
			self.data = {}

	def save(self):
		f = open("cached", 'wb')
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
		
		#page = open('temp', 'rt')
		page = urlopen( url )
		
		tree = html.parse( page )
		# Get all of the links from this page, while also grabbing the URL for the next page.
		jobLinks = tree.xpath( "//div[contains( @class, 'jbBox' )]//strong/a")
		executor = concurrent.futures.ThreadPoolExecutor( max_workers=5 )
		links = [link.attrib['href'] for link in jobLinks]

		ids = map( getId, links )
		jobs = executor.map( self.getJob, ids )
		# Need to grab subsequent pages too
		return list( jobs )



	def getJob( self, jobId ):
		if jobId in self.data:
			return None
		# Check first if we've retrieved this one before; how often do we need to recheck for changes?
		page = urlopen( "http://www.jobbank.gc.ca/detail-eng.aspx?OrderNum={}&Source=JobPosting".format( jobId ) )
		print("Retrieving job #{}".format(jobId))
		tree = html.parse( page )
		entry = {}
		body = tree.xpath("//div[@id='formatCont_en']")[0]
		if body is None:
			print("Invalid job")
			return None
		else:
			title = body.xpath("//span[@class='JobTitle']")[0]
			entry['title'] = title.text_content()
			# Need to trim whitespace here

			termsOfEmployment = body.xpath("p[@id='termOfEmployment']")[0]
			entry['termsofemployment'] = stripStrong( termsOfEmployment ).split(', ')

			entry["salary"] = stripStrong( body.xpath("p[@id='salary']")[0] )
			entry["startdate"] = stripStrong( body.xpath("p[@id='anticipatedStartDate']")[0] )
			entry["location"] = stripStrong( body.xpath("p[@id='location']")[0] )
			entry["employer"] = stripStrong( body.xpath("p[@id='employer']")[0] )

			entry['requirements'] = requirements = {}
			reqs = body.xpath("div[@id='skillRequirements']/div[@class='indent1']")
			for req in reqs:
				name = req.xpath("strong")[0].text_content()
				name = name.replace("Type of", "")
				name = re.sub( "\W","", name )
				
				value = stripStrong( req )
				requirements[name.lower()] = value

		self.data[jobId] = entry
		return (jobId, entry)

if __name__ == "__main__":
	miner = JobMiner()
	# miner.data = {}
	# print (miner.getJobs( searchRegions = ["GON008"], recency = "E7Days" ))
	# miner.save()
	reqs = set()
	from grammar import parse
	p = parse("[requirements::*] doesn't contain 'Drug test'")
	#p = parse("[requirements::Languages] doesn't contain \"French\"")

	for jobId, job in miner.data.items():
		for req in job['requirements']:
			reqs.add( req )
		if p(job):
			print (job['requirements'])
		
	print (reqs)