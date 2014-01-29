#!/usr/bin/env python3

import NOC
import re
import argparse

if __name__ == "__main__":

	parser = argparse.ArgumentParser( description="Processes JobBank.gc.ca jobs")
	parser.add_argument("--listtypes", action="store_true", help="List the overarching NOC types")
	parser.add_argument("--listmajor", action="store_true", help="List the major NOC catogories. If argument is provided, only list catogory numbers starting with that argument.")
	parser.add_argument("--listminor", action="store_true", help="List the minor NOC catogories. If argument is provided, only list catogory numbers starting with that argument.")
	parser.add_argument("--listall", action="store_true", help="List the NOC entries. If argument is provided, only list entry numbers starting with that argument.")

	parser.add_argument("--searchtypes", type=str, help="Search types for description")
	parser.add_argument("--searchmajor", type=str, help="Search major categories for description")
	parser.add_argument("--searchminor", type=str, help="Search types for description")
	parser.add_argument("--searchall", type=str, help="Search all for description")
	parser.add_argument("args", nargs="?")
	args = parser.parse_args()
	
	if args.listtypes:
		for key, value in sorted( NOC.top.items() ):
			print( "{}\t{}".format( key, value ) )

	if args.listmajor:
		for key, value in sorted( NOC.major.items() ):
			if not args.args or key.startswith( args.args ):
				print( "{}\t{}".format( key, value ) )
	
	if args.listminor:
		for key, value in sorted( NOC.minor.items() ):
			if not args.args or key.startswith( args.args ):
				print( "{}\t{}".format( key, value ) )

	if args.listall:
		for key, value in sorted( NOC.individual.items() ):
			if not args.args or key.startswith( args.args ):
				print( "{}\t{}".format( key, value ) )

	if args.searchtypes:
		needle = args.searchtypes.upper()
		for key, value in sorted( NOC.top.items() ):
			if needle in value.upper():
				print( "{}\t{}".format( key, value ) )

	if args.searchmajor:
		needle = args.searchmajor.upper()
		for key, value in sorted( NOC.major.items() ):
			if needle in value.upper():
				print( "{}\t{}".format( key, value ) )

	if args.searchminor:
		needle = args.searchminor.upper()
		for key, value in sorted( NOC.minor.items() ):
			if needle in value.upper():
				print( "{}\t{}".format( key, value ) )

	if args.searchall:
		needle = args.searchall.upper()
		for key, value in sorted( NOC.individual.items() ):
			if needle in value.upper():
				print( "{}\t{}".format( key, value ) )

	