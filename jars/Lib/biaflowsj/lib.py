from be.cytomine.client import Cytomine

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
		
	@classmethod
	def getInstance(cls):
		'''
		Get the current instance.

		If no current instance exists a new one with default-connection
		data is created and returned.
		'''
		if not cls.__INSTANCE:
			cls.__INSTANCE = BIAFlows()
		return cls.__INSTANCE