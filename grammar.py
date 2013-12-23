import re
from ply import lex, yacc

def PAnd( p1, p2 ):
	return lambda x: p1(x) and p2(x)

def POr( p1, p2 ):
	return lambda x: p1(x) or p2(x)

def PNot( p1 ):
	return lambda x: not p1(x)

def PContains( field, string ):
	def contains( field, x ):
		entry = x

		for i,subfield in enumerate(field):
			if subfield == '*':
				for key in entry:
					if contains( field[i+1:], entry[key] ):
						return True
				return False
			subfield = subfield.lower()
			if subfield in entry:
				entry = entry[subfield]
			else:
				return False

		if hasattr( entry, 'upper' ):
			return string.upper() in entry.upper()
		return False
	def wrap( x ):
		return contains( field, x )
	return wrap


def PMatches( field, pattern ):
	pattern = re.compile( pattern[1:-1] )
	def contains( field, x ):
		entry = x

		for i,subfield in enumerate(field):
			if subfield == '*':
				for key in entry:
					if contains( field[i+1:], entry[key] ):
						return True
				return False
			subfield = subfield.lower()
			if subfield in entry:
				entry = entry[subfield]
			else:
				return False

		if hasattr( entry, 'upper' ):
			if pattern.match( entry, re.IGNORECASE ):
				return True
		return False
	def wrap( x ):
		return contains( field, x )
	return wrap



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
	'LT', 'GT', 'LTE', 'GTE', 'EQ','NE', 'NUMBER', 
	'NAME', 'QUADPUNKT', 'STRING', 'PATTERN'] + uniq( list(reserved.values()) )


t_LBRACE = r'\['
t_RBRACE = r']'
t_QUADPUNKT = '::'
t_LPAREN = r'\('
t_RPAREN = r'\('
t_PATTERN = r'/[^/]*/'
t_LT = '<'
t_LTE = '<='
t_GT = '>'
t_GTE = '>='
t_EQ = '='
t_NE = '!='
t_NUMBER = r'\d+(\.\d+)?'

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
	r"\*|\w+"
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
	print( p[0] )

def p_condition_contains(p):
	"""condition : field CONTAIN STRING"""
	p[0] = PContains( p[1], p[3] )

def p_condition_doesntcontain(p):
	"""condition : field DOESNT CONTAIN STRING"""

	p[0] = PNot( PContains( p[1], p[4] ) )

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