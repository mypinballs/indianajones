# Streets Of Cairo Game Mode

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random

from procgame import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

#locale.setlocale(locale.LC_ALL, 'en_GB')
class ModeScoreLayer(dmd.TextLayer):
	def __init__(self, x, y, font,mode, justify="center", opaque=False):
		super(ModeScoreLayer, self).__init__(x, y, font,justify)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()

#mpc animation layer for sprites
class SpriteLayer(dmd.AnimatedLayer):

        dot_type=None
        
        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=1, frames=None, x=0,y=-4,dot_type=None):
		super(SpriteLayer, self).__init__(opaque,x,y,dot_type)
                self.target_x = x-44
                self.target_y = y
                self.dot_type = dot_type
                self.composite_op = "blacksrc"

                self.hold = hold
		self.repeat = repeat
		if frames == None:
			self.frames = list()
		else:
			self.frames = frames

		self.frame_time = frame_time # Number of frames each frame should be displayed for before moving to the next.
		self.frame_time_counter = self.frame_time

		self.frame_listeners = []

		self.reset()

	def next_frame(self):

		frame = super(SpriteLayer, self).next_frame()
                
		if frame:
			if self.dot_type == 1:
				for x in range(128):
					for y in range(32):
						color = frame.get_dot(x,y)
						if color == 5: # These are the same dots as in dot_type 2, so we remove them by letting blacksrc hide them. Possibly this could be an additional tint in other animations?
							frame.set_dot(x,y,0) # Ideally this should be set to alpha 0%
						elif color == 15:
							# These are the highlights of the monkeys face, they should remain white
							pass
			elif self.dot_type == 2:
				for x in range(128):
					for y in range(32):
						color = frame.get_dot(x,y)
						if color == 5:
							frame.set_dot(x,y,1) # Ideally this should be 0 at alpha 100% if we could use blendmode alpha. Now we use 1 to come as close to black as possible.
						elif color == 15:
							#These are the hightlights of the monkeys body, tone them down a little.
							frame.set_dot(x,y,7)

		return frame


