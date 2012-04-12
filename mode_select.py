# Mode Select

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random

from procgame import *
from get_the_idol import *
from streets_of_cairo import *
from monkey_brains import *
from steal_the_stones import *
from castle_grunwald import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Mode_Select(game.Mode):

	def __init__(self, game, priority):
            super(Mode_Select, self).__init__(game, priority)
            self.name_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center")
            self.info_layer = dmd.TextLayer(128/2, 18, self.game.fonts['07x5'], "center")

            #setup sound
            self.game.sound.register_sound('scene_started', sound_path+'mode_started.aiff')
            self.game.sound.register_sound('scene_ended', sound_path+'mode_ended.aiff')

            self.name_text =''
            self.info_text =''

            self.lamp_list = ['getTheIdol','streetsOfCairo','wellOfSouls','ravenBar','monkeyBrains','stealTheStones','mineCart','ropeBridge','castleGrunwald','tankChase','theThreeChallenges','chooseWisely']
            self.select_list = [0,0,0,0,0,0,0,0,0,0,0,0]
            self.current_mode_num = 0
            self.choice_id =0

            #default timer value
            self.timer=30

            #set mode enabled flag from game settings
            if self.game.user_settings['Gameplay (Feature)']['Mode Start Lit']!='Off':
                self.mode_enabled = True
            else:
                self.mode_enabled = False

            self.game.set_player_stats('mode_enabled',self.mode_enabled)

            #setup game modes
            self.get_the_idol = Get_The_Idol(self.game, 80,self)
            self.streets_of_cairo = Streets_Of_Cairo(self.game, 81,self)
            self.well_of_souls = Get_The_Idol(self.game, 82,self)
            self.raven_bar = Get_The_Idol(self.game, 83,self)
            self.monkey_brains = Monkey_Brains(self.game, 84,self)
            self.steal_the_stones = Steal_The_Stones(self.game, 85,self)
            self.mine_cart = Monkey_Brains(self.game, 86,self)
            self.rope_bridge = Monkey_Brains(self.game, 87,self)
            self.castle_grunwald = Castle_Grunwald(self.game, 88,self)
            self.tank_chase = Castle_Grunwald(self.game, 89,self)
            self.the_three_challenges = Castle_Grunwald(self.game, 90,self)
            self.choose_wisely = Castle_Grunwald(self.game, 91,self)

            self.reset()

        def reset(self):
            print("Main Mode Select Started")
            self.reset_lamps()

        def reset_lamps(self):
            #loop round and turn off all lamps
            for i in range(len(self.lamp_list)):
                self.game.effects.drive_lamp(self.lamp_list[i],'off')

            self.mode_start_lamp(self.mode_enabled)

        def mode_start_lamp(self,flag):
            lamp_name ='modeStart'
            if flag:
                self.game.effects.drive_lamp(lamp_name,'medium')
            else:
                self.game.effects.drive_lamp(lamp_name,'off')


        def mode_started(self):
            #load player stats
            self.current_mode_num = self.game.get_player_stats('current_mode_num')
            self.select_list = self.game.get_player_stats('mode_status_tracking')

            #setup scene list
            self.unplayed_scenes()

        def mode_tick(self):
            pass

        def mode_stopped(self):
            #update player stats
            self.game.set_player_stats('current_mode_num',self.current_mode_num)
            self.game.set_player_stats('mode_status_tracking',self.select_list)


        def update_lamps(self):
            print("Updating Mode Lamps")

            #current mode
            self.game.effects.drive_lamp(self.lamp_list[self.current_mode_num],'medium')

            #completed modes
            for i in range(len(self.lamp_list)):
                if self.select_list[i]==1:
                    self.game.effects.drive_lamp(self.lamp_list[i],'on')

            #mode start
            self.mode_start_lamp(self.mode_enabled)


        def unplayed_scenes(self,dirn=None):

            #turn off current mode lamp
            self.game.drive_lamp(self.lamp_list[self.current_mode_num],'off')

            #create list of unplayed scene numbers
            choice_list=[]
            for i in range(len(self.select_list)):
                if self.select_list[i]==0:
                    choice_list.append(i)
           
            #adjust choice number
            if dirn=='left':
                self.choice_id -=1
            elif dirn=='right':
                self.choice_id +=1
            else:
                self.choice_id = random.randint(0, len(choice_list)-1)

            #create wrap around
            if self.choice_id>len(choice_list)-1:
                self.choice_id=0
            elif self.choice_id<0:
                self.choice_id=len(choice_list)-1

            #set new mode number
            self.current_mode_num = choice_list[self.choice_id]

            #update lamps
            self.update_lamps()

            print("mode now active:"+str(self.lamp_list[self.current_mode_num]))

           



        def move_left(self):
            
            self.unplayed_scenes('left')

            self.game.coils.flasherLeftRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherLeftRamp.disable)


        def move_right(self):
            
            self.unplayed_scenes('right')

            self.game.coils.flasherRightRamp.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
            self.delay(name='disable_flasher', event_type=None, delay=2, handler=self.game.coils.flasherRightRamp.disable)


        def eject_ball(self):
            self.game.coils.leftEject.pulse(15)
     

        def start_scene(self):
            if self.mode_enabled and self.game.get_player_stats('multiball_running')==False:

                #play sound
                self.game.sound.play("scene_started")

                if self.current_mode_num==0:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Get The Idol Timer']
                    self.name_text = 'GET THE IDOL'
                    self.info_text = 'HIT CENTER DROP TARGETS'

                elif self.current_mode_num==1:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Streets Of Cairo Timer']
                    self.name_text = 'STREETS OF CAIRO'
                    self.info_text = 'SHOOT RAMPS TO FIND MARION'

                elif self.current_mode_num==2:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Well Of Souls Timer']
                    self.name_text = 'WELL OF SOULS'
                    self.info_text = 'SHOOT CENTER HOLE'

                elif self.current_mode_num==3:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Raven Bar Timer']
                    self.name_text = 'RAVEN BAR'
                    self.info_text = 'XXX'

                elif self.current_mode_num==4:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Monkey Brains Timer']
                    self.name_text = 'MONKEY BRAINS'
                    self.info_text = 'SHOOT LIT SHOTS'

                elif self.current_mode_num==5:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Steal The Stones Timer']
                    self.name_text = 'STEAL THE STONES'
                    self.info_text = 'GET ALL LIT LANES'

                elif self.current_mode_num==6:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Mine Cart Timer']
                    self.name_text = 'MINE CART'
                    self.info_text = 'XXX'

                elif self.current_mode_num==7:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Rope Bridge Timer']
                    self.name_text = 'ROPE BRIDGE'
                    self.info_text = 'XXX'

                elif self.current_mode_num==8:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Castle Grunwald Timer']
                    self.name_text = 'CASTLE GRUNWALD'
                    self.info_text = 'HIT CAPTIVE BALL TO ESCAPE CASTLE'

                elif self.current_mode_num==9:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer']
                    self.name_text = 'TANK CHASE'
                    self.info_text = 'SHOOT LIT LOOPS'

                elif self.current_mode_num==10:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['The 3 Challenges Timer']
                    self.name_text = 'THE 3 CHALLENGES'
                    self.info_text = 'HIT CENTER DROP TARGETS'

                elif self.current_mode_num==11:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Choose Wisely Timer']
                    self.name_text = 'CHOOSE WISELY'
                    self.info_text = 'SHOOT LIT SHOT, WATCH CAREFULLY!'

                anim = dmd.Animation().load(game_path+"dmd/start_scene.dmd")
                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=2)
                
                self.animation_layer.add_frame_listener(-1,self.mode_text)

                self.ssd_count=0#temp fix for frame_listener multi call with held
                self.animation_layer.add_frame_listener(-1,self.scene_start_delay)


                self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.name_layer,self.info_layer])

                self.mode_enabled=False
            else:
                self.delay(name='eject_delay', event_type=None, delay=0.5, handler=self.eject_ball)

        def add_selected_scene(self):

            print("Adding Movie Scene Mode"+str(self.current_mode_num))
            if self.current_mode_num==0:
                self.game.modes.add(self.get_the_idol)
            elif self.current_mode_num==1:
                self.game.modes.add(self.streets_of_cairo)
            elif self.current_mode_num==2:
                self.game.modes.add(self.well_of_souls)
            elif self.current_mode_num==3:
                self.game.modes.add(self.raven_bar)
            elif self.current_mode_num==4:
                self.game.modes.add(self.monkey_brains)
            elif self.current_mode_num==5:
                self.game.modes.add(self.steal_the_stones)
            elif self.current_mode_num==6:
                self.game.modes.add(self.mine_cart)
            elif self.current_mode_num==7:
                self.game.modes.add(self.rope_bridge)
            elif self.current_mode_num==8:
                self.game.modes.add(self.castle_grunwald)
            elif self.current_mode_num==9:
                self.game.modes.add(self.tank_chase)
            elif self.current_mode_num==10:
                self.game.modes.add(self.the_three_challenges)
            elif self.current_mode_num==11:
                self.game.modes.add(self.choose_wisely)

        def remove_selected_scene(self):
            print("Removing Movie Scene Mode"+str(self.current_mode_num))
            if self.current_mode_num==0:
                self.game.modes.remove(self.get_the_idol)
            elif self.current_mode_num==1:
                self.game.modes.remove(self.streets_of_cairo)
            elif self.current_mode_num==2:
                self.game.modes.remove(self.well_of_souls)
            elif self.current_mode_num==3:
                self.game.modes.remove(self.raven_bar)
            elif self.current_mode_num==4:
                self.game.modes.remove(self.monkey_brains)
            elif self.current_mode_num==5:
                self.game.modes.remove(self.steal_the_stones)
            elif self.current_mode_num==6:
                self.game.modes.remove(self.mine_cart)
            elif self.current_mode_num==7:
                self.game.modes.remove(self.rope_bridge)
            elif self.current_mode_num==8:
                self.game.modes.remove(self.castle_grunwald)
            elif self.current_mode_num==9:
                self.game.modes.remove(self.tank_chase)
            elif self.current_mode_num==10:
                self.game.modes.remove(self.the_three_challenges)
            elif self.current_mode_num==11:
                self.game.modes.remove(self.choose_wisely)

                    
        def mode_text(self):
            self.name_layer.set_text(self.name_text)
            self.info_layer.set_text(self.info_text)

        def scene_start_delay(self):
            time = 2

            if self.ssd_count==0: #make sure the following delays only get called once
                self.delay(name='scene_timeout', event_type=None, delay=self.timer, handler=self.end_scene)
                self.delay(name='scene_delay', event_type=None, delay=time, handler=self.add_selected_scene)
                self.delay(name='eject_delay', event_type=None, delay=time, handler=self.eject_ball)
                self.delay(name='clear_delay', event_type=None, delay=time, handler=self.clear)
                self.ssd_count+=1


        def end_scene(self):
            #play sound
            self.game.sound.play("scene_ended")

            #remove the active scene
            self.remove_selected_scene()

            #display mode total on screen
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            self.info_layer.set_text(locale.format("%d",self.game.get_player_stats('last_mode_score'),True))
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.name_layer,self.info_layer])

            #update mode completed status tracking
            self.select_list[self.current_mode_num] =1

            #clean up
            self.delay(name='clear_display', event_type=None, delay=2, handler=self.clear)
            self.update_lamps()
            

        def clear(self):
            self.layer=None
            

        def sw_leftEject_active_for_500ms(self,sw):
            self.start_scene()

        def sw_leftEject_active(self,sw):
            if self.mode_enabled:
                return procgame.game.SwitchStop

        def sw_leftRampMade_active(self, sw):
            self.move_left()

        def sw_rightRampMade_active(self, sw):
            self.move_right()