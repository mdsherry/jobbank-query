<html>
<head>
	<title>JobBank report</title>
</head>
<body>
JobBank query generated ${date} from query
<code><pre>${query}</pre></code>
<table>
<tr><th>ID</th><th>Description</th><th>Salary</th></tr>
%for result in results:
	<tr>
	<td><a href="http://www.jobbank.gc.ca/detail-eng.aspx?OrderNum=${result['id']}&Source=JobPosting">${result['id']}</a></td>
	<td>${result['title']}</td>
	<td>${result['salary']}</td>
	<td>$${"%0.2f" % result['salary-low']}</td><td>$${"%0.2f" % result['salary-high']}</td>
	</tr>
%endfor
</table>
</body>
</html>