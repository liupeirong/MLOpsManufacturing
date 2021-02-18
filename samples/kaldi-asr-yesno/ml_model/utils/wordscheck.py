#!/usr/bin/python

import sys

f = open(sys.argv[1])
ls = f.readlines()
f.close()

dic = {}
for i in xrange(len(ls)):
	l = ls[i].strip()
	t = l.split()

	if t[0] in dic:
		ls[i] = '%s%s %s' % (t[0], '$%d' % dic[t[0]], t[1])
		dic[t[0]]+= 1
	else:
		dic[t[0]] = 0


for l in ls:
	print l.strip()
