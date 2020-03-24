import os
from java.io import File
from ij import IJ
from org.apache.http.entity.mime import MultipartEntity
from org.apache.http.entity.mime.content import FileBody
from org.json.simple import JSONValue
from be.cytomine.client import Cytomine, HttpClient
from be.cytomine.client.collections import ProjectCollection, StorageCollection

class BIAFlows(object):
	'''
	A proxy to access a biaflows server.
	'''
	__DEFAULT_SERVER = 'https://biaflows.neubias.org'
	__DEFAULT_PUBLIC_KEY = 'c0f3be78-a1a7-4d86-ad09-9e1753f26a8b'
	__DEFAULT_PRIVATE_KEY = '73b7df42-3484-4c1b-9bf2-8d9e3ea53eac'
	__INSTANCE = None

	def __init__(self, server=None, publicKey=None, privateKey=None):
		'''
		Create a new instance with the server-url and the public and
		private key for authentiction.
		'''
		super(BIAFlows, self).__init__()
		self.server = server if server else self.__DEFAULT_SERVER
		self.publicKey = publicKey if publicKey else self.__DEFAULT_PUBLIC_KEY
		self.privateKey = privateKey if privateKey else self.__DEFAULT_PRIVATE_KEY
		self.connection = Cytomine.connection(self.server, self.publicKey, self.privateKey)
		BIAFlows.__INSTANCE = self

	def downloadPicture(self, relativeURL, picID, outPath):
		'''
		Download a picture (for example a project-thumbnail).
		'''
		self.connection.downloadPicture(self.connection.getHost() + relativeURL + picID + '/download', outPath)

	def getHost(self):
		'''
		Answer the url of the host.
		'''
		return self.server

	def setHost(self, host):
		'''
		Set the host.
		'''
		self.server = host
		self.connection = Cytomine.connection(self.server, self.publicKey, self.privateKey)
		
	def getPublicKey(self):
		'''
		Answer the public key.
		'''
		return self.publicKey

	def setPublicKey(self, publicKey):
		'''
		Set the public key.
		'''
		self.publicKey = publicKey
		self.connection = Cytomine.connection(self.server, self.publicKey, self.privateKey)
	
	def getPrivateKey(self):
		'''
		Answer the private key.
		'''
		return self.privateKey

	def setPrivateKey(self, privateKey):
		'''
		Set the private key.
		'''
		self.privateKey = privateKey
		self.connection = Cytomine.connection(self.server, self.publicKey, self.privateKey)

	def getUploadURL(self):
		'''
		Construct the url of the upload-server from the biaflows host url.
		'''
		protocol = ''
		url = self.getHost()
		result = url
		if url.find('://') >= 0:
			protocol = url.split("://")[0]
			result = url.split("://")[1]
		firstPartOfHost = result.split('.')[0]
		firstPartOfHost = firstPartOfHost.replace('/', '')
		replacement = firstPartOfHost + "-upload"
		result = url.replace(firstPartOfHost, replacement) + "/"
		return result
	
	@classmethod
	def getInstance(cls):
		'''
		Get the current instance.

		If no current instance exists a new one with default-connection
		data is created and returned.
		'''
		if not cls.__INSTANCE:
			BIAFlows()
		return cls.__INSTANCE

