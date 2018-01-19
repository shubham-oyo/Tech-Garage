from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import csv
import requests
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/callcentre'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

column_list = ['Ticket Id', 'Status', 'Priority', 'Source', 'Agent', 'Group', 'Created Time', 'Resolved Time']
primary_key = 'Ticket Id'
plotly.tools.set_credentials_file(username='gaurav54', api_key='Ec1QpRXJ8WJygkYwkl2U')
py.sign_in('gaurav54', 'Ec1QpRXJ8WJygkYwkl2U') # Replace the username, and API key with your credentials.

class CallCentre(db.Model):
	__tablename__ = 'callcentre'

	ticketId = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String())
	priority = db.Column(db.String())
	source = db.Column(db.String())
	agent = db.Column(db.String())
	group = db.Column(db.String())
	createdAt =  db.Column(db.String(), nullable=True)
	resolvedAt = db.Column(db.String(), nullable=True)

	def __init__(self, id, status, priority, source, agent, group, createdAt, resolvedAt):
		self.id = id
		self.status = status
		self.priority = priority
		self.source = source
		self.agent = agent
		self.group = group
		self.createdAt = createdAt
		self.resolvedAt = resolvedAt

	def __repr__(self):
		return "ticketId: %r | status: %r | priority: %r | source: %r | agent: %r | group: %r | created_time: %r | resolved_time: %r" %(str(self.ticketId), self.status, self.priority, self.source, self.agent, self.group, self.createdAt, self.resolvedAt)

def parseCsv():
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
		obj = CallCentre(l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])
		db.session.add(obj)
	db.session.commit()
	return "Success"


@app.route("/report")
def generateReports():
	fmt = '%Y-%m-%d %H:%M:%S'
	nowDate = date.today()
	nowTime = datetime.now()
	PRIORITY = ["Urgent", "High", "Medium"]
	STATUS = ["Open", "Resolved", "Closed", "Pending", "Waiting on finance", "Waiting on operations", "Waiting on Recon", "Call Back To be Arranged", "Call Back Scheduled", "Customer Responded", "Followed up by guest", "Guest Not Contactable", "Unassigned"]

	# Total tickets
	totalTickets = CallCenter.query.filter(((now - datetime.strptime(CallCenter.createdAt, fmt)).minutes <= 60), CallCenter.Group == "SIG IB").count()
	# Tickets resolved
	resolvedTickets = CallCenter.query.filter(((now - datetime.strptime(CallCenter.resolvedAt, fmt)).minutes <= 60), CallCenter.Status == "Resolved", CallCenter.Group == "SIG IB").count()
	# Tickets resolved under 1 hour
	resolvedWithinOneHour = CallCenter.query.filter
	# Total tickets created by captain
	resolvedTickets = CallCenter.query.filter(((datetime.strptime(CallCenter.createdAt, fmt) - now).minutes <= 60), CallCenter.Agent != "No Agent", CallCenter.Group == "SIG IB").count()
	# Status vs priority
	i = 1
	for pr in PRIORITY:
		for st in STATUS:
			tickets[i] = CallCenter.query.filter(((datetime.strptime(CallCenter.createdAt, fmt) - now).minutes <= 60), CallCenter.Priority == pr, CallCenter.Status == st)
			# tickets[pr + st] = CallCenter.query.filter(((datetime.strptime(CallCenter.createdAt, fmt) - now).minutes <= 60), CallCenter.Priority == pr, CallCenter.Status == st)
			i += 1
	i = 1
	tableRows = list()
	for st in STATUS:
		tableRows.append([st, tickets[i], tickets[i+1], tickets[i+2], tickets[i]+tickets[i+1]+tickets[i+2]])
		i += 3


	trace = go.Table(header=dict(values=['Status', PRIORITY]),
					cells=dict(values=tableRows))
	data=[trace]
	layout = go.Layout(title="Daily report - " + nowDate)
	# layout = go.Layout(title="Daily report - " + nowDate, width=800, height=678)
	fig = go.Figure(data=data, layout=layout)

	py.image.save_as(fig, filename='report.png')
	return "Success"


@app.route("/sendMessage")
def sendMessage():
	payload = { 'to': 'alwaysLast',
				'type': 'image',
				'client': 'OYO Call Center',
				'eid': 'qqqqq',
				'text': 'Daily reports',
				'file': 'photo.jpg'
			}
	requests.post("postman-prod-env-1.ap-southeast-1.elasticbeanstalk.com/whatsapp/internal/send", data=payload)
	return "Success"

def test():
	db.create_all()
	admin = CallCentre(1, "Resolved", "Medium", "Portal", "abc", "SIG IB", "2018-01-19 17:54:13", "2018-01-19 18:00:36")
	db.session.add(admin)
	db.session.commit()

@app.route("/run")
def run():
	r = requests.get('https://oyorooms.freshdesk.com/reports/scheduled_exports/2658061516364627/download_file.json', auth=('29ecd4SXzdbNYsmDJp0Z', 'X'))
	csvURL = ((r.json())["export"])["url"]
	csvData = requests.get(csvURL)
	with open("data.csv", "w") as csvFile:
		csvFile.write(csvData.content)
	#test()
	parseCsv()
	return "Success"