import cv2 
import webbrowser
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.image import Image
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

# Defines paths to file dependencies
PATH_TO_OBJ_REC = './crystal-clear/object_detection/classify_image.py'
PATH_TO_IMG = './crystal-clear/object_detection/tests/'
IMG_NAME = 'IMG.jpg'
PATH_TO_MODEL = './crystal-clear/object_detection/tmp/imagenet'
GUESS_COUNT = '1' 
PATH_TO_LANGFUNCTIONS = './crystal-clear/language_translation/'
PATH_TO_TRANSLATION = './crystal-clear/language_translation/data/spanish/translation.pkl'
PATH_TO_DEFINITION = './crystal-clear/language_translation/data/spanish/definition.pkl'
PATH_TO_USECASE = './crystal-clear/language_translation/data/spanish/use_case.pkl'
PATH_TO_AUDIO = './crystal-clear/language_translation/data/spanish/audio.pkl'

# Imports language translation functions
sys.path.insert(0,PATH_TO_LANGFUNCTIONS)
import language_translation

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
	FloatLayout:
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'

			Button:
				text: '<='
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'menu'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 100, 60
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
				size: 300, 60
				size_hint: None, None
				
		Camera:
			id: camera
			resolution: (640,480)
			play: True
			
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
			
	
				
		   
<SettingsScreen>:
	RelativeLayout:
	
		Label:
			text: 'Settings'
			font_size: '16sp'
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
			anchor_y:'top'
			
			Button:
				text: '<='
				size: 100, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'menu'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 100, 60
					#allow_stretch: True
					
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
				
<HistoryScreen>:
	on_enter: root.displayContentsOfDB()
	RelativeLayout:
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'center'
		
			Button:
				text: 'Image Display'
				size: 150, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.current = 'imgdisp'
		Label:
			text: 'History'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size

		Label:
			text: root.dbContents
			halign: 'left'
			valign: 'bottom'
			
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'top'
		
			Button:
				text: '<='
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
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 90, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
				
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'bottom'
					
			Button:
				text: 'Clear History'
				size: 120, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: root.clearHistory() 

<DisplayImageScreen>:
	on_enter: root.load_content()
    GridLayout:
        cols: 2
        # just add a id that can be accessed later on
        id: content
			
<LanguagesScreen>:

	RelativeLayout:
		Label:
			text: 'Settings'
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
			anchor_y:'top'
			
			Button:
				text: '<='
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 80, 60
					#allow_stretch: True
					
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
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

	RelativeLayout:
	
		Label:
			text: 'Power Settings'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
			
		Button:
			text: 'Low Power Mode'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 6 * self.height
			opacity: 1 if self.state == 'normal' else .5
				
		Button:
			text: 'High Power Mode'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5

			
		AnchorLayout:
			anchor_x:'left'
			anchor_y:'top'
			
			Button:
				text: ''
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 80, 60
					#allow_stretch: True
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()

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
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
		
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
			anchor_y:'top'
			
			Button:
				text: '<='
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 80, 60
					#allow_stretch: True
		Button:
			text: 'Display Downloaded Languages'
			size: 80, 60
			size_hint: None, None
			opacity: 1 if self.state == 'normal' else .5
			on_release: app.dlist(self)

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
			anchor_y:'top'
			
			Button:
				text: '<='
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'right'
					root.manager.current = 'settings'
			    Image:
					source: 'kivy.png'
					y: self.parent.y
					x: self.parent.x
					size: 80, 60
					#allow_stretch: True
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'top'
					
			Button:
				text: 'Exit'
				size: 80, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press: app.get_running_app().stop()
			
	
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
	dbContents = StringProperty()
	# List of image filenames as timestamp in seconds
	dbTimestamps = []
	def clearHistory(self):
		conn = sqlite3.connect('sqlitedb.db')
		c = conn.cursor()
		c.execute("delete from history")
		conn.commit()
		self.dbContents = "changed"
		
	def displayContentsOfDB(self):
		self.dbContents = ""
		self.dbTimestamps = []
		conn = sqlite3.connect('sqlitedb.db')
		c = conn.cursor()

		# Do this instead
		c.execute('SELECT * FROM history')
		conn.commit()
		for tuple in c.fetchall():
			objectLabel = tuple[0]
			confidenceLevel = tuple[1]
			translatedWord = tuple[2]
			self.dbTimestamps.append(tuple[3])
			timeStamp = datetime.fromtimestamp(tuple[3]).strftime("%A, %B %d, %Y %I:%M:%S")
			self.dbContents += objectLabel + "  -  " + str(confidenceLevel) + "  -  " + translatedWord + "  -  " + str(timeStamp) + "\n"
	"""
	def loadImages(self):
		for filename in self.dbTimestamps:
	"""	
	pass

class DisplayImageScreen(Screen):
	def load_content(self):
		imageSource = Image(source = 'kivy.png')
		imageButton = Button(background_normal = 'kivy.png')
		self.add_widget(imageButton)
		"""
		for image in range(10):
			imageSource = Image(source = 'kivy.png')
			imageButton = Button()
			self.ids.content.add_widget(imageButton)
		"""
	pass

class LanguageScreen(Screen) :
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
	pass
	
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
	def takePicture(self):
		camera = self.ids['camera']
		self.timeStamp = time.time()
		camera.export_to_png("crystal-clear/object_detection/tests/"+str(self.timeStamp)+".jpg")
		return
	def runScript(self):
		os.system("python " + PATH_TO_OBJ_REC + " --image_file " + PATH_TO_IMG + str(self.timeStamp) + ".jpg " + " --model_dir " + PATH_TO_MODEL + " --num_top_predictions " + GUESS_COUNT)
		return
	def updateText(self):
		file = open('output.txt')
		translation = open(PATH_TO_TRANSLATION)
		definition = open(PATH_TO_DEFINITION)
		temp = language_translation.Translator("english", "spanish")
		guess = file.readline()
		# Take the first word of the first line and translate it
		separatorIndex = guess.find(',')
		for char in guess:
			if char.isdigit():
				firstDigitIndex = guess.find(char)
				break
		if separatorIndex != -1:
			label = guess[0:separatorIndex]
		else:
			label = guess[0:firstDigitIndex-1]
		# Retrieves confidence level
		clevel = guess[firstDigitIndex:-1]
		# Retrieves translated word
		trans, data = temp.translate(label, True, False, False)
		self.objectLabel = guess + "Translation of \'" + label + "\': " + str(trans) + "\nDefinition: " + str(data["definition"])
		CameraScreen.insertObjectIntoHistoryDB(label,clevel,str(trans),self.timeStamp) 
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
		if numOfObjects > 10:
			
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
sm.add_widget(DisplayImageScreen(name='imgdisp'))
sm.add_widget(LanguageScreen(name='lang'))
sm.add_widget(PowerScreen(name='power'))
sm.add_widget(IssueScreen(name='report'))
sm.add_widget(LanguagesScreen(name='langs'))
sm.add_widget(CameraScreen(name='cam'))
sm.add_widget(DownloadScreen(name='download'))


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
		msg['Subject'] = 'From: ' + email + '   Issue: ' + sub
		
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
		conn = sqlite3.connect('sqlitedb.db')

		c = conn.cursor()
		# Create table
		c.execute('''CREATE TABLE history
					 (word, clevel, translatedWord, timeStamp)''')

		# Save (commit) the changes
		conn.commit()

		# We can also close the connection if we are done with it.
		# Just be sure any changes have been committed or they will be lost.
		conn.close()
	TestApp().run()