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
	.hidden
	{
		display: none;
	}
	.extra
	{
		border: 1px solid black;
		background: #eee;
	}
	</style>
	<script language="javascript">
function toggle( id )
{
	var node = document.getElementById( "secondary_" + id );
	if(node.className == "hidden" )
	{
		node.className = "";
		document.getElementById("button_" + id).innerHTML = "-";
	}
	else
	{
		node.className = "hidden";
		document.getElementById("button_" + id).innerHTML = "+";
	}
}

	</script>

</head>
<body>
JobBank query generated ${date} from query
<code>${query}</code>

${len(results)} results out of ${nJobs} jobs total.
<table>
<tr><th></th><th>ID</th><th>Description</th><th>Salary</th><th>Hours</th></tr>
%for result in sorted( results, key=lambda x: x['hoursperweek']):
	<tr id="main_${result['id']}">
	<td><b id="button_${result['id']}" onclick="toggle(${result['id']});">+</b></td>
	<td><a href="http://www.jobbank.gc.ca/detail-eng.aspx?OrderNum=${result['id']}&Source=JobPosting">${result['id']}</a></td>
	<td>${result['title']}</td>
	<td>$${'%.2f' % result['salary-low']}</td>
	<td>${result['hoursperweek']}</td>
	
	</tr>
	<tr id="secondary_${result['id']}" class="hidden">
	<td colspan="5">
		<div class="extra">${result['salary']}</div>
		<div class="extra">Expires: ${result['expires']}</div>
		<div class="extra">Added: ${result['added']}</div>
		<div class='extra'>Requirements:
		<table>
			%for reqname, reqdesc in result['requirements'].items():
			<tr><td>${reqname}</td><td>${reqdesc}</td></tr>
			%endfor
		</table>
	</td>
	</tr>
%endfor
</table>
</body>
</html>