from biaflowsj.lib import BIAFlows, Projects, Storages, Uploader
from ij import IJ
import unittest, sys, os
from shutil import copy2
from be.cytomine.client.collections import StorageCollection, ImageInstanceCollection
from be.cytomine.client.models import Project, Ontology

class BIAFlowsTest(unittest.TestCase):

	def setUp(self):
		 BIAFlows()
	
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

	def testSetHost(self):
		biaflows = BIAFlows()
		biaflows.setHost("a.b.c")
		self.assertEquals(biaflows.getHost(), 'a.b.c')

	def testGetPublicKey(self):
		self.assertEquals(BIAFlows.getInstance().getPublicKey(), 'c0f3be78-a1a7-4d86-ad09-9e1753f26a8b')

	def testSetPublicKey(self):
		biaflows = BIAFlows.getInstance()
		biaflows.setPublicKey("k1k1k1");
		self.assertEquals(BIAFlows.getInstance().getPublicKey(), 'k1k1k1')

	def testGetPrivateKey(self):
		self.assertEquals(BIAFlows.getInstance().getPrivateKey(), '73b7df42-3484-4c1b-9bf2-8d9e3ea53eac')

	def testSetPrivateKey(self):
		biaflows = BIAFlows.getInstance()
		biaflows.setPrivateKey("k2k2k2");
		self.assertEquals(BIAFlows.getInstance().getPrivateKey(), 'k2k2k2')

	def testGetUploadURL(self):
		biaflows = BIAFlows.getInstance()
		url = biaflows.getUploadURL()
		self.assertEquals(url.find('-upload')>=0, True)
	
	def testGetInstance(self):
		newInst = BIAFlows.getInstance()
		existingInst = BIAFlows.getInstance()
		self.assertEquals(newInst, existingInst)
		self.assertEquals(existingInst.getHost(), 'https://biaflows.neubias.org')


class ProjectsTest(unittest.TestCase):

	def setUp(self):
		 BIAFlows()

	def testConstructor(self):
		projects = Projects()
		self.assertEquals(len(projects.getNames())>0, True)
		self.assertEquals(len(projects.getIDs()), len(projects.getNames()))

	def testUpdateFromServer(self):
		projects = Projects()
		projects.updateFromServer()
		self.assertEquals(len(projects.getNames())>0, True)
		self.assertEquals(len(projects.getIDs()), len(projects.getNames()))

	def testGetNames(self):
		projects = Projects()
		names = projects.getNames()
		self.assertEquals(len(names)>0, True)
		self.assertEquals(isinstance(names[0], basestring), True)

	def testGetIDs(self):
		projects = Projects()
		ids = projects.getIDs()
		self.assertEquals(len(ids)>0, True)
		self.assertEquals(isinstance(ids[0], long), True)

class StoragesTest(unittest.TestCase):

	def setUp(self):
		 BIAFlows()

	def testConstructor(self):
		storages = Storages()
		self.assertEquals(len(storages.getNames())>0, True)
		self.assertEquals(len(storages.getIDs()), len(storages.getNames()))

	def testUpdateFromServer(self):
		storages = Storages()
		storages.updateFromServer()
		self.assertEquals(len(storages.getNames())>0, True)
		self.assertEquals(len(storages.getIDs()), len(storages.getNames()))

	def testGetNames(self):
		storages = Storages()
		names = storages.getNames()
		self.assertEquals(len(names)>0, True)
		self.assertEquals(isinstance(names[0], basestring), True)

	def testGetIDs(self):
		storages = Storages()
		ids = storages.getIDs()
		self.assertEquals(len(ids)>0, True)
		self.assertEquals(isinstance(ids[0], long), True)

