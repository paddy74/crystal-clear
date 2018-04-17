import cv2 
import webbrowser
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.base import runTouchApp
from imutils.video import VideoStream
from imutils.video import FPS
from kivy.properties import StringProperty
import numpy as np
import argparse
import imutils
import time
from datetime import datetime
import sqlite3
from kivy.uix.textinput import TextInput
import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.uix.boxlayout import BoxLayout
import sys
from kivy.uix.popup import Popup
import pyttsx3

# Defines paths to file dependencies
PATH_TO_OBJ_REC = './crystal-clear/object_detection/classify_image.py'
PATH_TO_IMG = './crystal-clear/object_detection/tests/'
IMG_NAME = 'IMG.jpg'
PATH_TO_MODEL = './crystal-clear/object_detection/tmp/imagenet'
GUESS_COUNT = '1' 
PATH_TO_LANGFUNCTIONS = './crystal-clear/language_translation/'
PATH_TO_TRANSLATION = './crystal-clear/language_translation/data/translated_Definitions.txt'
PATH_TO_DEFINITION = './crystal-clear/language_translation/data/spanish/definition.pkl'
PATH_TO_USECASE = './crystal-clear/language_translation/data/spanish/use_case.pkl'
PATH_TO_AUDIO = './crystal-clear/language_translation/data/spanish/audio.pkl'
chosenPictureInHistory = ""

import classify_image as cl

