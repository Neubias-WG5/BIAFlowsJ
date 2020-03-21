from biaflowsj.gui import ProjectDialog
import unittest, sys


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
	suite.addTest(ProjectDialogTest('testConstructor'))
	suite.addTest(ProjectDialogTest('testGetTitle'))
	
	return suite
	
runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
runner.run(suite())