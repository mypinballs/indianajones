# Loader

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *
import random
import os
from procgame._version import __version_info__


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"
machine_config_path = game_path + "config/machine.yaml"


class Loader(game.Mode):

	def __init__(self, game, priority):
            super(Loader, self).__init__(game, priority)

            self.game.sound.register_sound('up_down', sound_path+"gun_shot.aiff")
            self.game.sound.register_sound('select', sound_path+"evil_laugh.aiff")

            
            proc_game_version = '.'.join(map(str, __version_info__))

            self.selection=0
            spacer = '    '
            self.choices=['Williams L7','myPinballs v'+str(config.value_for_key_path('build_version'))+' p'+proc_game_version] #improve to pull versions from config files
            self.dates=['22/11/1993'+spacer,str(config.value_for_key_path('build_date'))+spacer]

            self.reset()


        def reset(self):
            self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/loader_bgnd.dmd").frames[0])
            self.text_layer = dmd.TextLayer(13, 9, self.game.fonts['tiny7'], "left", opaque=False)
            self.date_layer = dmd.TextLayer(13, 17, self.game.fonts['tiny7'], "left", opaque=False)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer, self.text_layer, self.date_layer])#set clear time


        def mode_started(self):
            self.select(1)

        def mode_tick(self):
            pass

        def select(self,number=None):
           
            if number:
                self.selection=number
            else:
                self.selection+=1
                
            if self.selection>=len(self.choices):
                self.selection=0

            self.text_layer.set_text(self.choices[self.selection],blink_frames=10)
            self.date_layer.set_text(self.dates[self.selection])

            self.game.sound.play('up_down')
            


        def sw_startButton_active(self, sw):
            #print(self.selection)
            self.game.sound.play('select')

            if self.selection == 0:
		self.launch_williams()
            elif self.selection == 1:
		self.launch_mypinballs()


        def sw_flipperLwL_active(self, sw):
            self.select()


        def sw_flipperLwR_active(self, sw):
            self.select()


        def launch_williams(self):
		self.stop_proc()

		# Call the pinmame executable to take over from here, further execution of Python code is halted.
                #os.system(r"C:\pinmame_23\pinmamep.exe ij_l7 -rp C:\pinmame_23 -window -p-roc config\machine.yaml -alpha_on_dmd -skip_disclaimer -skip_gameinfo")
                os.chdir("C:\pinmame_23");
                os.system(r"pinmamep ij_l7 -window -p-roc C:\p-roc\games\indyjones\config\machine.yaml -alpha_on_dmd -skip_disclaimer -skip_gameinfo")


		#Pinmame executable was:
		# - Quit by a delete on the keyboard
		# - Interupted by flipper buttons + start button combo

		# Reset mode & restart P-ROC / pyprocgame
		self.mode_started()
		self.restart_proc()


	def launch_mypinballs(self):
		self.stop_proc()

		# Import and run the startup script, further execution of this script is halted until the run_loop is stopped.
		import game
		game.main()

		# Reset mode & restart P-ROC / pyprocgame
		self.mode_started()
		self.restart_proc()


        def stop_proc(self):

                self.game.sound.stop_music()
		self.game.end_run_loop()
		while len(self.game.dmd.frame_handlers) > 0:
			del self.game.dmd.frame_handlers[0]
		del self.game.proc

	def restart_proc(self):
		self.game.proc = self.game.create_pinproc()
		self.game.proc.reset(1)
		self.game.load_config(self.game.yamlpath)
		#self.game.enable_flippers(True)
		self.game.dmd.frame_handlers.append(self.game.proc.dmd_draw)
		self.game.dmd.frame_handlers.append(self.game.set_last_frame)
		self.game.run_loop()