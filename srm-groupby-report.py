#
# STEP 1 - MAKE SURE TO INSTALL requests
#
import os.path, sys, json, argparse, html, requests
from datetime import datetime, timezone
from collections import defaultdict

#
# STEP 2 - MODIFY THE api_token, api_url and logo_url VARIABLES
#
api_token = os.environ['SRM_API_TOKEN']
#api_token = ""
api_url =  os.environ['SRM_URL']
#api_url = ""
logo_url ="https://www.synopsys.com/content/dam/synopsys/logos/synopsys-logo-color.svg"


# 
# DO NOT MODIFY BELOW AND PROCEED TO STEP 3
#
getprojects = api_url + "srm/api/projects"
findingscount = "findings/count"
projectfields = api_url + "srm/api/project-fields"
projectmetalist=[]
projectdict={}
filterby_list=[]
filterby_dict={}
mymfvalue=''
report_list=[]
report_data=''
report_data2=''
previoud_report_date=''
#
# DEFINE API HEADERS
#
headers = {
"accept": "Content-Type: application/json",
"API-Key": api_token
}
#
# GET PROJECT META FIELDS
#
projectmetadata = requests.get(projectfields, headers=headers) #get project meta data

if projectmetadata.status_code == 200:
	projectmetadata_ds = projectmetadata.json()

	for meta in projectmetadata_ds:
		projectmetalist.append(meta['name'])
		print(meta['name'])

#
# STEP 3 - RUN THIS SCRIPT TO GET FILTER OPTIONS
#

#
# STEP 4 - CHANGE THE VALUE BELOW TO THE DESIRED FILTER
filterby = ''
#

#
# STEP 5 - PUT A COMMENT (NUMBER SIGN) IN FRONT OF the above line of code --> print(meta['name'])
#