Builder.load_string('''
<MenuScreen>:
	FloatLayout:
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'bottom'

			Button:
				text: 'Settings'
				size: 150, 60
				size_hint: None, None
				on_press:
					root.manager.transition.direction = 'left'
					root.manager.current = 'settings'
			
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'
		
			Button:
				text: 'History'
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.current = 'hist'
		
		AnchorLayout:
			anchor_x:'center'
			anchor_y:'bottom'
			
			Button:
				text: 'Test Cam'
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'left'
					root.manager.current = 'cam'
					
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
					
<CameraScreen>:
	AnchorLayout:
	
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: root.playSound()
				
				Image:
					source: 'speaker.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
		
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'

			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'menu'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
			
		AnchorLayout:
			anchor_x: 'center'
			anchor_y: 'bottom'
	
			Button:
				text: 'Capture'
				size: 100, 60
				size_hint: None, None
				on_press: root.takePicture(), root.runScript(), root.updateText()
					
		AnchorLayout:
			anchor_x: 'center'
			anchor_y: 'top'
	
			Label:
				text: root.objectLabel
				size: 600, 60
				size_hint: None, None
				text_size: self.size
				
		Camera:
			id: camera
			resolution: (640,480)
			play: True
					   
<SettingsScreen>:
	RelativeLayout:
	
		Label:
			text: 'Settings'
			font_size: '25sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
			
		Button:
			text: 'Language Settings'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 2 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'langs'
		
			
		Button:
			text: 'Power Settings'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'power'
				
					
		Button:
			text: 'Report an Issue'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 6 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'report' 
		
		
		AnchorLayout:
			anchor_x:'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'menu'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True

<HistoryScreen>:
	on_enter: root.clearGrid(), root.load_content()
	FloatLayout:
	
		BoxLayout:
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'menu'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
				
			GridLayout:	  
				cols: 2
				# just add a id that can be accessed later on
				id: content
				
#Delete button				
			Button:
				text: 'Clear History'
				size: 110, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: 
					root.deleteHistory()
					root.manager.current = 'hist'
					root.clearGrid()
					root.load_content()

<ImageScreen>:
	on_enter: root.setPicture()
	AnchorLayout:
	
		AnchorLayout:
			anchor_x: 'center'
			anchor_y: 'bottom'			
			Image:
				source: ""
				y: self.parent.y
				x: self.parent.x
				size: 150, 60
				id: image
		
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
		
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: root.playSound()
				
				Image:
					source: 'speaker.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
		
		AnchorLayout:
			anchor_x: 'center'
			anchor_y: 'top'
			
			Label:
				text: root.objectInformation
				size: 600, 60
				size_hint: None, None
				text_size: self.size

		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'hist'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'bottom'
			
				#Delete button				
			Button:
				text: 'Delete from History'
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: 
					root.deleteObject() 
					root.manager.current = 'hist'	

					
				
<LanguagesScreen>:

	RelativeLayout:
		Label:
			text: 'Language Settings'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
			
			

		Button: 
			text: root.button_text
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 2 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_release: root.open_drop_down(self)
		
		Button: 
			text: root.button_text2
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_release: root.open_2(self)
			
			
		Button:
			text: 'Download Languages'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 6 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'download'
	
		AnchorLayout:
			anchor_x:'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
					
<CustomDropDown1>:
	padding: [0,0,0,0]
	Button:
		text: 'English'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
	Button:
		text: 'Spanish'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
	Button:
		text: 'Pig Latin'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
		
<CustomDropDown2>:
	padding: [0,0,0,0]
	Button:
		text: 'English'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
	Button:
		text: 'Spanish'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
	Button:
		text: 'Pig Latin'
		size:(200,50)
		size_hint:(None,None)
		text_size: self.size
		valign: 'center'
		padding: (10,0)
		on_release: root.select(self.text)
				
<PowerScreen>:


	on_enter: root.start()
	
	RelativeLayout:
	
		Label:
			text: 'Power Settings'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
			
		Button:
			id: lp
			background_normal: ''
			text: 'Low Power Mode'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 6 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_release: root.loww()
				
		Button:
			id: hp
			background_normal: ''
			text: 'High Power Mode'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_release: root.highh()

			
		AnchorLayout:
			anchor_x:'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
				
<DownloadScreen>:

	RelativeLayout:
	
	
		Label:
			text: 'Downloaded Languages'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
		
		AnchorLayout:
			anchor_x: 'center'
			anchor_y: 'bottom'
					
			Button:
				text: 'Download Packs'
				multiline: True
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: root.website()
		
		
		
		AnchorLayout:
			anchor_x:'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True
					
<IssueScreen>:
	email: email_in
	sub: sub_in
	rep: report_in

	RelativeLayout:
		Label:
			text: 'Report an Issue'
			font_size: '25sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
		
		Label: 
			text: 'Email Address:'
			font_size: '16sp'
			bold: True
			pos_hint: {'center_x' : .35, 'center_y' : .85}
			
		Label:
			text: 'Subject Line:'
			font_size: '16sp'
			bold: True
			pos_hint: {'center_x': .34, 'center_y' : .69}
			
		Label: 
			text: 'Body:'
			font_size: '16sp'
			bold: True
			pos_hint: {'center_x' : .31, 'center_y' : .54}
		
		AnchorLayout:
			anchor_x:'left'
			anchor_y: 'bottom'
			
			Button:
				text: ''
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
				Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 90, 60
					#allow_stretch: True		
	
		BoxLayout:
			orientation: 'vertical'
			spacing: 50
			padding: [50, 40, 60, 20]	
			
			Label:
				text: '---'
				font_size: '16sp'
				bold: True
				pos_hint: {'center_x' : .5}
				size_hint: [.01, .01]
			
			
			TextInput:
				id: email_in
				multiline: False
				text: ''
				pos_hint: {'center_x' : .5 , 'y' : .3}
				size_hint: [.5, .05]
			
			TextInput:
				id: sub_in
				multiline: False
				text: ''
				pos_hint: {'center_x' : .5, 'y' : .3}
				size_hint: [.5, .05]
				
			TextInput:
				id: report_in
				auto_indent: True
				multiline: True
				text: ''
				pos_hint: {'center_x' : .5, 'y' : .5}
				size_hint: [.5, .2]
			
			
			Button:
				text: 'Submit'
				size: 80, 20
				pos_hint: {'center_x' : .5, 'center_y' : .1}
				size_hint: [.5, .08]
				on_press: app.save(email_in.text, sub_in.text, report_in.text)
	
	
''')

class MenuScreen(Screen):
	pass

class SettingsScreen(Screen):
	pass

