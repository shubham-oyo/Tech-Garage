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

class CallCentre(db.Model):
	__tablename__ = 'callcentre'

	ticketId = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(), nullable=False)
	priority = db.Column(db.String(), nullable=False)
	source = db.Column(db.String(), nullable=False)
	agent = db.Column(db.String(), nullable=False)
	group = db.Column(db.String(), nullable=False)
	created_time =  db.Column(db.DateTime, nullable=False)
	resolved_time = db.Column(db.DateTime, nullable=False)


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

# db.create_all()
# admin = CallCentre(1, "Resolved", "Medium", "Portal", "abc", "SIG IB", "2018-01-19 17:54:13", "2018-01-19 18:00:36")
# db.session.add(admin)
# db.session.commit()

def parseCsv():
	df = pd.read_csv("data.csv")
	columns_data = []
	for columns in column_list:
		columns_data.append(df[columns])
	for i in columns_data:
		print i


@app.route("/run")
def run():
	r = requests.get('https://oyorooms.freshdesk.com/reports/scheduled_exports/2658061516364627/download_file.json', auth=('29ecd4SXzdbNYsmDJp0Z', 'X'))
	csvURL = ((r.json())["export"])["url"]
	csvData = requests.get(csvURL)
	with open("data.csv", "w") as csvFile:
		csvFile.write(csvData.content)
	parseCsv()
	return "Success"