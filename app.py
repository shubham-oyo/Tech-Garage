from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
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



@app.route("/test")
def test():
	ntime = "2018-01-14 17:54:13"
	fmt = '%Y-%m-%d %H:%M:%S'
	today = date.today()
	now = datetime.now()
	print(now)
	print(datetime.strptime(ntime, fmt))

	ts1 = now - datetime.strptime(ntime, fmt)
	# ts1 = datetime.strptime(now, fmt) - datetime.strptime(ntime, fmt)
	print(ts1)
	return "das"


@app.route("/report")
def generateReports():
	fmt = '%Y-%m-%d %H:%M:%S'
	nowDate = date.today()
	last60MinTime = (datetime.now() - timedelta(minutes=60)).strftime(fmt)
	print datetime.now(), last60MinTime

	PRIORITY = ["Urgent", "High", "Medium"]
	STATUS = ["Open", "Resolved", "Closed", "Pending", "Waiting on finance", "Waiting on operations", "Waiting on Recon", "Call Back To be Arranged", "Call Back Scheduled", "Customer Responded", "Followed up by guest", "Guest Not Contactable", "Unassigned"]
	# Total tickets
	# totalTickets = CallCentre.query.filter(((nowTime - pd.to_datetime(CallCentre.createdAt, format=fmt)).minutes <= 60), CallCentre.group == "SIG IB").count()
	totalTickets = CallCentre.query.filter(CallCentre.createdAt >= last60MinTime, CallCentre.group == 'SIG IB').count()
	print totalTickets
	
	# Tickets resolved
	# resolvedTickets = CallCentre.query.filter(CallCentre.resolved != "", ((nowTime - datetime.strptime(CallCentre.resolvedAt, fmt)).minutes <= 60), CallCentre.status == "Resolved", CallCentre.group == "SIG IB").count()
	resolvedTickets = CallCentre.query.filter(last60MinTime <= CallCentre.resolvedAt, CallCentre.status == "Resolved", CallCentre.group == "SIG IB").count()
	
	# # Tickets resolved under 1 hour
	# resolvedWithinOneHour = CallCentre.query.filter
	
	# # Total tickets created by captain
	# resolvedTickets = CallCentre.query.filter(((datetime.strptime(CallCentre.createdAt, fmt) - now).minutes <= 60), CallCentre.agent != "No Agent", CallCentre.group == "SIG IB").count()
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
			#tickets[i] = CallCentre.query.filter(((datetime.strptime(CallCentre.createdAt, fmt) - now).minutes <= 60), CallCentre.priority == pr, CallCentre.status == st)
			# tickets[pr + st] = CallCentre.query.filter(((datetime.strptime(CallCentre.createdAt, fmt) - now).minutes <= 60), CallCentre.Priority == pr, CallCentre.Status == st)
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
	# # layout = go.Layout(title="Daily report - " + nowDate, width=800, height=678)
	fig = go.Figure(data=data, layout=layout)
	#py.iplot(fig, filename = 'basic_table')

	py.image.save_as(fig, filename='report.png')
	return "Success"


@app.route("/sendMessage")
def sendMessage():
	payload = { 'to': 'alwaysLast',
				'type': 'image',
				'client': 'OYO Call Center',
				'eid': 'qqqqq',
				'text': 'Daily reports',
				'file': 'report.png'
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
	test()
	parseCsv()
	return "Success"