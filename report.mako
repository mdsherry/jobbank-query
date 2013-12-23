<html>
<head>
	<title>JobBank report</title>
	<style>
	code { 
		display:block; 
		margin: 1em; 
		padding: 1em; 
		border: 1px dashed #000; 
		background: #eee;
	}
	</style>
</head>
<body>
JobBank query generated ${date} from query
<code>${query}</code>

${len(results)} results out of ${nJobs} jobs total.
<table>
<tr><th>ID</th><th>Description</th><th>Salary</th></tr>
%for result in results:
	<tr>
	<td><a href="http://www.jobbank.gc.ca/detail-eng.aspx?OrderNum=${result['id']}&Source=JobPosting">${result['id']}</a></td>
	<td>${result['title']}</td>
	<td>${result['startdate']}</td>
	
	</tr>
%endfor
</table>
</body>
</html>