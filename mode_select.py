# Mode Select

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random
import logging
import audits

from procgame import *
from get_the_idol import *
from streets_of_cairo import *
from well_of_souls import *
from monkey_brains import *
from steal_the_stones import *
from rope_bridge import *
from castle_grunwald import *
from tank_chase import *
from the_three_challenges import *
from choose_wisely import *
from werewolf import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Mode_Select(game.Mode):

	def __init__(self, game, priority):
            super(Mode_Select, self).__init__(game, priority)
            self.log = logging.getLogger('ij.modeSelect')

            self.name_layer = dmd.TextLayer(128/2, 6, self.game.fonts['num_09Bx7'], "center")
            self.info_layer = dmd.TextLayer(128/2, 16, self.game.fonts['07x5'], "center")
            self.info2_layer = dmd.TextLayer(128/2, 22, self.game.fonts['07x5'], "center")

            #setup sound
            self.game.sound.register_sound('scene_started', sound_path+'mode_started.aiff')
            self.game.sound.register_sound('scene_ended', sound_path+'mode_ended.aiff')

            self.name_text =''
            self.info_text =''
            self.info2_text =''

            self.lamp_list = ['getTheIdol','streetsOfCairo','wellOfSouls','ravenBar','monkeyBrains','stealTheStones','mineCart','ropeBridge','castleGrunwald','tankChase','theThreeChallenges','chooseWisely']
            self.select_list = [0,0,0,0,0,0,0,0,0,0,0,0]
            self.current_mode_num = 0
            self.choice_id =0

            #default mode bonus value
            self.mode_bonus_value = 2000000

            #default timer value
            self.timer=30

            #setup mode enabled flag from game settings
            if self.game.user_settings['Gameplay (Feature)']['Mode Start Lit']!='Off':
                self.mode_enabled = True
            else:
                self.mode_enabled = False

            self.game.set_player_stats('mode_enabled',self.mode_enabled)

            #setup mode running flag
            self.mode_running = False

            #setup game modes
            self.get_the_idol = Get_The_Idol(self.game, 80,self)
            self.streets_of_cairo = Streets_Of_Cairo(self.game, 81,self)
            self.well_of_souls = Well_Of_Souls(self.game, 82,self)
            self.raven_bar = Werewolf(self.game, 83,self)
            self.monkey_brains = Monkey_Brains(self.game, 84,self)
            self.steal_the_stones = Steal_The_Stones(self.game, 85,self)
            self.mine_cart = Choose_Wisely(self.game, 86,self)
            self.rope_bridge = Rope_Bridge(self.game, 87,self)
            self.castle_grunwald = Castle_Grunwald(self.game, 88,self)
            self.tank_chase = Tank_Chase(self.game, 89,self)
            self.the_three_challenges = The_Three_Challenges(self.game, 90,self)
            self.choose_wisely = Choose_Wisely(self.game, 91,self)

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

            #reset bonus mode tracking at ball start - no carry over
            self.game.set_player_stats('bonus_mode_tracking',[])

            #setup scene list
            self.unplayed_scenes()

        def mode_tick(self):
            pass

        def mode_stopped(self):
            #update player stats
            self.game.set_player_stats('current_mode_num',self.current_mode_num)
            self.game.set_player_stats('mode_status_tracking',self.select_list)

            #clean up any running modes
            if self.mode_running:
                #remove the active scene
                self.remove_selected_scene()
                #call the common end scene code
                self.end_scene_common(0.1)


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
            self.game.coils.leftEject.pulse()
     

        def start_scene(self):
            if self.mode_enabled and self.game.get_player_stats('multiball_running')==False and self.game.get_player_stats('quick_multiball_running')==False:

                #play sound
                self.game.sound.play("scene_started")

                if self.current_mode_num==0:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Get The Idol Timer']
                    self.name_text = 'GET THE IDOL'
                    self.info_text = 'HIT CENTER DROP TARGETS'

                elif self.current_mode_num==1:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Streets Of Cairo Timer']
                    self.name_text = 'STREETS OF CAIRO'
                    self.info_text = 'SHOOT RAMPS'
                    self.info2_text = 'TO FIND MARION'

                elif self.current_mode_num==2:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Well Of Souls Timer']
                    self.name_text = 'WELL OF SOULS'
                    self.info_text = 'SHOOT CENTER HOLE'

                elif self.current_mode_num==3:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Raven Bar Timer']
                    #self.name_text = 'RAVEN BAR'
                    #self.info_text = 'XXX'
                    self.name_text = 'Werewolf Attack!'.upper()
                    self.info_text = 'Secret Video Mode'.upper()

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
                    self.info_text = 'HIT CAPTIVE BALL'
                    self.info2_text = 'TO ESCAPE CASTLE'

                elif self.current_mode_num==9:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer']
                    self.name_text = 'TANK CHASE'
                    self.info_text = 'SHOOT LOOPS'
                    self.info2_text = 'TO DESTROY TANK'

                elif self.current_mode_num==10:
                    self.timer = self.game.user_settings['Gameplay (Feature)']['The 3 Challenges Timer']
                    self.name_text = '3 CHALLENGES'
                    self.info_text = 'GET LIT LANES ON'
                    self.info2_text = 'PATH OF ADVENTURE'

                elif self.current_mode_num==11:
                    #timer = self.game.user_settings['Gameplay (Feature)']['Choose Wisely Timer']
                    self.name_text = 'CHOOSE WISELY'
                    self.info_text = 'VIDEO MODE'

                anim = dmd.Animation().load(game_path+"dmd/start_scene.dmd")
                self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=2)
                
                self.animation_layer.add_frame_listener(-1,self.mode_text)

                self.ssd_count=0#temp fix for frame_listener multi call with held
                self.animation_layer.add_frame_listener(-1,self.scene_start_delay)


                self.layer = dmd.GroupedLayer(128, 32, [self.animation_layer,self.name_layer,self.info_layer,self.info2_layer])

                #update mode flags and player stats
                self.mode_enabled=False
                self.game.set_player_stats('mode_enabled',self.mode_enabled)
                self.mode_running = True
                self.game.set_player_stats('mode_running',self.mode_running)

                #update lamp for mode start
                self.mode_start_lamp(self.mode_enabled)

                #record audits
                audits.record_value(self,'modeStarted')
                
            elif self.mode_running:
                self.mode_bonus()
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
            self.info2_layer.set_text(self.info2_text)

        def scene_start_delay(self):
            time = 2

            if self.ssd_count==0: #make sure the following delays only get called once
                if self.current_mode_num !=2 and self.current_mode_num!=3 :#don't set timeout for these non time based modes
                    self.delay(name='scene_timeout', event_type=None, delay=self.timer, handler=self.end_scene)
                self.delay(name='scene_delay', event_type=None, delay=time, handler=self.add_selected_scene)
                if self.current_mode_num!=3 and self.current_mode_num!=6 and self.current_mode_num!=11:#don't eject ball for video modes, scene will eject it itself at end
                    self.delay(name='eject_delay', event_type=None, delay=time, handler=self.eject_ball)
                self.delay(name='clear_delay', event_type=None, delay=time, handler=self.clear)
                self.ssd_count+=1

        def cancel_timeout(self):
            self.cancel_delayed("scene_timeout")

        def end_scene(self):
            #play sound
            self.game.sound.play("scene_ended")

            #remove the active scene
            self.remove_selected_scene()

            #display mode total on screen
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/scene_ended_bgnd.dmd").frames[0])
            self.info_layer.set_text(locale.format("%d",self.game.get_player_stats('last_mode_score'),True))
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.name_layer,self.info_layer])

            #call the common end scene code
            self.end_scene_common(2)
            
        def end_scene_common(self,timer):
            #update mode completed status tracking
            self.select_list[self.current_mode_num] =1
            #set next mode to be played
            self.unplayed_scenes('right')

            #update the bonus mode tracking
            bonus_mode_tracking = self.game.get_player_stats('bonus_mode_tracking')
            bonus_mode_tracking.append({'name':self.name_text,'score':self.game.get_player_stats('last_mode_score')})
            self.game.set_player_stats('bonus_mode_tracking',bonus_mode_tracking)
            #debug
            self.log.info("bonus mode tracking:%s",bonus_mode_tracking)

            #clean up
            self.delay(name='clear_display', event_type=None, delay=timer, handler=self.pre_clear)
            self.update_lamps()

            #update mode running flag and player stats
            self.mode_running = False
            self.game.set_player_stats('mode_running',self.mode_running)
            
        def mode_bonus(self):
            timer=2
            self.game.screens.mode_bonus(timer,self.mode_bonus_value)
            self.delay(name='eject_delay', event_type=None, delay=timer, handler=self.eject_ball)

            audits.record_value(self,'modeBonus')

        def pre_clear(self):
            self.name_layer.set_text("")
            self.info_layer.set_text("")
            self.info2_layer.set_text("")
            self.clear()

        def clear(self):
            self.layer=None
            

        def sw_leftEject_active_for_500ms(self,sw):
            if self.game.get_player_stats('hof_status')!='lit':
                self.start_scene()
                #return procgame.game.SwitchStop    
           



#        def sw_leftEject_active(self,sw):
#            if self.mode_enabled:
#                return procgame.game.SwitchStop

        def sw_leftRampMade_active(self, sw):
            if not self.mode_running:
                self.move_left()

        def sw_rightRampMade_active(self, sw):
            if not self.mode_running:
                self.move_right()

        def sw_leftLoopTop_active(self, sw):
            if not self.mode_enabled and not self.mode_running:
                self.mode_enabled=True
                self.game.set_player_stats('mode_enabled',self.mode_enabled)

                self.mode_start_lamp(self.mode_enabled)

        def sw_rightLoopTop_active(self, sw):
            if not self.mode_enabled and not self.mode_running:
                self.mode_enabled=True
                self.game.set_player_stats('mode_enabled',self.mode_enabled)
                
                self.mode_start_lamp(self.mode_enabled)