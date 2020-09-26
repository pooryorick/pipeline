#! /usr/bin/env python

import ast
import time
import unittest

import os.path
import sys
mydir = os.path.dirname(__file__)
topdir = os.path.dirname(mydir)

if len(sys.path) == 0 or sys.path[0] != topdir:
	sys.path.insert(0,topdir)
from pipeline import pipeline


class Harness1(unittest.TestCase):
	def setUp(self):
		self.unique = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

	def tearDown(self):
		pass


class TestPipeline(Harness1):


	def test_basic(self):
		cmd1 = (sys.executable, '-c' ,'print("hello")')
		p1 = pipeline.pipeline(cmd1)
		outchan = p1.open()
		data = outchan.read()
		p1.close()
		self.assertEqual("hello\n", data)


	def test_humbug:
		cmd1 = ('echo', 'echo', 'hello')
		cmd2 = ('sed', 'sed', 's/hello/humbug/')
		p1 = pipeline.pipeline(cmd1 ,cmd2)
		outchan = p1.open()
		data = outchan.read()
		p1.close()
		self.assertEqual(data, 'humbug')


	def test_pie(self):
		cmds = []
		cmds.append(('echo', 'easy as pie'))
		cmds.append(('awk', '{ print $1, $2, "rhubarb", $3 }'))
		p1 = pipeline.pipeline(*cmds)
		outchan = p1.open()
		data = outchan.read()
		p1.close()
		self.assertEqual(data ,"easy as rhubarb pie\n")


	def test_pipeline(self):
		cmd1 = ('echo', 'batman')
		cmd2 = ('tr', 'a', 'o')
		cmd3 = ('rev')
		p1 = pipeline.pipeline(cmd1, cmd2, cmd3)
		outchan = p1.open()
		data = outchan.read()
		p1.close()
		self.assertEqual("nomtob\n" , data)


	def test_close_active(self):
		cmd1 = (sys.executable, sys.executable, '-c' ,'''
import time
time.sleep(10)
print("hello")
		''')
		p1 = pipeline.pipeline(cmd1)
		outchan = p1.open()
		result = None 
		try:
			p1.close()
		except pipeline.PipelineError as e:
			result = ast.literal_eval(str(e.args[0]))

		self.assertNotEqual(None, result)
		self.assertEqual('process status' ,result['msg'])


	def test_error(self):
		result = None
		try:
			cmd1 = (sys.executable, '-c' ,'raise RuntimeError("some error")')
			p1 = pipeline.pipeline(cmd1)
			results=[]
			results = p1.close()
		except pipeline.PipelineError as e:
			result = ast.literal_eval(str(e.args[0]))

		self.assertNotEqual(None, result)
		self.assertEqual('process status' ,result['msg'])


	def test_badexec(self):
		cmd1 = (self.unique, self.unique)
		failed = 0
		results = [] 
		try:
			p1 = pipeline.pipeline(cmd1)
		except Exception as e:
			results.append('passed')
			return
		self.assertNotEqual(results[0], 'passed')


if __name__ == '__main__':
	unittest.main()