class HistoryScreen(Screen):
	#Variable to hold main ID(time stamp) that will be insert into the currentImage table 
	pictureID = 0.0
	#Variables to hold the ID(time stamp) for each button
	pictureID0 = 0.0
	pictureID1 = 0.0
	pictureID2 = 0.0
	pictureID3 = 0.0
	pictureID4 = 0.0
	pictureID5 = 0.0
	pictureID6 = 0.0
	pictureID7 = 0.0
	pictureID8 = 0.0
	pictureID9 = 0.0
		
	def selectImage(self):
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object 
		c = conn.cursor()
		#Delete contents of table currentImage
		c.execute("delete from currentImage")
		#Insert selected picture time stamp into currentImage table
		c.execute("insert into currentImage (tStamp) values (?)", (float(self.pictureID),))
		#Commit changes 
		conn.commit()
		#Close connection to DB 
		conn.close()
		return 
	#Function to clear all widgets attached to grid layout 
	def clearGrid(self):
		self.ids.content.clear_widgets()
		return
	#Function to change to ImageScreen and load first image in grid layout to that screen 
	def viewImage0(self):
		self.pictureID = self.pictureID0
		self.selectImage()
		sm.current = 'img'
		return
	#Function to change to ImageScreen and load second image in grid layout to that screen
	def viewImage1(self):
		self.pictureID = self.pictureID1
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load third image in grid layout to that screen	
	def viewImage2(self):
		self.pictureID = self.pictureID2
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load fourth image in grid layout to that screen	
	def viewImage3(self):
		self.pictureID = self.pictureID3
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load fifth image in grid layout to that screen	
	def viewImage4(self):
		self.pictureID = self.pictureID4
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load sixth image in grid layout to that screen	
	def viewImage5(self):
		self.pictureID = self.pictureID5
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load seventh image in grid layout to that screen	
	def viewImage6(self):
		self.pictureID = self.pictureID6
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load eighth image in grid layout to that screen	
	def viewImage7(self):
		self.pictureID = self.pictureID7
		self.selectImage()
		sm.current = 'img'
		return 
	#Function to change to ImageScreen and load ninth image in grid layout to that screen
	def viewImage8(self):
		self.pictureID = self.pictureID8
		self.selectImage()
		sm.current = 'img'
		return
	#Function to change to ImageScreen and load tenth image in grid layout to that screen	
	def viewImage9(self):
		self.pictureID = self.pictureID9
		self.selectImage()
		sm.current = 'img'
		return
	#Function to load images as buttons into the grid layout
	def load_content(self):
		imageIndex = 0
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object 
		c = conn.cursor()
		#Get all time stamps from history table 
		c.execute('SELECT timeStamp FROM history')
		#Put all data fetched into python variable 
		all_rows = c.fetchall()
		result = []
		#Fill result array with time stamps fetched from history table 
		result = [object[0] for object in all_rows]
		#Iterate through result, assign each image to a button, add corresponding function to each button, add each button to grid layout 
		for image in result:
			imageSource = PATH_TO_IMG + str(image) + ".jpg" 
			print ("debug code: " + imageSource)
			imageButton = Button(background_normal = imageSource)
			
			if imageIndex == 0:
				imageButton.on_press = self.viewImage0
				self.pictureID0 = image
				
			elif imageIndex == 1:
				imageButton.on_press = self.viewImage1
				self.pictureID1 = image
	
			elif imageIndex == 2:
				imageButton.on_press = self.viewImage2
				self.pictureID2 = image

			elif imageIndex == 3:
				imageButton.on_press = self.viewImage3
				self.pictureID3 = image

			elif imageIndex == 4:
				imageButton.on_press = self.viewImage4
				self.pictureID4 = image

			elif imageIndex == 5:
				imageButton.on_press = self.viewImage5
				self.pictureID5 = image

			elif imageIndex == 6:
				imageButton.on_press = self.viewImage6
				self.pictureID6 = image
			
			elif imageIndex == 7:
				imageButton.on_press = self.viewImage7
				self.pictureID7 = image
			
			elif imageIndex == 8:
				imageButton.on_press = self.viewImage8
				self.pictureID8 = image
				
			elif imageIndex == 9:
				imageButton.on_press = self.viewImage9
				self.pictureID9 = image
			
			self.ids.content.add_widget(imageButton)
			imageIndex += 1
		conn.close()
		return 
	#Function to delete history from the DB and the stored images 
	def deleteHistory(self):		
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object
		c = conn.cursor()
		#Delete all contents of history table from db 
		c.execute('delete from history')
		#Commit changes to DB 
		conn.commit()
		#Close connection to DB
		conn.close()
		#Fill fileList with all file names in image directory 
		fileList = os.listdir(PATH_TO_IMG)
		#Iterate through each file name and delete it from the directory 
		for fileName in fileList:
			os.remove(PATH_TO_IMG+fileName)
		return
	pass

