import re, os, shutil
from javax.swing.event import HyperlinkEvent	
from ij.gui import HTMLDialog
from ij import IJ, WindowManager
from ij.gui import HTMLDialog
from be.cytomine.client import CytomineException
from be.cytomine.client.collections import ProjectCollection, AttachedFileCollection
from be.cytomine.client.models import Project, Description, AttachedFile
from os.path import expanduser
from java.awt import Frame, TextField, Button, Label, FlowLayout, GridBagLayout, Choice, Checkbox, GridBagConstraints
from java.awt.event import TextListener, ActionListener, WindowListener

from biaflowsj.lib import BIAFlows, Projects, Storages, Uploader

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
		'''
		Answer the title of the window.
		'''
		return self.eventHandler.getTitle()

	def dispose(self):
		'''
		Close the window and remove it from the ij-window-manager.
		'''
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
	'''
	A window that allows to enter a biaflows host and the public and private keys
	needed to connect to the host.
	'''
	@classmethod
	def getInstance(cls):
		winList = [x for x in WindowManager.getNonImageWindows() if x.getTitle()=='BIAFlows Connection']
		if not winList:
			return ConnectionWindow()
		else:
			winList[0].setVisible(True)
			return winList[0]
			
	def __init__(self): 
		'''
		Create and display the connection window.
		'''
		super(ConnectionWindow, self).__init__("BIAFlows Connection")
		self.biaflows = BIAFlows.getInstance()
		self.createAndShowGUI()
		self.addWindowListener(self)
		WindowManager.addWindow(self)

	def getBiaflows(self):
		'''
		Answer the biaflows-instance.
		'''
		return self.biaflows
		
	def textValueChanged(self, e):
		'''
		Event handler for changes in the input.

		Sets the new data in the biaflows instance.
		'''
		tc = e.getSource()
		name = tc.getName();
		if name=='host':
			self.biaflows.setHost(tc.getText())
		if name=='publicKey':
			self.biaflows.setPublicKey(tc.getText())
		if name=='privateKey':
			self.biaflows.setPrivateKey(tc.getText())

	def windowClosing(self, e):  
		'''
		Only hides the window without disposing of it.

		The connection data remains accessible.
		'''
		self.setVisible(False)

	def windowActivated(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def windowDeactivated(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def windowClosed(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def actionPerformed(self, e):
		'''
		Event handler for the close button.

		Closes the window. The connection data will not be accessible afterwards.
		'''
		self.dispose()
		WindowManager.removeWindow(self)
		
	def createAndShowGUI(self):
		'''
		Create and display the gui.
		'''
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

class UploadWindow(Frame, WindowListener, ActionListener):
	'''
	A window to upload images to the biaflows server.

	The images can be uploaded as inut or as ground-truth images. Input images can
	be converted to the ome-tif format. Ground-truth images are always converted to
	ome-tif, if they are not alread in ome-tif format.
	'''
	def __init__(self): 
		'''
		Create and display the upload window.
		'''
		super(UploadWindow, self).__init__("BIAFlows Image Upload")
		self.biaflows = ConnectionWindow.getInstance().getBiaflows()
		projects = Projects()
		self.projectNames = projects.getNames()
		self.projectIDs = projects.getIDs()
		storages = Storages()
		self.storageNames = storages.getNames()
		self.storageIDs = storages.getIDs()
		self.createAndShowGUI()
		self.addWindowListener(self)
		WindowManager.addWindow(self)

	def windowClosing(self, e):   
		'''
		Close the image upload window and dispose of it. 

		Also remove it from the ij-window-manager.
		'''
		self.dispose()
		WindowManager.removeWindow(self)
		
	def windowActivated(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def windowDeactivated(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def windowClosed(self, e):  
		'''
		Nothing to do.
		'''
		pass

	def createAndShowGUI(self):
		'''
		Create and display the gui.
		'''
		layout = GridBagLayout()
		c = GridBagConstraints()
		self.setLayout(layout)
		projectLabel = Label("Project: ")
		c.gridx = 0
		c.gridy = 0
		c.ipady = 5
		c.ipadx = 5
		c.anchor = GridBagConstraints.EAST
		layout.setConstraints(projectLabel, c)
		self.projectChoice = Choice()
		for name in self.projectNames:
			self.projectChoice.add(name)
		c.gridx = 1
		c.gridy = 0
		c.fill = GridBagConstraints.HORIZONTAL 
		layout.setConstraints(self.projectChoice, c)
		storageLabel = Label("Storage: ")
		c.gridx = 0
		c.gridy = 1
		c.fill = GridBagConstraints.NONE 
		c.anchor = GridBagConstraints.EAST
		layout.setConstraints(storageLabel, c)
		self.storageChoice = Choice()
		for name in self.storageNames:
			self.storageChoice.add(name)	
		c.gridx = 1
		c.gridy = 1
		c.fill = GridBagConstraints.HORIZONTAL 
		layout.setConstraints(self.storageChoice, c)
		self.convertToOMETIFCheckBox = Checkbox("convert to OME-TIF", True)
		c.gridx = 1
		c.gridy = 2
		layout.setConstraints(self.convertToOMETIFCheckBox, c)
		self.uploadAsGroundTruthCheckBox = Checkbox("upload as ground-truth images")
		c.gridx = 1
		c.gridy = 3
		layout.setConstraints(self.uploadAsGroundTruthCheckBox, c)
		self.folderTextField = TextField("", 15)
		self.folderTextField.setText("<Image-Folder>")
		c.gridx = 0
		c.gridy = 4
		layout.setConstraints(self.folderTextField, c)
		self.folderTextField.setEditable(False)
		browseButton = Button('Browse...')
		browseButton.addActionListener(self)
		c.gridx = 1
		c.gridy = 4
		layout.setConstraints(browseButton, c)
		statusLabel = Label("Status:")
		c.gridy = 5
		c.gridx = 0
		c.fill = GridBagConstraints.NONE 
		c.anchor = GridBagConstraints.EAST
		layout.setConstraints(statusLabel, c)
		self.statusTextField = TextField("Select a folder!", 20)
		c.gridy = 5
		c.gridx = 1
		c.fill = GridBagConstraints.HORIZONTAL 
		layout.setConstraints(self.statusTextField, c)
		self.statusTextField.setEditable(False)
		self.uploadButton = Button("Upload Images")
		self.uploadButton.addActionListener(self)
		c.gridwidth = 2
		c.gridheight = 2
		c.gridy = 6
		c.gridx = 0
		c.weighty = 1.0
		layout.setConstraints(self.uploadButton, c)
		self.add(projectLabel)
		self.add(self.projectChoice)
		self.add(storageLabel)
		self.add(self.storageChoice)
		self.add(self.convertToOMETIFCheckBox)
		self.add(self.uploadAsGroundTruthCheckBox)
		self.add(self.folderTextField)
		self.add(browseButton)
		self.add(statusLabel)
		self.add(self.statusTextField)
		self.add(self.uploadButton)
		self.setSize(400,300)
		self.setVisible(True)		

	def actionPerformed(self, e):
		'''
		Event handler for the buttons.
		'''
		cmd = e.getActionCommand()
		if cmd=='Browse...':
			folder = IJ.getDirectory("Select the image folder")
			if not folder:
				return
			self.folderTextField.setText(folder)
			images = Uploader.getImageList(folder)
			self.nrOfImagesToUpload = len(images)
			self.inputFolder = folder
			self.statusTextField.setText(str(self.nrOfImagesToUpload) + ' images to upload...')
		if cmd=='Upload Images':
			if self.nrOfImagesToUpload < 1:
				return
			else:
				# convert if ome checked. Add _lbl if ground-truth checked. upload
				self.statusTextField.setText('Uploading ' + str(self.nrOfImagesToUpload) + ' images...')
				imageFolder = self.folderTextField.getText()
				uploader = Uploader()
				if self.convertToOMETIFCheckBox.getState() or self.uploadAsGroundTruthCheckBox.getState():
					self.statusTextField.setText('Converting ' + str(self.nrOfImagesToUpload) + ' images...')
					# convert and add '_lbl' if ground truth
					tmpFolder = imageFolder + os.sep + 'biaflows_tmp/'
					suffix = ''
					if self.uploadAsGroundTruthCheckBox.getState():
						suffix = '_lbl'
					uploader.convertImagesInFolderToOME(imageFolder, tmpFolder, suffix)
					imageFolder = tmpFolder
				# upload
				pid = self.projectIDs[self.projectChoice.getSelectedIndex()]
				sid = self.storageIDs[self.storageChoice.getSelectedIndex()]
				self.statusTextField.setText('Uploading ' + str(self.nrOfImagesToUpload) + ' images...')
				nr = uploader.uploadImagesInFolder(imageFolder, str(pid), str(sid))
				# cleanup
				self.statusTextField.setText('Done uploading '+str(nr) + ' images.')
				if self.convertToOMETIFCheckBox.getState():
					shutil.rmtree(tmpFolder)