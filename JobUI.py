#!/usr/bin/env python3
import jobMiner
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_jobbankmain
import ui_jobentry

class JobEntry( QMainWindow, ui_jobentry.Ui_JobEntry ):
	def __init__( self, parent, job ):
		super( JobEntry, self ).__init__( parent )
		self.setupUi( self )

		self.job = job
		self.id.setText( str( job['id'] ) )
		self.title.setText( job['title'] )

class Form( QMainWindow, ui_jobbankmain.Ui_MainWindow ):
	def __init__( self, parent=None ):
		super( Form, self ).__init__( parent )
		self.setupUi( self )
		self.queryText.setPlainText("[id] > 3")
		self.queryText.selectAll()

		self.runQuery.clicked.connect( self.evalQuery )
		
		self.connect( self.actionLoad_Query, SIGNAL("activated()"), self.loadQuery )
		self.connect( self.actionLoad_Query, SIGNAL("activated()"), self.saveQuery )
		self.miner = jobMiner.JobMiner()

	def evalQuery( self ):
		from grammar import parse
		
		p = parse( self.queryText.toPlainText() )
		if p:
			
			results = []
			for jobId, job in self.miner.data.items():
				if p( job ):
					results.append( job )
					#print( job["id"] )
			
			for i, job in enumerate( results ):
				item = JobEntry( None, job )
				self.queryResultsLayout.addWidget( item )
				item.show()
				if i > 4:
					break
			
			
		else:
			print("Invalid query!")

	def loadQuery( self ):
		print("Load query")

	def saveQuery( self ):
		print("Save query: " + self.queryText.text() )
import sys
app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()