class Uploader(object):
	'''
	Upload data to the biaflows server.
	'''
	__INSTANCE = None

	IMAGE_FILE_EXTENSIONS = ['tif', 'tiff', 'jpg', 'jpeg']

	def convertImagesInFolderToOME(self, folder, outFolder, suffix = ''):
		'''
		Convert all images in folder to ome-tif and save the results
		into outFolder.
		'''
		print(folder)
		print(outFolder)
		images = Uploader.getImageList(folder)
		for image in images:
			self.convertImageToOME(folder + image, outFolder, suffix)
		
	def convertImageToOME(self, image, outFolder, suffix = ''):
		'''
		Convert an image to ome-tif and save it into the outFolder. 
		'''
		if not outFolder.endswith(os.sep):
			outFolder = outFolder + os.sep
			
		if not os.path.isdir(outFolder):
			os.mkdir(outFolder)
		path, filename = os.path.split(image)	
		outfilename = filename
		if not outfilename.lower().endswith('.ome.tif'):
			root, ext = os.path.splitext(outfilename)
			if root.endswith('_lbl'):
				suffix = ''
			outfilename = root + suffix + ".ome.tif"
		imp = IJ.openImage(image)
		out = outFolder + outfilename
		IJ.run(imp, "OME-TIFF...", "save="+out+" compression=Uncompressed");
		imp.close()

	def uploadImagesInFolder(self, folder, projectID, storageID):
		'''
		Upload all images in the folder.

		The images will be associated to a project and a storage. Returns the number of
		successfully uploaded images.
		'''
		images = Uploader.getImageList(folder)
		nrOfUploadedImages = 0
		for image in images:
			code, _ = self.uploadImage(folder + image, projectID, storageID)
			if not code==200:
				print('Error ('+code+') uploading image: ' + folder + image)
			else:
				nrOfUploadedImages = nrOfUploadedImages + 1
		return nrOfUploadedImages
		
	def uploadImage(self, aFile, projectID, storageID):
		'''
		Upload an image to the server. 

		The image will be associated to a project and a storage.
		'''
		biaflows = BIAFlows.getInstance()
		host = biaflows.getUploadURL()
		client = HttpClient(biaflows.getPublicKey(), biaflows.getPrivateKey(), host)
		url = "/upload?idStorage=" + storageID + "&cytomine=" + biaflows.getHost() + "&idProject=" + projectID
		entity = MultipartEntity()
		entity.addPart("files[]", FileBody(File(aFile)))
		client.authorize("POST", url, entity.getContentType().getValue(), "application/json,*/*")
		client.connect(host + url)
		code = client.post(entity)
		response = client.getResponseData()
		client.disconnect()
		obj = JSONValue.parse(response)
		return code, obj

	@classmethod
	def getImageList(cls, folder):
		'''
		Get a list of the image files in the folder.
		'''
		files = os.listdir(folder)
		images = [f for f in files if os.path.isfile(folder + f) and f.split('.')[-1] in Uploader.IMAGE_FILE_EXTENSIONS]
		return images
		
	@classmethod
	def getInstance(cls):
		'''
		Get the current instance of the uploader. 

		Creates and returns a new instance if none exists.
		'''
		if not cls.__INSTANCE:
			cls.__INSTANCE = Uploader()
		return cls.__INSTANCE

class Projects(object):
	def __init__(self):
		'''
		Create a new Projects instance.
		'''
		super(Projects, self).__init__()
		self.projectNames = []
		self.projectIDs = []
		self.updateFromServer()

	def updateFromServer(self):
		'''
		Update the local list of project names and ids from the server.
		'''
		names = []
		ids = []
		projectCollection = ProjectCollection().fetch()
		for i in range(0, projectCollection.size()):
			project = projectCollection.get(i)
			names.append(project.get('name'))
			ids.append(project.get('id'))
		projectTupels = zip(ids, names)
		projectTupels.sort(key=lambda tup: tup[1]) 
		unzipped = [list(t) for t in zip(*projectTupels)]
		self.projectIDs = unzipped[0]
		self.projectNames = unzipped[1]

	def getNames(self):
		return self.projectNames

	def getIDs(self):
		return self.projectIDs

class Storages(object):
	def __init__(self):
		'''
		Create a new Storages instance.
		'''
		super(Storages, self).__init__()
		self.storageNames = []
		self.storageIDs = []
		self.updateFromServer()

	def updateFromServer(self):
		names = []
		ids = []
		collection = StorageCollection().fetch()
		for i in range(0, collection.size()):
			storage = collection.get(i)
			names.append(storage.get('name'))
			ids.append(storage.get('id'))
		storageTupels = zip(ids, names)
		storageTupels.sort(key=lambda tup: tup[1]) 
		unzipped = [list(t) for t in zip(*storageTupels)]
		self.storageIDs = unzipped[0]
		self.storageNames = unzipped[1]

	def getNames(self):
		return self.storageNames

	def getIDs(self):
		return self.storageIDs
	