from biaflowsj.lib import BIAFlows
import unittest, sys, os

class BIAFlowsTest(unittest.TestCase):

	def testConstructorNoArgs(self):
		biaflows = BIAFlows()
		self.assertEquals(biaflows.getHost(), 'https://biaflows.neubias.org')

	def testConstructorWithArgs(self):
		biaflows = BIAFlows('https://url.org', '000', '111')
		self.assertEquals(biaflows.getHost(), 'https://url.org')

	def testDownloadPicture(self):
		if os.path.exists('test.jpg'):
			os.remove('test.jpg')
		biaflows = BIAFlows()
		biaflows.downloadPicture('/api/attachedfile/', '5363317', 'test.jpg')
		fileExists = os.path.exists('test.jpg')
		self.assertEquals(fileExists, True)
		os.remove('test.jpg')

	def testGetHost(self):
		biaflows = BIAFlows()
		self.assertEquals(biaflows.getHost(), 'https://biaflows.neubias.org')

	def testGetInstance(self):
		newInst = BIAFlows.getInstance()
		existingInst = BIAFlows.getInstance()
		self.assertEquals(newInst, existingInst)
		self.assertEquals(existingInst.getHost(), 'https://biaflows.neubias.org')

class ProjectDialogTest(unittest.TestCase):

	def testConstructor(self):
		dialog = ProjectDialog()
		self.assertEquals(dialog.getTitle(), 'BIAFlows')
		dialog.dispose()

	def testGetTitle(self):
		dialog = ProjectDialog(False)
		self.assertEquals(dialog.getTitle(), 'BIAFlows')
		dialog.dispose()

def suite():
	suite = unittest.TestSuite()
	suite.addTest(BIAFlowsTest('testConstructorNoArgs'))
	suite.addTest(BIAFlowsTest('testConstructorWithArgs'))
	suite.addTest(BIAFlowsTest('testDownloadPicture'))
	suite.addTest(BIAFlowsTest('testGetHost'))
	suite.addTest(BIAFlowsTest('testGetInstance'))

	return suite
	
runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
runner.run(suite())