class Streets_Of_Cairo(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Streets_Of_Cairo, self).__init__(game, priority)

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen setup
            self.timer = int(self.game.user_settings['Gameplay (Feature)']['Streets Of Cairo Timer'])
            print("Monkey Brains Timer is:"+str(self.timer))

            self.score_layer = ModeScoreLayer(128/2, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(128/2, 5, self.game.fonts['23x12'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
#            self.sprite_data_layers = []
#            self.sprite_layer = dmd.layers.GroupedLayer(128,32, self.sprite_data_layers)
#            self.sprite_layer.composite_op ="blacksrc"

            #sound setup
            self.game.sound.register_music('soc_background_play', music_path+"streets_of_cairo.aiff")
            self.game.sound.register_sound('soc_marrion_0', sound_path+"soc_jingle.aiff")
            self.game.sound.register_sound('soc_marrion_1', speech_path+"show_lady_good_time.aiff")
            self.game.sound.register_sound('soc_s0', speech_path+"cairo_city_of_the_living.aiff")
            self.game.sound.register_sound('soc_s1', speech_path+"oh_shit.aiff")
            self.game.sound.register_sound('soc_s2', sound_path+"monkey_chirp.aiff")
            self.game.sound.register_sound('soc_s3', sound_path+"monkey_scream_1.aiff")
            self.game.sound.register_sound('soc_s4', sound_path+"swipe_1.aiff")
            self.game.sound.register_sound('soc_s5', sound_path+"swipe_2.aiff")

            #self.game.sound.register_sound('soc_gun_shot', sound_path+"gun_shot_deep.aiff")

            #lamps setup
            self.lamps = ['leftLoop','rightLoop','leftRampArrow','rightRampArrow']
            
            self.reset()


        def reset(self):
            #var setup
            self.count = 0
            self.position = [1,0,0,0]
            self.marrion_posn = 0
            self.score_value_boost = 1000000
            self.score_value_start = 10000000
            self.score_value_bonus = 2000000
            self.score_value_dual = 20000000
            self.dual_completed = 0
            self.dual_enabled = False


        def load_scene_anim(self,count,found,posn):

            #set the scene number to load depending on shots made
            y=0
            x=30*posn

            self.scene_anim = "dmd/streets_of_cairo_scene_"+str(found)+".dmd"
            anim = dmd.Animation().load(game_path+self.scene_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=2)
            self.scene_layer.add_frame_listener(-1,self.award_score)

            if found==1:
                 self.scene_layer.add_frame_listener(-1, self.load_dual_anim)
            else:
                self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)

            self.layer = self.scene_layer

        def load_bgnd_anim(self):
            self.bgnd_anim = "dmd/streets_of_cairo_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])

            
        def load_dual_anim(self):
            #set mode flag
            self.dual_enabled = True

            #load animation
            self.bgnd_anim = "dmd/streets_of_cairo_dual.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.timer_layer,self.info_layer,self.award_layer])

            #play speech & sounds
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=1)
            self.cancel_delayed('monkey_chirp_delay')
            self.dual_swipe(1)

        def load_completed_anim(self):

            self.dual_completed=1
            
            self.bgnd_anim = "dmd/streets_of_cairo_dual_completed.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,frame_time=6)
            self.bgnd_layer.add_frame_listener(-1,self.award_score)
            #call the mode select end scene sequence here
            self.bgnd_layer.add_frame_listener(-1, self.mode_select.end_scene)
            self.bgnd_layer.add_frame_listener(-1, self.eject_ball)
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.timer_layer,self.info_layer,self.award_layer])

            #play sounds
            self.game.sound.play('gun_shot')

        def eject_ball(self):
            #create eject delay
            self.delay(name='eject_delay', event_type=None, delay=2, handler=self.mode_select.eject_ball)


        def create_monkey_sprite(self,data=None,delay=None):
            
            x=data[0]  #horizontal position of sprite
            frame_num=data[1] #sprite frame to load

            if delay:
                self.delay(name='create_sprite_layer', event_type=None, delay=delay, handler=self.create_monkey_sprite, param=data)
            else:
                monkey_frames = dmd.Animation().load("dmd/soc_monkey_moves.dmd").frames

                even_frames = monkey_frames[0::2] # This layer gets the even frames
                odd_frames = monkey_frames[1::2] # This layer gets the uneven frames


                self.sprite_data1 = SpriteLayer(frames=[even_frames[frame_num]], opaque=False, hold=False, repeat=True, x=x, dot_type=1)
                self.sprite_data2 = SpriteLayer(frames=[odd_frames[frame_num]], opaque=False, hold=False, repeat=True, x=x, dot_type=2)
                #self.sprite_data1 = dmd.AnimatedLayer(frames=[monkey1_frames], opaque=False, hold=False, repeat=True)
                #self.sprite_data2 = dmd.AnimatedLayer(frames=[monkey2_frames], opaque=False, hold=False, repeat=True)

                self.sprite_data_layers = []
                self.sprite_data_layers += [self.sprite_data2]
                self.sprite_data_layers += [self.sprite_data1]

                self.sprite_layer = dmd.layers.GroupedLayer(128,32, self.sprite_data_layers)
                self.sprite_layer.composite_op ="blacksrc"
                #print("sprite created")

                self.bgnd_anim = "dmd/streets_of_cairo_bgnd.dmd"
                anim = dmd.Animation().load(game_path+self.bgnd_anim)
                self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=2)
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


            

        def move_monkey(self):
            #create posn for monkey based on shot to complete mode
            for i in range(len(self.position)):
                if self.position[i]==1:
                    self.marrion_posn = i
            #print(marrion_posn)

            posn = 0

            delay=0
            self.create_monkey_sprite([posn,5])
            delay+=1
            
            #move full right and stop

            #turn
            self.create_monkey_sprite([posn+(32*0),4],delay)
            delay+=0.3

            #move
            for i in range(1,4):
                self.create_monkey_sprite([posn+(32*i),2],delay)
                delay+=0.1
                self.create_monkey_sprite([posn+(32*i),3],delay)
                delay+=0.1
                #print(i)

            #sit
            self.create_monkey_sprite([posn+(32*3),5],delay)
            delay+=1



            #move full left and stop

            #turn
            self.create_monkey_sprite([posn+(32*3),6],delay)
            delay+=0.3

