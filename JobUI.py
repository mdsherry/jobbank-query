#!/usr/bin/env python3
import jobMiner
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_jobbankmain


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
			self.queryResults.clear()
			self.queryResults.setSortingEnabled( False )
			headers = ["ID", "Title", "Salary (low)"]
			self.queryResults.setColumnCount( len( headers ) )
			self.queryResults.setHorizontalHeaderLabels( headers )

			results = []
			for jobId, job in self.miner.data.items():
				if p( job ):
					results.append( job )
					#print( job["id"] )
			self.queryResults.setRowCount( len( results ) )
			for i, job in enumerate( results ):
					item = QTableWidgetItem( str( job["id"] ) )
					item.data = str( job["id"] )
					self.queryResults.setItem( i, 0, item )
					self.queryResults.setItem( i, 1, QTableWidgetItem( job["title"]))
					self.queryResults.setItem( i, 2, QTableWidgetItem( str( job["salary-low"])) )
			self.queryResults.setSortingEnabled( True )
			
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