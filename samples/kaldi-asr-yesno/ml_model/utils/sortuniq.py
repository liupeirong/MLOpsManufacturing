#!/usr/bin/python

import sys


lst = {}

for l in sys.stdin:
	l = l.strip()
	lst[l] = 0


lstk = list(lst.keys())

lstk.sort()

for item in lstk:
	print (item)

