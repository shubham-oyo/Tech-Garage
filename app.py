from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
import pandas as pd
import csv


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/callcentre'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
column_list = ['Ticket Id', 'Status', 'Priority', 'Source', 'Agent', 'Group', 'Created Time', 'Resolved Time']
primary_key = 'Ticket Id'

class CallCentre(db.Model):
	__tablename__ = 'callcentre'

	ticketId = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String())
	priority = db.Column(db.String())
	source = db.Column(db.String())
	agent = db.Column(db.String())
	group = db.Column(db.String())
	created_time =  db.Column(db.String(), nullable=True)
	resolved_time = db.Column(db.String(), nullable=True)

	def __init__(self, id, status, priority, source, agent, group, created_time, resolved_time):
		self.ticketId = id
		self.status = status
		self.priority = priority
		self.source = source
		self.agent = agent
		self.group = group
		self.created_time = created_time
		self.resolved_time = resolved_time

	def __repr__(self):
		return "ticketId: %r | status: %r | priority: %r | source: %r | agent: %r | group: %r | created_time: %r | resolved_time: %r" %(str(self.ticketId), self.status, self.priority, self.source, self.agent, self.group, self.created_time, self.resolved_time)

def test():		
	print 'test'
	db.create_all()
	admin = CallCentre(4387072, "Resolved", "Medium", "Portal", "abc", "SIG IB", "2018-01-19 17:54:13", "2018-01-19 18:00:36")
	db.session.add(admin)
	db.session.commit()

def parseCsv():
	print 'here'
	df = pd.read_csv("data.csv")
	columns_data = {}
	for columns in column_list:
		columns_data[columns] = df[columns].fillna('')
	for i in columns_data[primary_key]:
		obj = CallCentre.query.get(i)
		if obj:
			db.session.delete(obj)
	for i in xrange(0, len(columns_data[primary_key])):
		l = []
		for column in column_list:
			l.append(columns_data[column][i])
		print l
		obj = CallCentre(l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])
		db.session.add(obj)
	db.session.commit()


@app.route("/run")
def run():
	r = requests.get('https://oyorooms.freshdesk.com/reports/scheduled_exports/2658061516364627/download_file.json', auth=('29ecd4SXzdbNYsmDJp0Z', 'X'))
	csvURL = ((r.json())["export"])["url"]
	csvData = requests.get(csvURL)
	print 'csv creation start'
	with open("data.csv", "w") as csvFile:
		csvFile.write(csvData.content)
	test()
	parseCsv()
	return "Success"