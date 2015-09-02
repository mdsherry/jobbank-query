import re
import operator
from ply import lex, yacc
import datetime

def PAnd( p1, p2 ):
	return lambda x: p1(x) and p2(x)

def POr( p1, p2 ):
	return lambda x: p1(x) or p2(x)

def PNot( p1 ):
	return lambda x: not p1(x)

def predOnFields( field, entry, pred ):
	for i,subfield in enumerate(field):
		if subfield == '*':
			for key in entry:
				if predOnFields( field[i+1:], entry[key], pred ):
					return True
			return False
		subfield = subfield.lower()
		if subfield in entry:
			entry = entry[subfield]
		else:
			return False

	return pred( entry )

def toUpper(l):
	return [el.upper() for el in l if hasattr( el, 'upper')	]

def PContains( field, string ):
	def pred( entry ):
		if type( entry ) == list:
			return string.upper() in toUpper( entry )
		elif hasattr( entry, 'upper' ):
			return string.upper() in entry.upper()
		return False
	
	return lambda entry: predOnFields( field, entry, pred )


def PMatches( field, pattern ):
	pattern = re.compile( pattern[1:-1].replace(r'\/','/'), re.IGNORECASE )
	
	def pred( entry ):
		if pattern.search( str(entry) ):
			return True
		return False
	
	return lambda entry: predOnFields( field, entry, pred )
	

def PCompare( field, value, op ):
	value = float( value )
	def pred( entry ):
		return op( float( entry ), value )
	return lambda entry: predOnFields( field, entry, pred )

def PCompareDate( field, value, op ):
	def pred( entry ):
		try:
			return op( entry, value )
		except TypeError:
			return False
	return lambda entry: predOnFields( field, entry, pred )


reserved = {
	'and': 'AND',
	'or': 'OR',
	'not': 'NOT',
	'contain': 'CONTAIN',
	'contains': 'CONTAIN',
	'before': 'BEFORE',
	'after': 'AFTER',
	'match': 'MATCH',
	'matches': 'MATCH'
}

def uniq( l ):
	result = []
	last = None
	for el in sorted( l ):
		if el != last:
			result.append( el )
			last = el
	return result

tokens = [ 'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'DOESNT',
	'LT', 'GT', 'LTE', 'GTE', 'EQ','NE', 'NUMBER', 'DATE',
	'NAME', 'QUADPUNKT', 'STRING', 'PATTERN'] + uniq( list(reserved.values()) )


t_LBRACE = r'\['
t_RBRACE = r']'
t_QUADPUNKT = '::'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PATTERN = r'/(\\/|[^/])*/'
t_LT = '<'
t_LTE = '<='
t_GT = '>'
t_GTE = '>='
t_EQ = '='
t_NE = '!='
t_NUMBER = r'\d+(\.\d+)?'

def t_DATE(t):
	"""today|yesterday|\d+\s+(day|month|week)s?\s+ago|next\s+(month|week)|\d{4}/\d{2}/\d{2}"""
	now = datetime.date.today()
	if t.value.lower() == "today":
		t.value = now
	elif 'next' in t.value.lower():
		if 'week' in t.value.lower():
			t.value = now + datetime.timedelta( days = 7 - now.weekday() )
		elif 'month' in t.value.lower():
			t.value = now + datetime.timedelta( days = 32 - now.day )
			t.value += datetime.timedelta( days= 1 - t.value.day )
	elif 'ago' in t.value.lower():
		matches = re.match('(\d+)\s+(day|month|week)s?\s+ago', t.value.lower())
		n = int( matches.group(1) )
		unit = matches.group(2).lower()
		# These don't really match the same semantics as 'next FOO'.
		# TODO: Decide on one set of semantics and modify the other to match.
		if unit == 'day':
			t.value = now + datetime.timedelta( days=-1 )
		elif unit == 'week':
			t.value = now + datetime.timedelta( days=-7 )
		elif unit == 'month':
			t.value = now + datetime.timedelta( days=-31 )
	else:
		t.value = datetime.date.strptime( t.value, "%Y/%m/%d")
	t.value = datetime.datetime.combine( t.value, datetime.datetime.min.time() )
	return t

def t_DOESNT(t):
	"""DOESN'T"""
	t.type = 'DOESNT'
	return t

def t_STRING(t):
	""""([^"]|\\\\")*"|'([^']|\\\\')*'"""
	quote = t.value[0]
	t.value = t.value[1:-1]
	t.value = t.value.replace("\\" + quote, quote)
	return t

def t_NAME(t):
	r"\*|[a-zA-Z_]\w*(-\w+)?"
	if t.value.lower() in reserved.keys():
		t.type = reserved[t.value.lower()]
	return t

t_ignore = " \t\n"
def t_error(t):
	print ("Illegal character '{}'".format( t.value[0] ))
	t.lexer.skip(1)

precedence = (
	('left', 'OR'),
	('left', 'AND'),
	('right', 'NOT')
)

def p_query_paren(p):
	"""query : LPAREN query RPAREN"""
	p[0] = p[2]

def p_query_binop(p):
	"""query : query AND query
	         | query OR query"""
	if p[2].upper() == 'AND':
		p[0] = PAnd( p[1], p[3] )
	else:
		p[0] = POr( p[1], p[3] )

def p_query_not(p):
	"""query : NOT query"""
	p[0] = PNot( p[2] )

def p_query_condition(p):
	"""query : condition"""
	p[0] = p[1]


def p_condition_matches(p):
	"""condition : field MATCH PATTERN"""
	p[0] = PMatches( p[1], p[3] )
	
def p_condition_doesntmatch(p):
	"""condition : field DOESNT MATCH PATTERN"""
	p[0] = PNot( PMatches( p[1], p[3] ) )
	


def p_condition_contains(p):
	"""condition : field CONTAIN STRING"""
	p[0] = PContains( p[1], p[3] )

def p_condition_doesntcontain(p):
	"""condition : field DOESNT CONTAIN STRING"""

	p[0] = PNot( PContains( p[1], p[4] ) )

def p_condition_numcompare( p ):
	"""condition : field GT NUMBER
	             | field GTE NUMBER
	             | field LT NUMBER
	             | field LTE NUMBER
	             | field EQ NUMBER
	             | field NE NUMBER
	"""
	p[0] = PCompare( p[1], p[3], {
		'=': operator.eq, 
		'!=': operator.ne, 
		'<': operator.lt,
		'>': operator.gt,
		'<=': operator.le,
		'>=': operator.ge }[p[2]])

def p_condition_datecompare( p ):
	"""condition : field BEFORE DATE
	             | field AFTER DATE
	"""
	p[0] = p[0] = PCompareDate( p[1], p[3], operator.le if p[2].lower() == 'before' else operator.ge )

def p_field_base(p):
	"""field : LBRACE NAME optnames RBRACE"""
	p[0] = [p[2]] + p[3]

def p_optnames(p):
	"""optnames : QUADPUNKT NAME optnames
				| 
	"""
	if len(p) > 1:
		p[0] = [p[2]] + p[3]
	else:
		p[0] = []

lex.lex(reflags=re.IGNORECASE)
parser = yacc.yacc()

def parse(s):
	return parser.parse( s, debug=0 )

def main():
	print (parse("[Salary] contains 'hourly'"))

if __name__ == '__main__':
	main()