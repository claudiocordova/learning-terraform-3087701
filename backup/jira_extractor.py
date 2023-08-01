# Import the required libraries
from datetime import timezone 
import datetime
from requests.auth import HTTPBasicAuth
import json
#import pandas as pd
import requests

# URL to Search all issues.
#url = "https://jira.ci.motional.com/rest/api/2/search"
url = "https://jira.ci.motional.com/atljira/rest/api/2/search"

# Create an authentication object,using
# registered emailID, and, token received.
#auth = HTTPBasicAuth("claudio.cordova@motional.com",
#					"NjUzMzUyMzg4NDI5OjY3kza/AgHzVeg/iwWmIA9PkfcB")


def test():
    return 'OK!'


auth = HTTPBasicAuth("claudio.cordova",
					"ODMzMzYwNTA0MjUyOkpYFy0KKY/Kod3MXuV2ZAqkuR/G")




# The Header parameter, should mention, the
# desired format of data.
headers = {
	"Accept": "application/json",
	"Authorization": "Bearer MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d"
}



#cookies = {'atlassian.xsrf.token': 'B0AE-MVIC-55BB-DCHW_fb5749bf40b119d425ecb8cfc104086d62f1b668_lin'}

#r = requests.post('http://wikipedia.org', cookies=cookies)
# Mention the JQL query.
# Here, all issues, of a project, are
# fetched,as,no criteria is mentioned.





#data = json.loads(json_str)
#customer = data['Customer']
#order_1 = data['Orders'][0]['Id']
#order_2 = data['Orders'][1]['Id']
#total = len(data['Orders'])
#print(f"Customer: {customer}, Orders: {order_1}, {order_2}, Total: {total}")



#{
#"expand": "schema,names",
# "startAt": 0,
# "maxResults": 50,
# "total": 4055,
# "issues": [
# {
# "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
# "id": "543323",
# "self": "https://jira.ci.motional.com/atljira/rest/api/2/issue/543323",
# "key": "MAPBUILD-4685",
# "fields": {
# "resolution": null,
# "customfield_11720": null,


#
#https://jira.ci.motional.com/atljira/rest/api/2/field

#
#https://jira.ci.motional.com/atljira/rest/api/2/issuetype


#
#https://jira.ci.motional.com/atljira/rest/api/2/issue/MAPBUILD-4354

#
#https://jira.ci.motional.com/atljira/rest/api/2/search?jql=key=MAPBUILD-4354


#expand
#http://localhost:8090/jira/rest/api/2/issue/MKY-1?expand=renderedFields


# api version 2
#https://developer.atlassian.com/server/jira/platform/jira-rest-api-version-2-tutorial-8946379/

#query = {
#	'jql': 'project = MAPBUILD and UPDATED >= -1d '
#}

parameters = {
	'jql': 'project = MAPBUILD and updated > startOfDay(-0d)'        #"2023-07-14T18:00"'
}


parameters = {
	'jql': 'project = MAPBUILD and updated > "2023-07-13"'        #"2023-07-14T18:00"'
}


parameters = {
	'jql': ' updatedDate > "2023-07-13 17:00 " and updatedDate <  "2023-07-14 17:00" and startAt = 51'        #"2023-07-14T18:00"'
}

#{'errorMessages': ["Date value '2023-07-13T21:24:33.000+0000' for field 'updated' is invalid. Valid formats include: 
# 'yyyy/MM/dd HH:mm', 
# 'yyyy-MM-dd HH:mm', 
# 'yyyy/MM/dd', 
# 'yyyy-MM-dd', 
# or a period format e.g. '-5d', '4w 2d'."], 'errors': {}}








time = datetime.datetime.now()
timeUTC = datetime.datetime.now(timezone.utc)
today = datetime.date.today()

print(today)
print(time)
print(time.strftime('%Y-%m-%d %H:%M'))
print(timeUTC)
print(timeUTC.strftime('%Y-%m-%d %H:%M'))




counter = 0
issuesLength = 1
startAt = -50

while issuesLength > 0:

	maxResults = 50
	startAt = startAt + maxResults
	

	parameters = {
		'jql': 'project = MAPBUILDDDDDDDD  and updatedDate > "2023-07-13 17:00 " and updatedDate <  "2023-07-14 17:00" ORDER BY created, id desc', 
		'startAt': startAt,
		'maxResults': maxResults,
		#'fields': "key,status,project,priority,issuetype,created,statuscategory"
	}

	print(parameters)

	response = requests.request("GET",url,headers=headers,params=parameters,timeout=30)
	responseJson = json.loads(response.text)

	if "startAt" in responseJson:
		startAt = responseJson['startAt']
		print(f"startAt: {startAt}")
	if "total" in responseJson:
		total = responseJson['total']
		print(f"total : {total}")
	if "maxResults" in responseJson:
		maxResults = responseJson['maxResults']
		print(f"maxResults: {maxResults}")
	if "issues" in responseJson:
		issuesLength = len(responseJson['issues'])
		print(f"issuesLength: {issuesLength}")	
	else:
		issuesLength = 0		


	if issuesLength > 0:
		for i in range(issuesLength):
			jiraTicketId = responseJson['issues'][i]['key']
			dataId = responseJson['issues'][i]['id']
			updated = responseJson['issues'][i]['fields']['updated']
			creatorName = responseJson['issues'][i]['fields']['creator']['name']
			projectKey = responseJson['issues'][i]['fields']['project']['key']
			projectName = responseJson['issues'][i]['fields']['project']['name']
			issueType = responseJson['issues'][i]['fields']['issuetype']['name']
			print(f"Issue#: {counter}, Id: {dataId}, JiraTicketId: {jiraTicketId}, updated: {updated}, creator: {creatorName}, project: {projectName}, IssueType: {issueType}")
			counter = counter + 1
	else:
		print(responseJson)



print(counter)




# Iterate through the API output and look
# for key 'issues'.
#for key, value in dictProjectIssues.items():

	# Issues fetched, are present as list elements,
	# against the key "issues".
#	if(key == "issues"):

		# Get the total number of issues present
		# for our project.
#		totalIssues = len(value)
#		print(totalIssues)
		# Iterate through each issue,and,
		# extract needed details-Key, Summary,
		# Reporter Name.
#		for eachIssue in range(1):
#			listInner = []

			#print(type(value[eachIssue]))
			# Issues related data,is nested
			# dictionary object.
			#iterateDictIssues(value[eachIssue], listInner)

			# We append, the temporary list fields,
			# to a final list.
			#listAllIssues.append(listInner)
            
		#	print(eachIssue.key)
