Once upon a time, this set of scripts would help query http://jobbank.gc.ca, and allow more 
complex queries to be performed. For instance, you could search for jobs based on expected
salary, location, NOC, term of employment, and do keyword filtering on some or all fields.

One friend credits it for helping her find a job, by reducing the number of prospects she had to consider.

---

Unfortunately, jobbank.gc.ca changed their site, and I haven't had reason to revisit this program.

---

The query language is very simple: predicates joined by *and* and *or*, with *not* for negation, and parentheses for setting precedence. Fields are [bracketed], with subfield names identified as [parentfield::subfield]. Field names are all lower case, and match the field in the table on the website, minus spaces and other punctuation.

Numerical comparison operators (<, >, =) all work. *contains*/*doesn't contain* performs basic substring matching with strings marked by single quotes ('), while *matches*/*doesn't match* use (Python) regular expressions delimited by slashes (/).

See query.txt for a sample query.