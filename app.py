from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
from requests_toolbelt.multipart.encoder import MultipartEncoder
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
		columns_data[columns] = df[columns].fillna("")
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


# @app.route("/test")
# def test():
# 	ntime = "2018-01-14 17:54:13"
# 	fmt = '%Y-%m-%d %H:%M:%S'
# 	today = date.today()
# 	now = datetime.now()
# 	print(now)
# 	print(datetime.strptime(ntime, fmt))

# 	ts1 = now - datetime.strptime(ntime, fmt)
# 	# ts1 = datetime.strptime(now, fmt) - datetime.strptime(ntime, fmt)
# 	print(ts1)
# 	return "das"

def generateAgingReport():
	fmt = '%Y-%m-%d %H:%M:%S'
	nowDate = date.today()
	last60MinTime = (datetime.now() - timedelta(minutes=60)).strftime(fmt)
	last12HrsTime = (datetime.now() - timedelta(hours=12)).strftime(fmt)
	last24HrsTime = (datetime.now() - timedelta(hours=24)).strftime(fmt)
	last36HrsTime = (datetime.now() - timedelta(hours=36)).strftime(fmt)
	last48HrsTime = (datetime.now() - timedelta(hours=48)).strftime(fmt)
	last72HrsTime = (datetime.now() - timedelta(hours=72)).strftime(fmt)

	aging = ["AGING" , ">72hrs", "48-72hrs", "36-48hrs", "24-36hrs", "12-24hrs", "<12hrs", "Total"]
	STATUS = ["Open", "Pending", "Waiting on finance", "Waiting on operations", "Waiting on Recon", "Call Back To be Arranged", "Call Back Scheduled", "Customer Responded", "Followed up by guest", "Guest Not Contactable", "Unassigned"]

	pendency = ["Ticket Pendency"]
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt > last72HrsTime).count())
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt > last48HrsTime, CallCentre.createdAt <= last72HrsTime).count())
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt > last36HrsTime, CallCentre.createdAt <= last48HrsTime).count())
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt > last24HrsTime, CallCentre.createdAt <= last36HrsTime).count())
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt > last12HrsTime, CallCentre.createdAt <= last24HrsTime).count())
	pendency.append(CallCentre.query.filter(CallCentre.group == "SIG IB", CallCentre.status.in_(STATUS), CallCentre.createdAt <= last12HrsTime).count())
	trace1 = go.Table(header=dict(values=aging),
	 				cells=dict(values=pendency))
	pendency.append(sum(pendency[1:]))
	data1=[trace1]
	print aging
	print pendency
	layout1 = go.Layout(title="Daily report - " + datetime.now().strftime("%Y/%m/%d %H:%M:%S"), width=900, height=550)
	fig1 = go.Figure(data=data1, layout=layout1)
	py.image.save_as(fig1, filename='report1.png')


# @app.route("/report")
def generateStatusReport():
	fmt = '%Y-%m-%d %H:%M:%S'
	nowDate = date.today()
	last60MinTime = (datetime.now() - timedelta(minutes=60)).strftime(fmt)
	print datetime.now(), last60MinTime

	PRIORITY = ["Urgent", "High", "Medium"]
	STATUS = ["Open", "Pending", "Waiting on finance", "Waiting on operations", "Waiting on Recon", "Call Back To be Arranged", "Call Back Scheduled", "Customer Responded", "Followed up by guest", "Guest Not Contactable", "Unassigned"]
	RSTATUS = ["Resolved", "Closed"]
	# Total tickets
	totalTickets = CallCentre.query.filter(CallCentre.createdAt >= last60MinTime, CallCentre.group == 'SIG IB').count()
	print totalTickets
	
	# Tickets resolved
	resolvedTickets = CallCentre.query.filter(last60MinTime <= CallCentre.resolvedAt, CallCentre.status == "Resolved", CallCentre.group == "SIG IB").count()
	
	# # Total tickets created by captain
	resolvedTicketsByCaptain = CallCentre.query.filter(last60MinTime <= CallCentre.createdAt, CallCentre.agent != "No Agent", CallCentre.group == "SIG IB").count()

	print totalTickets, resolvedTickets, resolvedTicketsByCaptain

	l = [0 for i in xrange(0, len(STATUS))]
	tickets = [STATUS + ['Grand Total']]

	# # Status vs priority
	for pr in PRIORITY:
		ticket = []
		for index, st in enumerate(STATUS):
			ticket.append(CallCentre.query.filter(CallCentre.createdAt >= last60MinTime, CallCentre.priority == pr, CallCentre.status == st).count())
			l[index] += ticket[-1]
		ticket.append(sum(ticket))
		tickets.append(ticket)
	print l
	l.append(sum(l))
	tickets.append(l)
	for i in tickets:
		print " ".join([str(r) for r in i])

	PRIORITY.insert(0, 'Status')
	PRIORITY.append('Pendency')

	trace = go.Table(header=dict(values=PRIORITY, 
								fill = dict(color='#C2D4FF'),
								align = ['left']*5),
	 				cells=dict(values=tickets, fill = dict(color='#F5F8FF'), align = ['left']*5))
	data=[trace]
	layout = go.Layout(title="Daily report - " + datetime.now().strftime("%Y/%m/%d %H:%M:%S"), width=900, height=550)
	fig = go.Figure(data=data, layout=layout)
	py.image.save_as(fig, filename='report.png')

	return "Success"


#@app.route("/sendMessage", methods=["POST"])
def sendMessage():
	payload = MultipartEncoder(fields = { 'to': '8764066357',
											'type': 'Image',
											'client': 'OYO Call Center',
											'eId': 'qqqqq',
											'file': ('report.png', open('./report.png', 'rb'), 'image/png'),
											'caption': 'Hourly call centre report',
										})
	headers = { 'Content-Type': payload.content_type}
	# requests.post("https://postman-prod-env-1.ap-southeast-1.elasticbeanstalk.com/whatsapp/internal/send", data=payload)
	print requests.post("http://54.254.232.208:8080/whatsapp/internal/send", data=payload, headers=headers).text
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
	test()
	parseCsv()
	generateStatusReport()
	generateAgingReport()
	sendMessage()
	return "Success"