class ImageScreen(Screen):
	#Variable to hold information in label 
	objectInformation = StringProperty()
	#Values to be set on db query 
	word = ""
	clevel = 0.0
	translatedWord = ""
	timeStamp = 0.0
	definition = ""
	
	def playSound(self):
		if self.translatedWord == "":
			engine = pyttsx3.init()
			engine.say("No translation available")
			engine.runAndWait()
		else:
			engine = pyttsx3.init()
			voices = engine.getProperty('voices')
			for voice in voices:
				if voice.name == "Microsoft Sabina Desktop - Spanish (Mexico)":
					engine.setProperty('voice',voice.id)
					break
			engine.say(self.translatedWord)
			engine.runAndWait()
		
	#Function to delete an object from db as well as the .jpg file associated with that image 
	def deleteObject(self):
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object
		c = conn.cursor()
		#Delete row from table history for object currently being viewed 
		c.execute('delete from history where timeStamp = ?', (float(self.timeStamp),))
		#commit the changes to the db 
		conn.commit()
		#close the connection to the db
		conn.close()
		#remove the image associated with the object being viewed from the image storage folder 
		os.remove(PATH_TO_IMG + str(self.timeStamp) + ".jpg")
		print ("test")
		return 

	def setPicture(self):
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object
		c = conn.cursor()
		c.execute("select * from currentImage")
		#c.execute('select h.word, h.clevel, h.translatedWord, h.timeStamp from history h, currentImage c where h.timeStamp = c.tStamp')
		c.execute('select h.word, h.clevel, h.translatedWord, h.timeStamp, t.definition from history h LEFT JOIN translation t ON h.word = t.englishW WHERE h.timeStamp IN (SELECT tStamp FROM currentImage)') 
		
		for tuple2 in c.fetchall():
			self.word = tuple2[0]
			self.clevel = tuple2[1]
			self.translatedWord = tuple2[2]
			self.timeStamp = tuple2[3]
			self.definition = tuple2[4]
		print("DEBUG word display: " + self.word)
		imageValue = str(self.timeStamp) + ".jpg"
		#print (imageValue)
		#wimg = Image(source = PATH_TO_IMG + imageValue)
		#self.add_widget(wimg)
		self.ids.image.source = PATH_TO_IMG + imageValue
		#self.objectInformation = "test"
		self.objectInformation = self.word + "\nTranslation of \'" + self.word + "\': " + self.translatedWord + "\nDefinition: " + str(self.definition)
		return 
	pass

class LanguagesScreen(Screen) :
	button_text = StringProperty('English')
	button_text2 = StringProperty('Spanish')
	def __init__(self, **kwargs):
		super(LanguagesScreen, self).__init__(**kwargs)
		self.dropdown = CustomDropDown1(self)
		self.dropdown2 = CustomDropDown2(self)
	
	def open_drop_down(self, widget):
		self.dropdown.open(widget)
	def open_2(self, widget):
		self.dropdown2.open(widget)
	pass	
	
