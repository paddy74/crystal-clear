import cv2 
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from imutils.video import VideoStream
from imutils.video import FPS
from kivy.properties import StringProperty
import numpy as np
import argparse
import imutils
import time
import sqlite3
from kivy.uix.textinput import TextInput
import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

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
	RelativeLayout
		Label:
			text: 'History'
			font_size: '26sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
				
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
			id: natlang
			text: 'Native'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 2 * self.height
			opacity: 1 if self.state == 'normal' else .5
	#		on_release: dropdown.open(self)
			
		Button:
			text: 'Download Languages'
			size: 150, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'power'
	
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

<PowerScreen>:

	RelativeLayout:
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
				
			
		
		
    #	DropDown:
	#		id: 'dropdown'
	#		on_parent: self.dismiss()
	#		on_select: btn.text = '{}'.format(args[1])
	#
	#		Button:
	#			text: 'English'
	#			size: 100, 60
	#			on_release: dropdown.select('English')
	#		
	#		Button:
	#			text: 'Spanish'
	#			size: 100, 60
	#			on_release: dropdown.select('Spanish')
	
	
''')

class MenuScreen(Screen):
	pass

class SettingsScreen(Screen):
	pass

class HistoryScreen(Screen):
	pass

class LanguageScreen(Screen) :
	pass

class LanguagesScreen(Screen) :
	pass	
	
class PowerScreen(Screen) :
	pass
	
class IssueScreen(Screen) :
	pass

class CustomDropDown(DropDown):
	pass
	
class ReportScreen(Screen) :
	pass
	
class CameraScreen(Screen):
	objectLabel = StringProperty()
	def takePicture(self):
		camera = self.ids['camera']
		timestr = time.strftime("%Y%m%d_%H%M%S")
		camera.export_to_png("crystal-clear/object_detection/tests/IMG.jpg")
		return
	def runScript(self):
		os.system("python " + PATH_TO_OBJ_REC + " --image_file " + PATH_TO_IMG + IMG_NAME + " --model_dir " + PATH_TO_MODEL + " --num_top_predictions " + GUESS_COUNT)
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
		trans, data = temp.translate(label, True, False, False)
		self.objectLabel = guess + "Translation of \'" + label + "\': " + str(trans) + "\nDefinition: " + str(data["definition"])
		return	
	pass

	
#dropdown = CustomDropDown()
#mainbutton = Button(text='Hello', size_hint=(None, None))
#mainbutton.bind(on_release=dropdown.open)
#dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
#sm.add_wdiget(MenuScreen(name=menu))	
		
sm = ScreenManager()

#for i in range(2): #making 2 base screens- history menu, settings menu
	#screen = Screen(name='Title %d' % i)
	#sm.add_widget(screen)
	
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(HistoryScreen(name='hist'))
sm.add_widget(LanguageScreen(name='lang'))
sm.add_widget(PowerScreen(name='power'))
sm.add_widget(IssueScreen(name='report'))
sm.add_widget(LanguagesScreen(name='langs'))
sm.add_widget(CameraScreen(name='cam'))



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
		
		
if __name__ == '__main__':
    TestApp().run()