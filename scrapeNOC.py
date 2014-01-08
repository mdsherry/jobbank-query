#!/usr/bin/env python3
import re
from lxml import html

tree = html.parse( open( 'nocinfo.html', 'rt'))
toplayer = tree.xpath( "//div[@class='center']/div/h2")
top_classifications = {}
for entry in toplayer:
	number, desc = entry.text_content().split('\xa0', 1)
	top_classifications[number] = desc

major_classifications = {}
major_numbers = tree.xpath( "//div[@class='center']/div/h3")
major_labels = tree.xpath( "//div[@class='center']/div/h4")
for numbers, entry in zip(major_numbers, major_labels):
	match = re.match( r"Major Group (\d+)([-/](\d+))?", numbers.text_content())
	if match:
		start = int( match.group(1) )
		end = start

		if match.group(3):
			end = int( match.group(3) )
		for i in range( start, end+1 ):
			major_classifications["%02d" % i] = entry.text_content()
	

minor = tree.xpath( "//div[@class='center']/div//h5")
minor_classifications = {}
for entry in minor:
	number, desc = entry.text_content().split('\xa0', 1)
	minor_classifications[number] = desc	


individual = tree.xpath( "//div[@class='center']/div//li/a")
individual_classifications = {}
for entry in individual:
	number, desc = entry.text_content().split('\xa0', 1)
	individual_classifications[number] = desc	

f = open('NOC.py', 'wt')
import pprint
pp = pprint.PrettyPrinter(indent=4,stream=f)
f.write("top = ")
pp.pprint( top_classifications )
f.write("\n")

f.write("major = ")
pp.pprint( major_classifications )
f.write("\n")

f.write("minor = ")
pp.pprint( minor_classifications )
f.write("\n")

f.write("individual = ")
pp.pprint( individual_classifications )
f.write("\n")