class PowerScreen(Screen) :
	pressed = True
	np = False

	def start(self):
		self.pressed = True
		self.np = False
		self.ids.hp.background_color = 1, .3, .4, .85
		self.ids.lp.background_color = .18, .843, .227, 1

	def highh(self):
		if not self.np:
			self.ids.hp.background_color = 0.18, 0.843, 0.227, 1
			self.ids.lp.background_color = 1, .3, .4, .85
			self.np = True
			self.pressed = False
			pop = Popup(title='', content=Label(text='High Power Mode activated'), size_hint=(.5, .5))
			pop.open()
		elif self.np:
			#	background_color: 1, .3, .4, .85
			# self.np = True
			# self.pressed = False
			poppp = Popup(title='', content=Label(text='High Power mode already on'), size_hint=(.5, .5))
			poppp.open()

	def loww(self):
		if self.pressed:
			# self.pressed = True
			# self.np = False
			popp = Popup(title='', content=Label(text='Low Power mode already on'), size_hint=(.5, .5))
			popp.open()
		elif not self.pressed:
			self.ids.lp.background_color = 0.18, 0.843, 0.227, 1
			self.ids.hp.background_color = 1, .3, .4, .85
			self.pressed = True
			self.np = False
			poppi = Popup(title='', content=Label(text='Low Power Mode Activated'), size_hint=(.5, .5))
			poppi.open()
	
class IssueScreen(Screen) :
	pass

class CustomDropDown(DropDown):
	pass
	
class ReportScreen(Screen) :
	pass

class DownloadScreen(Screen) : 
	def website(instance):
		webbrowser.open('http://www.cs.odu.edu/~411crystal/')
	pass
	
class CameraScreen(Screen):
	objectLabel = StringProperty()
	timeStamp = 0
	translatedWord = ""
	def playSound(self):
		if self.translatedWord == "":
			engine = pyttsx3.init()
			engine.say("No translation available")
			engine.runAndWait()
		else:
			engine = pyttsx3.init()
			voices = engine.getProperty('voices')
			for voice in voices:
				if voice.name == "Microsoft Sabina Desktop - Spanish (Mexico)":
					engine.setProperty('voice',voice.id)
					break
			engine.say(self.translatedWord)
			engine.runAndWait()
		
	def takePicture(self):
		camera = self.ids['camera']
		self.timeStamp = time.time()
		camera.export_to_png(PATH_TO_IMG+str(self.timeStamp)+".jpg")
		return
	def runScript(self):
		#os.system("python " + PATH_TO_OBJ_REC + " --image_file " + PATH_TO_IMG + str(self.timeStamp) + ".jpg " + " --model_dir " + PATH_TO_MODEL + " --num_top_predictions " + GUESS_COUNT)
		return
	def updateText(self):
		conn = sqlite3.connect('sqlitedb.db')
		c = conn.cursor()
		
		image = PATH_TO_IMG + str(self.timeStamp) + ".jpg"
		label, clevel = cl.run_inference_on_image(image)
		
		# Take the first word of the first line and translate it
		tuple = label.partition(',')
		label = str(tuple[0])

		c.execute('SELECT spanishW, definition FROM translation where (?) = englishW', (label,))
		all_rows = c.fetchall()
		trans = ""
		defin = ""
		for row in all_rows:
			trans = str(row[0])
			defin = str(row[1])
		self.translatedWord = trans
		self.objectLabel = label + "\nTranslation of \'" + label + "\': " + trans + "\nDefinition: " + defin
		CameraScreen.insertObjectIntoHistoryDB(label,clevel,trans,self.timeStamp) 
		return	
		
	#Function to insert data into the SQLITE database, history table 
	#Takes parameters for the word, the confidence level, and a time stamp
	def insertObjectIntoHistoryDB(word, clevel, translatedWord, timeStamp):
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for DB object
		c = conn.cursor()
		#Get number of objects in DB
		c.execute("select count(*) from history")
		#Object to hold first tuple in DB
		all_rows = c.fetchone()
		#Object to hold first element in first tuple which is the count of the number of objects
		numOfObjects = all_rows[0]
		#Check if there are more than 10 objects in the DB
		if numOfObjects > 9:
			#Get minimum time stamp in history 
			c.execute("select MIN(timeStamp) from history")
			#Object to hold the row for this timeStamp 
			row = c.fetchone()
			#variable to hold the minimum timeStamp 
			timeStampMin = row[0]
			#Remove picture from memory 
			os.remove(PATH_TO_IMG + str(timeStampMin) + ".jpg")
			#Delete oldest object if there are more than 10
			c.execute("delete from history where timeStamp IN (select MIN(timeStamp) from history)")
		#Insert New object into DB
		c.execute("insert into history (word, clevel, translatedWord, timeStamp) values (?,?,?,?)", (word, clevel, translatedWord, timeStamp))
		#Save (commit) the changes
		conn.commit()
		#Close the connection
		conn.close()
		#End of function
		return
	pass
	
