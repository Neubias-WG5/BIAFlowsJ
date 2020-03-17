import re
from javax.swing.event import HyperlinkEvent	
from ij.gui import HTMLDialog
from ij import IJ, WindowManager
from ij.gui import HTMLDialog
from be.cytomine.client import CytomineException
from be.cytomine.client.collections import ProjectCollection, AttachedFileCollection
from be.cytomine.client.models import Project, Description, AttachedFile
from os.path import expanduser
from java.awt import Frame, TextField, Button, Label, FlowLayout
from java.awt.event import TextListener, ActionListener, WindowListener

from biaflowsj.lib import BIAFlows

class ProjectDialog(object):
	'''
	Display a list of BIAFlows workflows and let the user download data and run workflows.
	'''

	def __init__(self, download = True):
		'''
		Display the list of project descriptions in a non-modal dialog.
		'''
		super(ProjectDialog, self).__init__(self)
		self.biaflows = ConnectionWindow.getInstance().getBiaflows()
		IJ.showStatus('Connecting to: ' + self.biaflows.getHost() + " - please stand by...")
		self.download = download
		self.eventHandler = ProjectDialogEventHandler('BIAFlows', self.getHTML(), False)

	def getTitle(self):
		return self.eventHandler.getTitle()

	def dispose(self):
		WindowManager.removeWindow(self.eventHandler)
		self.eventHandler.dispose()

	def getHTML(self):
		'''
		Get the list of project descriptions as HTML.
		'''
		content = ''
		projectData = self.getProjectData()
		for entry in projectData:
			content = content + entry['message']
		return content
		
	def getProjectData(self):
		'''
		Retrieve the project data of all available projects from the BIAFLOWS server.
		'''
		projects = ProjectCollection().fetch()
		projectData = []
		for i in range(0, projects.size()):
			if (i%2):
				IJ.showStatus('Connecting to: ' + self.biaflows.getHost() + " - please stand by.../")
			else:
				IJ.showStatus('Connecting to: ' + self.biaflows.getHost() + " - please stand by...\\")
			project = projects.get(i)
			name = project.get("name")
			pId = project.get('id')
			try:
				text = Description().fetch(project).get('data')
				text = self.downloadThumbnailsAndReplaceLinks(text)
				message = '\n' + '<h1>' + name + '</h1>' 
				message = message + '\n' + text
				projectData.append({'id': pId, 'name': name, 'message': message})
			except CytomineException, e:
				print(e.getMessage())
				continue
		projectData.sort(key=lambda x: x['name'], reverse=False)
		return projectData

	def downloadThumbnailsAndReplaceLinks(self, text):
		'''
		Download the thumbnail-images of the project and replace
		the links in the text to display the local thumbnails.
		'''
		home = expanduser("~")
		thumbIDs = re.findall('<img src="api/attachedfile/(.+?)/download">', text)
		for thumbID in thumbIDs:
			thumbOutPath = home+'/tmp/thumb'+str(thumbID)+'.jpg'
			if self.download:
				self.biaflows.downloadPicture('/api/attachedfile/', thumbIDs[0], thumbOutPath)
			thumbLink = 'file://' + thumbOutPath
			text = text.replace('api/attachedfile/'+ thumbID + '/download', thumbLink)
		return text

class ProjectDialogEventHandler(HTMLDialog):
	'''
	Event handler for the project dialog.

	Handles actions that are triggered by clicks on urls in the
	dialog.
	'''
	def hyperlinkUpdate(self, e):
		'''
		Handle a click on a link in the dialog.
		'''
		if e.getEventType() == HyperlinkEvent.EventType.ACTIVATED:
			url = e.getDescription(); 
			print(url)

	def windowClosing(self, e):
		self.dispose()
		WindowManager.removeWindow(self)

class ConnectionWindow(Frame, TextListener, WindowListener, ActionListener):
	@classmethod
	def getInstance(cls):
		winList = [x for x in WindowManager.getNonImageWindows() if x.getTitle()=='BIAFlows Connection']
		if not winList:
			return ConnectionWindow()
		else:
			winList[0].setVisible(True)
			return winList[0]
			
	def __init__(self): 
		super(ConnectionWindow, self).__init__("BIAFlows Connection")
		self.biaflows = BIAFlows.getInstance()
		self.createAndShowGUI()
		self.addWindowListener(self)
		WindowManager.addWindow(self)

	def getBiaflows(self):
		return self.biaflows
		
	def textValueChanged(self, e):
		tc = e.getSource()
		name = tc.getName();
		if name=='host':
			self.biaflows.setHost(tc.getText())
		if name=='publicKey':
			self.biaflows.setPublicKey(tc.getText())
		if name=='privateKey':
			self.biaflows.setPrivateKey(tc.getText())

	def windowClosing(self, e):  
		self.setVisible(False)

	def windowActivated(self, e):  
		pass

	def windowDeactivated(self, e):  
		pass

	def windowClosed(self, e):  
		pass

	def actionPerformed(self, e):
		self.dispose()
		WindowManager.removeWindow(self)
		
	def createAndShowGUI(self):
		self.setLayout(FlowLayout())

		serverLabel = Label("BIAFlows host: ");
		serverField =TextField(30)
		serverField.setName('host')
		serverField.setText(self.biaflows.getHost())
		serverField.addTextListener(self)
		publicKeyLabel = Label("public key: ")
		publicKeyField=TextField(40)
		publicKeyField.setName('publicKey')
		publicKeyField.setText(self.biaflows.getPublicKey())
		publicKeyField.addTextListener(self)
		privateKeyLabel = Label("private key: ")
		privateKeyField=TextField(40)
		privateKeyField.setName('privateKey')
		privateKeyField.setEchoChar('*')
		privateKeyField.setText(self.biaflows.getPrivateKey())
		privateKeyField.addTextListener(self)

		closeButton = Button("Disconnect and close")
		closeButton.addActionListener(self)

		self.add(serverLabel)
		self.add(serverField)
		self.add(publicKeyLabel)
		self.add(publicKeyField)
		self.add(privateKeyLabel)
		self.add(privateKeyField)
		self.add(closeButton)
				
		self.setSize(400,250)
		self.setVisible(True)