#
# STEP 6 - REMOVE THE 3 APOSTROPHES BELOW THIS LINE AND SCROLL TO BOTTOM FOR STEP 7
#
'''


########################################################################################
#
# ONCE SCRIPT IS ACTIVE - DO NOT EDIT BELOW THIS LINE 
#
########################################################################################
# 
#
# [ DEFINITIONS ]
#
#
# GROUP PROJECT IDS BASED ON FILTERBY VARIABLE ASSIGNED ABOVE
def grouped_ids(records):
    grouped_records = {}
    
    for record_id, record in records.items():
        mygroup = record.get(filterby)
        if mygroup:
            if mygroup not in grouped_records:
                grouped_records[mygroup] = []
            grouped_records[mygroup].append(record_id)
    
    return grouped_records
#
# DEDUPE A LIST
def list_dedupe(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list
#
# GET DATES
#
def get_date():
	dt = datetime.now(timezone.utc)
	#tz_dt = dt.astimezone()
	#iso_date = tz_dt.isoformat()
	return dt
#
#
# [ COLLECTING PROJECT DATA ]
#
# CHECK TO SEE IF DATA FILES EXISTS
filterbyjson_path = './'+'filterby_'+filterby.lower().strip().replace(" ", "")+'_dump.json'
filterbyjson_check = os.path.isfile(filterbyjson_path)

# GET PREVIOUS DICTIONARY DATA
if filterbyjson_check == True:
	with open('filterby_'+filterby.lower().strip().replace(" ", "")+'_dump.json', 'r') as fbyjson:
		previous_data = json.load(fbyjson)

# GET PROJECT META API REQUEST
projectmetadata = requests.get(projectfields, headers=headers) #get project meta data

if projectmetadata.status_code == 200:
	projectmetadata_ds = projectmetadata.json()

	for meta in projectmetadata_ds:
		projectmetalist.append(meta['name'])

# GET PROJECTS API REQUEST
projectresponse = requests.get(getprojects, headers=headers) #get project info

# IF SUCCESSFUL CAPTURE PROJECT DATA
if projectresponse.status_code == 200:
	project_api_ds = projectresponse.json()

	# Iterating the elements in list
	for x in project_api_ds['projects']:
		projectID = str(x['id'])
		projectdict[projectID] = {'id': projectID, 'name': x['name']}
		
		#get project details
		projectdetail = requests.get(getprojects+'/'+projectID, headers=headers)
		projectdetail_ds = projectdetail.json()
		projectdict[projectID].update({'hasChildren': projectdetail_ds['hasChildren'], 'parentId': projectdetail_ds['parentId'], 'hierarchyIds': projectdetail_ds['hierarchyIds']})

		#add structure to dictionary
		for mf in list_dedupe(projectmetalist):
			projectdict[projectID].update({mf: None})

		#apply project meta data
		for m in projectdetail_ds['metadata']:
			projectdict[projectID].update({m['name']: m['value']})

		#findings counts
		totalfindings = {"filter": {"~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}
		totalcritical = {"filter": {"severity": "Critical","~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}
		totalhigh = {"filter": {"severity": "High","~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}
		totalmedium = {"filter": {"severity": "Medium","~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}
		totallow = {"filter": {"severity": "Low","~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}
		totalinfo = {"filter": {"severity": "Info","~findingStatus": "gone","~status": ["fixed", "mitigated", "false-positive", "ignored"]}}

		#total					
		findingstotal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totalfindings)
		findingscount_ds = findingstotal.json()
		#critical					
		criticaltotal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totalcritical)
		criticalcount_ds = criticaltotal.json()
		#high					
		hightotal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totalhigh)
		highcount_ds = hightotal.json()
		#medium					
		mediumtotal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totalmedium)
		mediumcount_ds = mediumtotal.json()
		#low					
		lowtotal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totallow)
		lowcount_ds = lowtotal.json()
		#info					
		infototal = requests.post(getprojects+'/'+projectID+'/'+findingscount, headers=headers, json=totalinfo)
		infocount_ds = infototal.json()
								
		projectdict[projectID].update({'totalfindings': findingscount_ds['count'], 'totalcritical': criticalcount_ds['count'], 'totalhigh': highcount_ds['count'], 'totalmedium': mediumcount_ds['count'], 'totallow': lowcount_ds['count'], 'totalinfo': infocount_ds['count']})

# GET FILTERBY LIST OF VALUES
key_grouped_ids = grouped_ids(projectdict)

# CREATE LISTS FROM DICTIONARY VALUES FOR FILTER NAMES
for key, values in key_grouped_ids.items():
	
	# SET FILTERBY SCHEMA
	filterby_dict[key] = {'fb_totalcount': 0, 'raw_totalcount': 0, 'fb_totalfindings': 0, 'raw_totalfindings': 0, 'fb_totalcritical': 0, 'raw_totalcritical': 0, 'fb_totalhigh': 0, 'raw_totalhigh': 0, 'fb_totalmedium': 0, 'raw_totalmedium': 0, 'fb_totallow': 0, 'raw_totallow': 0, 'fb_totalinfo': 0, 'raw_totalinfo': 0, 'fb_timestamp': 0}

	#add structure to dictionary
	for mf in list_dedupe(projectmetalist):
		filterby_dict[key].update({mf: None})

	#OBTAIN KEY SPECIFIC FILTER TOTALS
	fb_totalcount=0
	fb_totalfindings=0
	fb_totalcritical=0
	fb_totalhigh=0
	fb_totalmedium=0
	fb_totallow=0
	fb_totalinfo=0

	for record in values:
		fb_totalcount = fb_totalcount+1
		raw_totalcount = fb_totalcount

		fb_totalfindings = fb_totalfindings + projectdict[record]['totalfindings']
		raw_totalfindings =fb_totalfindings

		fb_totalcritical = fb_totalcritical + projectdict[record]['totalcritical']
		raw_totalcritical = fb_totalcritical

		fb_totalhigh = fb_totalhigh + projectdict[record]['totalhigh']
		raw_totalhigh = fb_totalhigh

		fb_totalmedium = fb_totalmedium + projectdict[record]['totalmedium']
		raw_totalmedium = fb_totalmedium

		fb_totallow = fb_totallow + projectdict[record]['totallow']
		raw_totallow = fb_totallow

		fb_totalinfo = fb_totalinfo + projectdict[record]['totalinfo']
		raw_totalinfo = fb_totalinfo

		#apply project meta data
		for m in list_dedupe(projectmetalist):
			filterby_dict[key].update({m: projectdict[record][m]})
	
	# DOES PREVIOUS DATA EXIST?
	if filterbyjson_check == False:
		previous_report_date = 'that is not found at this time'
		prev_totalcount = 0
		prev_totalfindings = 0
		prev_totalcritical = 0
		prev_totalhigh = 0
		prev_totalmedium = 0
		prev_totallow = 0
		prev_totalinfo = 0
	else:
		previous_report_date = previous_data[key]['fb_timestamp']
		prev_totalcount = int(previous_data[key]['raw_totalcount'])
		prev_totalfindings = int(previous_data[key]['raw_totalfindings'])
		prev_totalcritical = int(previous_data[key]['raw_totalcritical'])
		prev_totalhigh = int(previous_data[key]['raw_totalhigh'])
		prev_totalmedium = int(previous_data[key]['raw_totalmedium'])
		prev_totallow = int(previous_data[key]['raw_totallow'])
		prev_totalinfo = int(previous_data[key]['raw_totalinfo'])

		#apply trend styles for change in total
		
		#totalcount
		if int(fb_totalcount) > int(prev_totalcount):
			fb_totalcount = str(fb_totalcount) + '  <span class=\"red\" alt=\"'+str(prev_totalcount)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalcount) < int(prev_totalcount):
			fb_totalcount = str(fb_totalcount) + ' <span class=\"green\" alt=\"'+str(prev_totalcount)+'\">&#8595;</span>'#findings going down - green

		#totalfindings
		if int(fb_totalfindings) > int(prev_totalfindings):
			fb_totalfindings = str(fb_totalfindings) + '  <span class=\"red\" alt=\"'+str(prev_totalfindings)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalfindings) < int(prev_totalfindings):
			fb_totalfindings = str(fb_totalfindings) + ' <span class=\"green\" alt=\"'+str(prev_totalfindings)+'\">&#8595;</span>'#findings going down - green

		#totalcritical
		if int(fb_totalcritical) > int(prev_totalcritical):
			fb_totalcritical = str(fb_totalcritical) + '  <span class=\"red\" alt=\"'+str(prev_totalcritical)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalcritical) < int(prev_totalcritical):
			fb_totalcritical = str(fb_totalcritical) + ' <span class=\"green\" alt=\"'+str(prev_totalcritical)+'\">&#8595;</span>'#findings going down - green

		#totalhigh
		if int(fb_totalhigh) > int(prev_totalhigh):
			fb_totalhigh = str(fb_totalhigh) + '  <span class=\"red\" alt=\"'+str(prev_totalhigh)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalhigh) < int(prev_totalhigh):
			fb_totalhigh = str(fb_totalhigh) + ' <span class=\"green\" alt=\"'+str(prev_totalhigh)+'\">&#8595;</span>'#findings going down - green

		#totalmedium
		if int(fb_totalmedium) > int(prev_totalmedium):
			fb_totalmedium = str(fb_totalmedium) + ' <span class=\"red\" alt=\"'+str(prev_totalmedium)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalmedium) < int(prev_totalmedium):
			fb_totalmedium = str(fb_totalmedium) + ' <span class=\"green\" alt=\"'+str(prev_totalmedium)+'\">&#8595;</span>'#findings going down - green

		#totallow
		if int(fb_totallow) > int(prev_totallow):
			fb_totallow = str(fb_totallow) + ' <span class=\"red\" alt=\"'+str(prev_totallow)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totallow) < int(prev_totallow):
			fb_totallow = str(fb_totallow) + ' <span class=\"green\" alt=\"'+str(prev_totallow)+'\">&#8595;</span>'#findings going down - green

		#totalinfo
		if int(fb_totalinfo) > int(prev_totalinfo):
			fb_totalinfo = str(fb_totalinfo) + ' <span class=\"red\" alt=\"'+str(prev_totalinfo)+'\">&#8593;</span>'#findings going down - red
		elif int(fb_totalinfo) < int(prev_totalinfo):
			fb_totalinfo = str(fb_totalinfo) + ' <span class=\"green\" alt=\"'+str(prev_totalinfo)+'\">&#8595;</span>'#findings going down - green


	# SET TOTALS
	filterby_dict[key].update({'fb_totalcount': fb_totalcount, 'raw_totalcount': raw_totalcount, 'fb_totalfindings': fb_totalfindings, 'raw_totalfindings': raw_totalfindings, 'fb_totalcritical': fb_totalcritical, 'raw_totalcritical': raw_totalcritical, 'fb_totalhigh': fb_totalhigh, 'raw_totalhigh': raw_totalhigh, 'fb_totalmedium': fb_totalmedium, 'raw_totalmedium': raw_totalmedium, 'fb_totallow': fb_totallow, 'raw_totallow': raw_totallow, 'raw_totalinfo': raw_totalinfo, 'fb_totalinfo': fb_totalinfo, 'fb_timestamp': str(get_date()) })

	# ADD TO LIST AFTER FILTERS FOR REPORT
	report_list.insert(len(projectmetalist)+1, fb_totalcount)
	report_list.insert(len(projectmetalist)+2, fb_totalfindings)
	report_list.insert(len(projectmetalist)+3, fb_totalcritical)
	report_list.insert(len(projectmetalist)+4, fb_totalhigh)
	report_list.insert(len(projectmetalist)+5, fb_totalmedium)
	report_list.insert(len(projectmetalist)+6, fb_totallow)
	report_list.insert(len(projectmetalist)+7, fb_totalinfo)

# REMOVE COMMENT TO GET PROJECT & FILTERBY DATA DICTIONARY
#print(projectdict)
#print(filterby_dict)
########################################################################################
########################################################################################
# CREATE REPORT DATA
#
filterby_len = len(filterby_dict)
for row in filterby_dict:
	report_data2=""
	#add structure to dictionary
	for mf in list_dedupe(projectmetalist):
		report_data2 += '\''+ str(filterby_dict[row][mf]) +'\', '
		#report_list.insert(0, str(filterby_dict[row][mf]))
	report_data += '[' + report_data2 + '\'' +str(filterby_dict[row]['fb_totalcount'])+'\', \''+str(filterby_dict[row]['fb_totalfindings'])+'\', \''+str(filterby_dict[row]['fb_totalcritical'])+'\', \''+str(filterby_dict[row]['fb_totalhigh'])+'\', \''+str(filterby_dict[row]['fb_totalmedium'])+'\', \''+str(filterby_dict[row]['fb_totallow'])+'\', \''+str(filterby_dict[row]['fb_totalinfo']) +'\'],' 
#
#
with open('filterby_'+filterby.lower().strip().replace(" ", "")+'_dump.json', 'w') as fp:
    json.dump(filterby_dict, fp)

# HTML REPORT
#
my_mflist = list_dedupe(projectmetalist)
for a in my_mflist:
  mymfvalue += 'data.addColumn(\'string\', \''+a+'\');'+'\n'

def writeHTML():
	try:
		#createJSprojectcharts()
		reportname = 'srm_'+filterby.lower().strip().replace(" ", "")+'_report.html'
		f = open(reportname, "w")
		html1 = """<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        """+str(mymfvalue)+"""
        data.addColumn('string', '# of Projects');
        data.addColumn('string', '# of Findings');
        data.addColumn('string', '# of Critical');
        data.addColumn('string', '# of High');
        data.addColumn('string', '# of Medium');
        data.addColumn('string', '# of Low');
        data.addColumn('string', '# of Info');
        data.addRows([
          """+str(report_data[:-1])+"""
        ]);

        var table = new google.visualization.Table(document.getElementById('table_div'));
		table.draw(data, {allowHtml: true, showRowNumber: false, width: '100%'});
      }
    </script>
    <style type="text/css">body,html{font-family:Arial,Helvetica,sans-serif}h2{font-size:1.5em;text-align:center}h3{font-size:1.2em;text-align:center}h2{margin-bottom:5px}h2+h3{margin-top:0}.header{height:100px}button{border:none}.logo{width:300px;float:left; margin-bottom: 50px;}.report{color:rgba(90,42,130,.5);font-size:.8em;text-align:right}.report strong{font-size:1.1em}.purple{background-color:#80539c}.lite-purple h2,.purple h2{color:#fff}.lite-purple{background-color:#5a2a82}.left,.left h2,.left p{text-align:left}.right,.right h2,.right p{text-align:right}.center,.center h2,.center p{text-align:center}.column{float:left}.column a{color:#000}.column h5{margin:5% auto;text-align:center;font-weight:700;font-size:6.5em}.column h6{margin:0 auto;text-align:center;font-variant:small-caps}.middle.column h6{margin:0 auto;text-align:center;font-variant:small-caps;line-height:1.2;font-family:monospace;font-size:1.25em;text-align:center;margin-left:5px}.column p{margin-block-start:.1em;font-size:.75em;font-family:monospace}.row:after{content:"";display:table;clear:both}h2{color:#5a2a82}#wrapper{width:100%;position:absolute}#container{max-width:1200px;min-height:1200px;margin:0 auto}.row{width:100%;display:block;min-width:1200px;max-width:1200px}.info p{font-size:1.5em;line-height:2}.info h2,.info h3{padding:1px;margin:8px 0 0 0;line-height:1}.info h3{font-size:.9em}div.space{padding-top:75px;padding-bottom:50px}.w200{width:200px;height:200px;min-width:200px;min-height:200px}.w300{width:300px;height:300px;min-width:300px;min-height:300px}.w400{width:400px;height:300px;min-width:400px;min-height:300px}.w500{width:500px;height:300px;min-width:500px;min-height:300px}.w600{width:600px;height:300px;min-width:600px;min-height:300px}em{border-bottom:solid 3px red}.borders{border-top:solid 1px #ddd;}.projects div{max-height:125px;min-height:125px}.projects div h4{text-align:125px}.padtop35 h2{padding-top:35px}.info table{width:100%;margin:5%;border:0;padding-top:10px}.info td{border-bottom-style:dashed;border-bottom-color:#ccc;border-bottom-width:1px;line-height:40px}.info td:nth-child(2){text-align:right}div.projects{padding-top:25px}.projects table{width:100%;margin:5px}.projects tr:nth-child(even) td{border-bottom:dashed 1px #ccc}.projects td{width:20%;text-align:center}.projects h2{margin:20px}.projects h4{text-align:left;margin:10px 5px;font-family:monospace}.projects h5{font-size:5em;margin:0;padding:0}div[id^=project_]{display:inline-block;margin:0 auto!important}body,html{background-color:#fff}.google-visualization-table-td{text-align: center;padding-top:5px; padding-bottom:5px;}span.red{color: red;font-family: monospace;font-weight: bolder;font-size: 120%;}span.green{color: green;font-family: monospace;font-weight: bolder;font-size: 120%;}tr.google-visualization-table-tr-head{background-color:#5a2a8263;}p.footer {text-align: center;font-family: monospace;font-size: .8em;padding: 20px;}</style>
  </head>
  <body>
  	<div id="wrapper">
		<div id="container">
			<div class="row header">
				<div class="logo">
			    	<img src=\""""+str(logo_url)+"""\" alt="Home" width="250">
			    </div>
			    <div class="report"><strong>APPLICATION FINDINGS REPORT</strong><br />GENERATED ON """+str(get_date())+"""</div>
			</div>
			<div class="row">
				<div class="full-width"></div>
			</div>
    		<div id="table_div"></div>
			<div class="row">
				<div class="full-width"><p class="footer">Results displayed above have been grouped by """+str(filterby)+""" and compared to a previous report """+str(previous_report_date)+""".</p></div>
			</div>    		
    	</div>
    </div>
  </body>
</html>"""
		f.write(html1)
		f.close()
		print('Completed writing report!')
	except:
		print("Error creating html report (see writeHTML)")


writeHTML()
########################################################################################
#
# STEP 7 - REMOVE THE 3 APOSTROPHES BELOW THIS LINE
#
'''