class CustomDropDown1(DropDown):
	def __init__(self, screen_manager, **kwargs):
		super(CustomDropDown1, self).__init__(**kwargs)
		self.sm = screen_manager
	  
	def on_select(self, data):
		self.sm.button_text = data
		
class CustomDropDown2(DropDown):
	def __init__(self, screen_manager, **kwargs):
		super(CustomDropDown2, self).__init__(**kwargs)
		self.sm = screen_manager
	  
	def on_select(self, data):
		self.sm.button_text2 = data
	
#dropdown = CustomDropDown()
#mainbutton = Button(text='Hello', size_hint=(None, None))
#mainbutton.bind(on_release=dropdown.open)
#dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
#sm.add_widget(MenuScreen(name=menu))	
		
sm = ScreenManager()

#for i in range(2): #making 2 base screens- history menu, settings menu
	#screen = Screen(name='Title %d' % i)
	#sm.add_widget(screen)
	
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(HistoryScreen(name='hist'))
sm.add_widget(PowerScreen(name='power'))
sm.add_widget(IssueScreen(name='report'))
sm.add_widget(LanguagesScreen(name='langs'))
sm.add_widget(CameraScreen(name='cam'))
sm.add_widget(DownloadScreen(name='download'))
sm.add_widget(ImageScreen(name='img'))


class TestApp(App):
	def build(self):
		return sm
		
	def save(self, email, sub, rep):
		fob = open( './crystal-clear/test.txt', 'w')
		fob.write('From: '+ email + '\n')
		fob.write('Subject: ' + sub + '\n')
		fob.write('Report: \n' + rep + '\n')
		fromaddr = email
		toaddr = 'ccreceived.reps@gmail.com'
		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = 'From: ' + email + '	Issue: ' + sub
		
		body = rep
		
		msg.attach(MIMEText(body, 'plain'))
		
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login('ccuser.reports@gmail.com', 'CrystalC!')
		text=msg.as_string()

		server.sendmail('ccuser.reports@gmail.com', toaddr, text)
		server.quit()
		fob.close()
		
	def dlist(self):
		file = open ('downloaded.txt', 'r')
		i=0;
		for line in file:
			i= i+1;
			x = line.split(',')
			print(x[0], '\t')
		
if __name__ == '__main__':
	# Check for existing db
	if os.path.isfile('./sqlitedb.db'):
		print("\nDatabase already exists, skipping DB initialization\n")
	else:
		#Connect to DB
		conn = sqlite3.connect('sqlitedb.db')
		#Cursor for database object 
		c = conn.cursor()
		#Create history table that will store the word in english, the confidence level, the translated word in spanish, and a timestamp  
		c.execute('''CREATE TABLE history
					 (word varchar(40) NOT NULL, clevel int NOT NULL, translatedWord varchar(40) NOT NULL, timeStamp int PRIMARY KEY NOT NULL)''')
		
		#Create currentImage table to store the current image being accessed in history screen 
		c.execute('''CREATE TABLE currentImage (tStamp int PRIMARY KEY NOT NULL)''')
		
		c.execute('''CREATE TABLE translation (englishW varchar(40) PRIMARY KEY NOT NULL, spanishW varchar(40), definition varchar(1000), englishP varchar(1000), spanishP varchar(1000))''')
		#Commit the changes
		conn.commit()
		#Close connection 
		conn.close()
	TestApp().run()