class UploaderTest(unittest.TestCase):

	def setUp(self):
		biaflows = BIAFlows('http://biaflows/', '7fe8b526-93ae-481e-932d-e1e0bb598529', '45953ccd-0984-4471-ba68-31c6d212699a')
		IJ.newImage("Ramp", "8-bit ramp", 256, 256, 1)
		imp = IJ.getImage()
		IJ.saveAs("tiff", "./ctest.tif")
		imp.close()

		projects = Projects()
		names = projects.getNames()
		ids = projects.getIDs()
		index = -1
		pid = -1
		try:
			index = names.index('upload-test')
			pid = ids[index]
		except ValueError, e:
			p = Project(name, Ontology('upload-test')).save()
			pid = p.getId()
		self.projectID = pid
		
		storages = StorageCollection().fetch()
		sid = storages.get(0).get('id')
		self.storageID = sid

		p = Project().fetch(pid);
		images = ImageInstanceCollection.fetchByProject(p)
		for i in range(0, images.size()):
			image = images.get(i)
			image.delete()
				
	def testConvertImageToOME(self):
		uploader = Uploader()
		uploader.convertImageToOME('./ctest.tif', './tmp/')
		fileExists = os.path.isfile('./tmp/ctest.ome.tif')
		self.assertEquals(fileExists, True)
		os.remove('./tmp/ctest.ome.tif')

	def testConvertImagesInFolderToOME(self):
		if not os.path.isdir('./convert_tmp'): 
			os.mkdir('./convert_tmp')
		copy2('./ctest.tif', './convert_tmp/ctest1.tif')
		copy2('./ctest.tif', './convert_tmp/ctest2.tif')
		uploader = Uploader()
		uploader.convertImagesInFolderToOME('./convert_tmp/', './convert_tmp/out/')
		file1Exists = os.path.isfile('./convert_tmp/out/ctest1.ome.tif')
		file2Exists = os.path.isfile('./convert_tmp/out/ctest2.ome.tif')
		self.assertEquals(file1Exists, True)
		self.assertEquals(file2Exists, True)
		os.remove('./convert_tmp/out/ctest1.ome.tif')
		os.remove('./convert_tmp/out/ctest2.ome.tif')

	def testUploadImage(self):
		uploader = Uploader()
		code, obj = uploader.uploadImage("./ctest.tif", str(self.projectID), str(self.storageID))
		self.assertEquals(code, 200)

	def testUploadImagesInFolder(self):
		uploader = Uploader()
		if not os.path.isdir('./upload_tmp'):
			os.mkdir('./upload_tmp')
		copy2('./ctest.tif', './upload_tmp/ctest1.tif')
		copy2('./ctest.tif', './upload_tmp/ctest2.tif')
		uploader.convertImagesInFolderToOME('./upload_tmp/', './upload_tmp/out/')
		nrOfUploadedImages = uploader.uploadImagesInFolder('./upload_tmp/out/', str(self.projectID), str(self.storageID))
		self.assertEquals(nrOfUploadedImages, 2)

	def testGetObservers(self):
		uploader = Uploader()
		observers = uploader.getObservers()
		self.assertEquals(len(observers), 0)
	
def suite():
	suite = unittest.TestSuite()
	suite.addTest(BIAFlowsTest('testConstructorNoArgs'))
	suite.addTest(BIAFlowsTest('testConstructorWithArgs'))
	suite.addTest(BIAFlowsTest('testDownloadPicture'))
	suite.addTest(BIAFlowsTest('testGetHost'))
	suite.addTest(BIAFlowsTest('testSetHost'))
	suite.addTest(BIAFlowsTest('testGetPublicKey'))
	suite.addTest(BIAFlowsTest('testSetPublicKey'))
	suite.addTest(BIAFlowsTest('testGetPrivateKey'))
	suite.addTest(BIAFlowsTest('testSetPrivateKey'))
	suite.addTest(BIAFlowsTest('testGetUploadURL'))	
	suite.addTest(BIAFlowsTest('testGetInstance'))

	suite.addTest(ProjectsTest('testConstructor'))
	suite.addTest(ProjectsTest('testUpdateFromServer'))
	suite.addTest(ProjectsTest('testGetNames'))
	suite.addTest(ProjectsTest('testGetIDs'))

	suite.addTest(StoragesTest('testConstructor'))
	suite.addTest(StoragesTest('testUpdateFromServer'))
	suite.addTest(StoragesTest('testGetNames'))
	suite.addTest(StoragesTest('testGetIDs'))

	suite.addTest(UploaderTest('testConvertImageToOME'))
	suite.addTest(UploaderTest('testConvertImagesInFolderToOME'))
	suite.addTest(UploaderTest('testUploadImage'))
	suite.addTest(UploaderTest('testUploadImagesInFolder'))
	suite.addTest(UploaderTest('testGetObservers'))
		
	return suite
	
runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
runner.run(suite())
