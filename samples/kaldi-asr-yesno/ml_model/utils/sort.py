#!/usr/bin/python

import sys

lst = sys.stdin.readlines()

lst.sort()

for item in lst:
	print (item[:-1])