#            self.create_monkey_sprite([posn+(32*2),0],delay)
#            delay+=0.1
#            self.create_monkey_sprite([posn+(32*2),1],delay)
#            delay+=0.1
#
#            self.create_monkey_sprite([posn+(32*1),0],delay)
#            delay+=0.1
#            self.create_monkey_sprite([posn+(32*1),1],delay)
#            delay+=0.1
#
#            self.create_monkey_sprite([posn+(32*0),0],delay)
#            delay+=0.1
#            self.create_monkey_sprite([posn+(32*0),1],delay)
#            delay+=0.1

            #move
            for i in range(3,-1,-1):
                self.create_monkey_sprite([posn+(32*i),0],delay)
                delay+=0.1
                self.create_monkey_sprite([posn+(32*i),1],delay)
                delay+=0.1

                if i==self.marrion_posn:
                    for k in range(8):
                        self.create_monkey_sprite([posn+(32*self.marrion_posn),5],delay)
                        delay+=0.1
                        self.create_monkey_sprite([posn+(32*self.marrion_posn),7],delay)
                        delay+=0.1
                    self.voice_call(3)
                    self.create_monkey_sprite([posn+(32*self.marrion_posn),6],delay)
                    
                #print(i)

            #sit
            self.create_monkey_sprite([posn+(32*0),5],delay)

            

            

        def mode_started(self):
            #load player stats
            self.baskets_searched = self.game.get_player_stats('soc_baskets_searched');

            #shuffle marrion position
            random.shuffle(self.position)
            
            #setup additonal layers
            self.timer_layer = dmd.TimerLayer(0, -1, self.game.fonts['07x5'],self.timer,"left")
            self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS TO FIND MARRION",blink_frames=1000)

            #load animation
            self.move_monkey()
            #self.load_bgnd_anim()
            
            #start mode music, speech & sounds
            self.game.sound.play_music('soc_background_play', loops=-1)
            self.delay(name='mode_speech_delay', event_type=None, delay=0.5, handler=self.voice_call, param=self.count)
            #self.monkey_chirp(3)

            #open gates
            self.open_gates('left')
            self.open_gates('right')

            #update_lamps
            self.update_lamps()

        def mode_stopped(self):
            #save player stats

            self.baskets_searched+=self.count
            self.game.set_player_stats('soc_baskets_searched',self.baskets_searched)

            score_value = (self.score_value_start*self.count)+(self.score_value_dual*self.dual_completed)
            self.game.set_player_stats('streets_of_cairo_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)


            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')
            self.cancel_delayed('monkey_chirp_delay')
            self.cancel_delayed('dual_swipe_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #close gates
            self.close_gates('left')
            self.close_gates('right')

            #reset lamps
            self.reset_lamps()

        def mode_tick(self):
            pass


        def open_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.pulse(0)
            elif side=='right':
                 self.game.coils.leftControlGate.pulse(0)

        def close_gates(self,side):
            if side=='left':
                 self.game.coils.rightControlGate.disable()
            elif side=='right':
                 self.game.coils.leftControlGate.disable()

        def voice_call(self,count,delay=None,label="soc_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

        def monkey_chirp(self,delay=None):
            #method that repeats a series of sound/voice calls at a preset time until cancelled
            start_delay = 0.5
            interval = 0.2
            self.voice_call(2,start_delay)
            self.voice_call(2,start_delay+interval)
            
            self.delay(name='monkey_chirp_delay', event_type=None, delay=delay, handler=self.monkey_chirp, param=delay)

        def dual_swipe(self,delay):
            #method that repeats a series of sound/voice calls at a preset time until cancelled
            start_delay = 0
            interval = 0.2
            self.voice_call(4,start_delay)
            self.voice_call(4,start_delay+interval)
            self.voice_call(5,start_delay+(interval*2))

            self.delay(name='dual_swipe_delay', event_type=None, delay=delay, handler=self.dual_swipe, param=delay)



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)
     

        def mode_progression(self,num):

            self.count+=1
            
            #load progression animation
            if self.position[num]==1:
                self.load_scene_anim(self.count,1,num)
            else:
                self.load_scene_anim(self.count,0,num)
            
            #play sound
            #self.game.sound.play('marrion_'+self.position[num])
            self.voice_call(self.position[num],label="soc_marrion_")


        def award_score(self,score_value=0):

            if self.dual_completed==1:
                score_value = self.score_value_dual
            else:
                score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=3,color=dmd.MAGENTA)
            self.game.score(score_value)

        def mode_bonus(self):
            self.game.score(score_value_bonus)
            


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def clear(self):
            self.layer = None

    
        def sw_leftLoopTop_active(self, sw):
            if self.game.switches.rightLoopTop.time_since_change()>1:
                self.mode_progression(0)

            return procgame.game.SwitchStop

        def sw_leftRampMade_active(self, sw):
            self.mode_progression(1)

            return procgame.game.SwitchStop

        def sw_rightRampMade_active(self, sw):
            self.mode_progression(2)

            return procgame.game.SwitchStop

        def sw_rightLoopTop_active(self, sw):
            if self.game.switches.leftLoopTop.time_since_change()>1:
                self.mode_progression(3)

            return procgame.game.SwitchStop

        def sw_leftEject_active(self, sw):
            if self.dual_enabled:
                self.load_completed_anim()
                return procgame.game.SwitchStop
            #else:
                #self.mode_bonus()

            

        def sw_gunTrigger_active(self, sw):
            if self.dual_enabled:
                self.score_value_dual =  self.score_value_dual/10
                self.load_completed_anim()

            return procgame.game.SwitchStop
 