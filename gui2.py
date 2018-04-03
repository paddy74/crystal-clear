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
import cv2
import os
import subprocess


PATH_TO_OBJ_REC = './crystal-clear/object_detection/classify_image.py'
PATH_TO_IMG = './crystal-clear/object_detection/tests/'
IMG_NAME = 'IMG.jpg'
PATH_TO_MODEL = './crystal-clear/object_detection/tmp/imagenet'
GUESS_COUNT = '1' 


Builder.load_string('''
<MenuScreen>:
	FloatLayout:
	
	
		AnchorLayout:
			anchor_x: 'right'
			anchor_y: 'bottom'

			Button:
				text: 'Settings'
				size: 100, 60
				size_hint: None, None
				on_press:
					root.manager.transition.direction = 'left'
					root.manager.current = 'settings'
			
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'
		
			Button:
				text: 'History'
				size: 100, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
		
		AnchorLayout:
			anchor_x:'center'
			anchor_y:'bottom'
			
			Button:
				text: 'Test Cam'
				size: 100, 60
				size_hint: None, None
				opacity: 1 if self.state == 'normal' else .5
				on_press:
					root.manager.transition.direction = 'left'
					root.manager.current = 'cam'
					
<CameraScreen>:
	FloatLayout:
	
	
		AnchorLayout:
			anchor_x: 'left'
			anchor_y: 'bottom'

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
	
			Button:
				text: root.objectLabel
				size: 300, 60
				size_hint: None, None
				
		Camera:
			id: camera
			resolution: (640, 480)
			play: True
			
	
				
		   
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
			size: 100, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 2 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'langs'
		
			
		Button:
			text: 'Power Settings'
			size: 100, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'power'
				
					
		Button:
			text: 'Report an Issue'
			size: 100, 60
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
					
<LanguagesScreen>:

	RelativeLayout:
		Label:
			text: 'Settings'
			font_size: '16sp'
			bold: True
			halign: 'center'
			valign: 'top'
			text_size: self.size
			

		Button:
			id: natlang
			text: 'Native'
			size: 100, 60
			size_hint: None, None
			pos: root.width/2 - self.width, root.height - 2 * self.height
			opacity: 1 if self.state == 'normal' else .5
	#		on_release: dropdown.open(self)
			
		Button:
			text: 'Download Languages'
			size: 100, 60
			size_hint: None, None
			pos: root.width/2 - self.width/2, root.height - 4 * self.height
			opacity: 1 if self.state == 'normal' else .5
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'power'
				
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
		self.objectLabel = file.readline()
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
	
if __name__ == '__main__':
    TestApp().run()