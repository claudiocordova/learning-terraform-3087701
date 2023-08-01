
https://stackoverflow.com/questions/6323860/sibling-package-imports


===================================================================




Whenever you change Poetry related stuff in your pyproject.toml run:
 
 poetry lock --no-update 
 
 afterwards to sync the poetry.lock files with those changes. The --no-update flag tries to preserve existing versions of dependencies. Once the lock file is updated run poetry install to sync your venv with the locked dependencies.

Wherever possible you should prefer using Poetry's cli instead of manually edit the pyproject.toml. Poetry will take care of the steps described above for you. So if you run poetry add <somedep>, Poetry will add the entry to your pyproject.toml, update the poetry.lock and will install necessary dependencies.



===================================================================


SELECT s.* FROM 
servicerun s
JOIN servicerunindexserviceid i on s.servicerunid = i.servicerunid 
where 
--and s.trackingactivityid = 'MAPBUILD-1234'
i.serviceid = 'SERVICE_ID_1'



Athena also supports dynamic filtering and dynamic partition pruning, which improves the query runtime and reduces data scanned for queries with joins and a very selective filter clause for the table on the right side of join, as shown in the following example. In the following query, Table_B is a small table with a very selective filter (column_A = “value”). After the selective filter is applied to Table_B, a value list for a joined column Table_B.date is extracted first, and it’s pushed down to a joined table Table_A as a filter. It’s used to filter out unnecessary rows and partitions of Table_A. This results in reading fewer rows and partitions from the source for Table_A and helps reduce query runtime and data scan size, which in turn helps reduce the costs of running the query in Athena.

SELECT count(*)
FROM Table_A
    JOIN Table_B ON Table_A.date = Table_B.date
WHERE Table_B.column_A = "value"





======================================================================



https://github.com/PredictMobile/aws-sso-credentials-getter/

npm install -g aws-sso-credentials-getter

#creates temp creds in .aws/credentials
ssocred motional-mapping


===========================================================================================================


https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125
1:28
https://jira.ci.motional.com/atljira/rest/api/2/field
1:29
https://jira.ci.motional.com/atljira/rest/api/2/issuetype
1:29
https://jira.ci.motional.com/atljira/rest/api/2/search?jql=project=MAPBUILD


#curl --request GET \
#--url 'https://<SITE_NAME>.atlassian.net/rest/api/3/issue/<ISSUE_KEY>' \
#--user '<EMAIL>:<API_TOKEN>' \
#--header 'Accept: application/json' \
#--header 'Content-Type: application/json'


#basic authorization: fail
curl -v https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125 --user 'claudio.cordova@motional.com:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl'
curl -v https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125 --user 'claudio.cordova:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl'



curl -D- -u 'claudio.cordova@motional.com:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl' -X GET -H "Content-Type: application/json" https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125
curl -D- -u 'claudio.cordova:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl' -X GET -H "Content-Type: application/json" https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125
curl -D- -u "claudio.cordova@motional.com:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl" -X GET -H "Content-Type: application/json" https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125
curl -D- -u "claudio.cordova:NTY4OTkxODk3MDY2OrAHFEv/k67o6Zu09ZfMLPjfHHEl" -X GET -H "Content-Type: application/json" https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125



MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d

curl -D- -u 'claudio.cordova@motional.com:MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d' -X GET -H "Content-Type: application/json" https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125

echo -n claudio.cordova@motional.com:MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d | base64
Y2xhdWRpby5jb3Jkb3ZhQG1vdGlvbmFsLmNvbTpNelExTlRFeE9UazRNRE0zT3UzVm54ZnQvVHBzdXpMc1J4MHI5ZjVUME42ZA==


curl -D- -X GET -H "Authorization: Basic Y2xhdWRpby5jb3Jkb3ZhQG1vdGlvbmFsLmNvbTpNelExTlRFeE9UazRNRE0zT3UzVm54ZnQvVHBzdXpMc1J4MHI5ZjVUME42ZA==" -H "Content-Type: application/json" "https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125"


MB-F142VCQ3L6:jira-client claudio.cordova$ echo -n claudio.cordova:MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d | base64
Y2xhdWRpby5jb3Jkb3ZhOk16UTFOVEV4T1RrNE1ETTNPdTNWbnhmdC9UcHN1ekxzUngwcjlmNVQwTjZk


curl -D- -X GET -H "Authorization: Basic Y2xhdWRpby5jb3Jkb3ZhOk16UTFOVEV4T1RrNE1ETTNPdTNWbnhmdC9UcHN1ekxzUngwcjlmNVQwTjZk" -H "Content-Type: application/json" "https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125"


#Works!
curl -H "Authorization: Bearer MzQ1NTExOTk4MDM3Ou3Vnxft/TpsuzLsRx0r9f5T0N6d" "https://jira.ci.motional.com/atljira/rest/api/2/issue/MAP-2125"