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


def run(*args):
	p1 = pipeline.pipeline(*args)
	outchan = p1.open()
	data = outchan.read()
	p1.close()
	return data


class TestPipeline(Harness1):


	def test_basic(self):
		cmd1 = (sys.executable, '-c' ,'print("hello")')
		data = run(cmd1)
		self.assertEqual("hello\n", data)


	def test_humbug(self):
		cmd1 = ('echo', 'hello')
		cmd2 = ('sed', 's/hello/humbug/')
		data = run(cmd1 ,cmd2)
		self.assertEqual(data, 'humbug\n')


	def test_greenbeans(self):
		cmd1 = ('echo', 'green beans')
		cmd2 = ('awk' , '/beans/{ print $1 }')
		cmd3 = ('rev' ,)
		cmd4 = ('bash', '-c', 'read; echo $REPLY $REPLY')
		data = run(cmd1, cmd2, cmd3, cmd4)
		self.assertEqual(data ,'neerg neerg\n')


	def test_test1(self):
		p1 = pipeline.pipeline(
			('yes', 'easy as py'),
			('cat'),
			('tr', 'a', 'A'),
			('tr', 'g', 'G'),
			('awk', '{ print $0 }'),
			('sed', 's/pipe/PIPE/g'),
			('sed', 's/import/IMPORT/g'),
		)
		chan = p1.open()
		data1 = chan.read(3)
		data2 = chan.read(3)
		p1.terminate()
		self.assertEqual(data1, 'eAs')
		self.assertEqual(data2, 'y A')


	def test_pie(self):
		cmds = []
		cmds.append(('echo', 'easy as pie'))
		cmds.append(('awk', '{ print $1, $2, "rhubarb", $3 }'))
		data = run(*cmds)
		self.assertEqual(data ,"easy as rhubarb pie\n")


	def test_pipeline(self):
		cmd1 = ('echo', 'batman')
		cmd2 = ('tr', 'a', 'o')
		cmd3 = ('rev')
		data = run(cmd1, cmd2, cmd3)
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
