# Werewolf Secret Video Mode
# Jim
# Nov 2013

import procgame
import locale
import logging
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

        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=4, frames=None, x=0,y=0,dot_type=None):
		super(SpriteLayer, self).__init__(opaque,x,y,dot_type)
                self.target_x = x
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
			for x in range(128):
                            for y in range(32):
				color = frame.get_dot(x,y)
                                if color == 5:
                                    frame.set_dot(x,y,6)
                                elif color == 10:
                                    frame.set_dot(x,y,15)
		return frame


class Minecart(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Minecart, self).__init__(game, priority)

            self.log = logging.getLogger('ij.minecart')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen seetup
            #self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(0, 0, self.game.fonts['7x4'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            self.tunnel_info_layer = dmd.TextLayer(128, -1, self.game.fonts['7x4'], "right", opaque=False)
            self.sprite_layer1 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer2 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer3 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)

            #sound setup
            self.game.sound.register_music('minecart_mode_music', music_path+"mine_cart.aiff")
            self.game.sound.register_sound('minecart_jingle', sound_path+"mine_cart_jingle.aiff")
            self.game.sound.register_sound('minecart_roll', sound_path+"mine_cart_roll.aiff")
            self.game.sound.register_sound('minecart_crash', sound_path+"mine_cart_crash.aiff")
            
            #lamps setup
            self.lamps = []


        def reset(self):
            #load stored vars from settings

            #var setup
            self.instructions_completed = False
            self.count = 0
            self.level = 1
            self.tunnels_start = int(self.game.user_settings['Gameplay (Feature)']['Mine Cart Tunnel Start'])
            self.tunnels_remaining = self.tunnels_start
            self.frame_time = 4
            
            self.barrier_posn1 =9 #default not configured value
            self.barrier_posn2 =9 #default not configured value
            self.current_posn = 1
            self.tunnel_reached = False
            self.flipper_pressed = False

            self.tunnel_value_boost = 500000
            self.tunnel_value_start = 1000000
            self.tunnel_value_bonus = 10000000
            self.score_total = 2000000
            

        def create_barrier(self,layer=0,posn=0):
            
            dmd_path = ["dmd/mine_cart_sprite_left_barrier.dmd","dmd/mine_cart_sprite_middle_barrier.dmd","dmd/mine_cart_sprite_right_barrier.dmd"]
            x_offset = [4,2,14]
            y_offset = [-3,-12,-2]
            barrier_frames = dmd.Animation().load(dmd_path[posn]).frames

            #set the sprite posn
            offset = 10
            x = x_offset[posn]
            y = y_offset[posn]

            
            if layer==1:
                self.sprite_layer1 = SpriteLayer(frames=barrier_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                #self.sprite_layer1.add_frame_listener(-1,xx)
            elif layer==2:
                self.sprite_layer2 = SpriteLayer(frames=barrier_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                #self.sprite_layer2.add_frame_listener(-1,xx)

            #update the display layer
            #self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.tunnel_info_layer,self.award_layer])


        def create_barrier_turn(self,layer=0,barrier_posn=0,current_posn=0):
            if barrier_posn==0:
                dmd_path = ["","dmd/mine_cart-left_barrier_straight_on.dmd","dmd/mine_cart-left_barrier_right_turn.dmd"]
                x_offset = [0,-16,-34]
                y_offset = [0,6,0]
            elif barrier_posn==1:
                dmd_path = ["dmd/mine_cart-mid_barrier_left_turn.dmd","","dmd/mine_cart-mid_barrier_right_turn.dmd"]
                x_offset = [40,0,-36]
                y_offset = [-2,0,-2]
            elif barrier_posn==2:
                dmd_path = ["dmd/mine_cart-right_barrier_left_turn.dmd","dmd/mine_cart-right_barrier_straight_on.dmd",""]
                x_offset = [34,36,0]
                y_offset = [0,6,0]
            
            barrier_frames = dmd.Animation().load(dmd_path[current_posn]).frames
            
            #set the sprite posn
            x = x_offset[current_posn]
            y = y_offset[current_posn]
          
            if layer==1:
                self.sprite_layer1 = SpriteLayer(frames=barrier_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                #self.sprite_layer1.add_frame_listener(-1,xx)
            elif layer==2:
                self.sprite_layer2 = SpriteLayer(frames=barrier_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                #self.sprite_layer2.add_frame_listener(-1,xx)

            #update the display layer
            #self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.tunnel_info_layer,self.award_layer])


        def create_cart(self,posn=1):
            cart_frame = dmd.Animation().load(game_path+"dmd/mine_cart_sprite_cart.dmd")
            self.cart_layer = dmd.FrameLayer(frame=cart_frame.frames[posn])
            self.cart_layer.composite_op ="blacksrc"
            self.cart_layer.target_x=7
            self.cart_layer.target_y=14
            
            
        def update_tunnel_count(self):
            self.tunnels_remaining-=1
            self.tunnel_info_layer.set_text('Tunnels '.upper()+str(self.tunnels_remaining),color=dmd.BROWN)
            
            
        def half_way(self):
            self.bgnd_anim = "dmd/mine_cart_bump.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=self.frame_time)
            self.scene_layer.add_frame_listener(-1,self.load_main_anim)
            self.layer = self.scene_layer
            
            self.game.sound.play_voice('minecart_roll')
            
            
        def completed(self):
            self.bgnd_anim = "dmd/mine_cart_bump.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=self.frame_time)
            self.scene_layer.add_frame_listener(-1,self.scene_totals)
            self.layer = self.scene_layer
            
            self.game.sound.play_voice('minecart_roll')
            
            
        def crash(self):
            #create the crash animation
            self.bgnd_anim = "dmd/mine_cart_crash.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=self.frame_time)
            self.scene_layer.add_frame_listener(-1,self.explosion)
            self.layer = self.scene_layer #dmd.GroupedLayer(128, 32, [self.scene_layer,self.award_layer])
            
            self.game.sound.play('minecart_crash')
            
            
        def explosion(self):
            #create the crash animation
            self.bgnd_anim = "dmd/mine_cart_explosion.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=self.frame_time)
            self.scene_layer.add_frame_listener(-5,self.scene_totals)

            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer])
        
            
        def scene_totals(self):
            title_layer = dmd.TextLayer(64, 2, self.game.fonts['8x6'], "center", opaque=False)
            info_layer = dmd.TextLayer(64, 12, self.game.fonts['07x5'], "center", opaque=False)
            award_layer = dmd.TextLayer(64, 20, self.game.fonts['9x7_bold'], "center", opaque=False)

            title_layer.composite_op ="blacksrc"
            award_layer.composite_op ="blacksrc"
            info_layer.composite_op ="blacksrc"
            
            title_layer.set_text(str(self.tunnels_start-self.tunnels_remaining)+" Tunnels Passed".upper(),color=dmd.CYAN)
            if self.tunnels_remaining<self.tunnels_start/2:
                info_layer.set_text("10 Million Half Way Bonus".upper(),color=dmd.YELLOW)
            award_layer.set_text(locale.format("%d",self.score_total,True),blink_frames=10,color=dmd.GREEN)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer,title_layer,info_layer,award_layer])
            
            self.end_scene_delay()


        def create_tunnel(self):
            
            self.update_tunnel_count()

            posn_data = [0,1,2]
            
            #create barriers -  choose 2 posns from the 3 available.
            #only create a second barrier after a certain number of tunnels passed
            self.barrier_posn1 = random.choice(posn_data)
            self.create_barrier(layer=1,posn=self.barrier_posn1)
            
            if self.tunnels_remaining<12:
                for i in posn_data:
                    if i==self.barrier_posn1:
                        posn_data.pop(i)
                    
                self.barrier_posn2 = random.choice(posn_data)
                self.create_barrier(layer=2,posn=self.barrier_posn2)
                
            self.log.info('Barrier Posns are:%s and %s',self.barrier_posn1,self.barrier_posn2)


        def end_scene_delay(self):
            self.delay(name='scene_cleanup', event_type=None, delay=3, handler=self.mode_select.end_scene)

            
        def load_main_anim(self,x_posn=0,y_posn=0,delay=None):

            self.instructions_completed = True

            #create bgnd
            self.bgnd_anim = "dmd/mine_cart_main.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,frame_time=self.frame_time)
            self.bgnd_layer.add_frame_listener(-1,self.choose_route)
            
            #create sprites
            self.current_posn = 1
            self.create_cart(posn=self.current_posn)
            
            self.create_tunnel()
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.cart_layer,self.sprite_layer1,self.sprite_layer2,self.tunnel_info_layer,self.award_layer])

            self.game.sound.play_voice("minecart_roll")


        def choose_route(self):
            self.tunnel_reached = True
            self.flipper_pressed = False
            
            #this is needed here as we need to check the flipper switches at this point in the process
            if self.instructions_completed and self.tunnel_reached:
                if self.game.switches.flipperLwL.is_active():
                    self.move_cart(-1)
                    self.flipper_pressed = True
                elif self.game.switches.flipperLwR.is_active():
                    self.move_cart(1)
                    self.flipper_pressed = True
            
            #auto continue if no user interaction received    
            if not self.flipper_pressed:
                #self.log.info('cart staying put')
                self.move_cart()
                
            
            
        def move_cart(self,dirn=0):
            self.current_posn+=dirn
            if self.current_posn<0:
                self.current_posn=0
            elif self.current_posn>2:
                self.current_posn=2
            
            self.log.info("Moving Cart to Posn:%s",self.current_posn)
            
            self.tunnel_reached=False
            self.flipper_pressed=False
                 
            if self.current_posn!=self.barrier_posn1 and self.current_posn !=self.barrier_posn2:
                dmd_path = ["dmd/mine_cart_turn_left.dmd","dmd/mine_cart_straight_on.dmd","dmd/mine_cart_turn_right.dmd"]
                anim = dmd.Animation().load(game_path+dmd_path[self.current_posn])
                self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=False,frame_time=self.frame_time)
                
                if self.tunnels_remaining==self.tunnels_start/2:
                    self.bgnd_layer.add_frame_listener(-1,self.half_way) 
                elif self.tunnels_remaining==0:
                    self.bgnd_layer.add_frame_listener(-1,self.completed)
                else:
                    self.bgnd_layer.add_frame_listener(-1,self.load_main_anim) #this allows the journey to continue and we repeat the whole process

                #create the barrier turns
                if self.barrier_posn1<=2:
                    self.create_barrier_turn(layer=1,barrier_posn=self.barrier_posn1,current_posn=self.current_posn)
                if self.barrier_posn2<=2:
                    self.create_barrier_turn(layer=2,barrier_posn=self.barrier_posn2,current_posn=self.current_posn) 
                    
                #update cart
                self.create_cart(posn=self.current_posn)
                    
                #update score
                self.score_total+=self.tunnel_value_start
                
                #play sound
                self.game.sound.play("minecart_roll")
                
                #update layer
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.cart_layer,self.sprite_layer1,self.sprite_layer2,self.tunnel_info_layer,self.award_layer])
            else:
                self.crash()
            
            

        def instructions(self):
            anim = dmd.Animation().load(game_path+"dmd/mine_cart_main.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,frame_time=self.frame_time)

            #set text layers
            title_layer = dmd.TextLayer(64, 0, self.game.fonts['8x6'], "center", opaque=False)
            text_layer1 = dmd.TextLayer(0, 15, self.game.fonts['07x5'], "left", opaque=False)
            text_layer2 = dmd.TextLayer(128, 15, self.game.fonts['07x5'], "right", opaque=False)
            text_layer3 = dmd.TextLayer(0, 23, self.game.fonts['07x5'], "left", opaque=False)
            text_layer4 = dmd.TextLayer(128, 23, self.game.fonts['07x5'], "right", opaque=False)
            
            title_layer.composite_op ="blacksrc"
            text_layer1.composite_op ="blacksrc"
            text_layer2.composite_op ="blacksrc"
            text_layer3.composite_op ="blacksrc"
            text_layer4.composite_op ="blacksrc"


            title_layer.set_text("Avoid     Barriers",color=dmd.CYAN)
            text_layer1.set_text("Hold".upper(),color=dmd.GREEN)
            text_layer2.set_text("Hold".upper(),color=dmd.GREEN)
            text_layer3.set_text("Left".upper(),color=dmd.GREEN)
            text_layer4.set_text("Right".upper(),color=dmd.GREEN)
            
            #create a middle barrier
            self.create_barrier(layer=1,posn=1)
            
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,self.sprite_layer1,title_layer,text_layer1,text_layer2,text_layer3,text_layer4])

            #start mode music & speech
            self.game.sound.stop_music()
            jingle_length = self.game.sound.play('minecart_jingle')
            
            self.delay(name='music_delay', delay=jingle_length-0.2, handler=self.start_music)
            self.delay(name='start_animation_delay', delay=3, handler=self.extra_instructions)


        def extra_instructions(self):

            info_layer = dmd.TextLayer(128/2, 7, self.game.fonts['8x6'], "center", opaque=False)
            info_layer.composite_op ="blacksrc"
            info_layer.set_text("Clear ".upper()+str(self.tunnels_remaining)+" To Escape".upper(),color=dmd.GREEN,seconds=1)
            bgnd_frame = dmd.Animation().load(game_path+"dmd/mine_cart_main.dmd")
            bgnd_layer= dmd.FrameLayer(frame=bgnd_frame.frames[0])
            
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,info_layer])
            self.delay(name='load_main_scene',delay=2,handler=self.load_main_anim)
            

        def start_music(self):
            self.game.sound.play_music('minecart_mode_music', loops=-1)
            

        def mode_started(self):
            #reset
            self.reset()

            #load player stats
            #self.distance = self.game.get_player_stats('tank_chase_distance')
            
            #setup additonal layers
            #self.timer_layer = dmd.TimerLayer(128, -1, self.game.fonts['07x5'],self.timer,"right")
            #self.info_layer = dmd.TextLayer(128/2, 20, self.game.fonts['07x5'], "center", opaque=False)
            #self.info_layer.set_text("SHOOT LIT SHOTS",blink_frames=1000)

            #show instructions
            self.instructions()

            #turn off flippers
            self.game.enable_flippers(enable=False)
           

            #update_lamps
            #self.update_lamps()

        def mode_stopped(self):
            #save player stats
#            current_list = self.game.get_player_stats('mode_status_tracking');
#            updated_list =current_list
#            updated_list[0]=1
#
#            self.game.set_player_stats('mode_status_tracking',updated_list)

            if self.tunnels_remaining<self.tunnels_start/2:
                self.score_total+=self.tunnel_value_bonus
                
            self.game.set_player_stats('mine_cart_score',self.score_total)
            self.game.set_player_stats('last_mode_score',self.score_total)


            #cancel speech calls
            self.cancel_delayed('mode_speech_delay')
            self.cancel_delayed('aux_mode_speech_delay')

            #reset music
            self.game.sound.stop_music()
            self.game.sound.play_music('general_play', loops=-1)

            #clear display
            self.clear()

            #turn on flippers
            self.game.enable_flippers(enable=True)

            #eject ball
            self.game.coils.leftEject.pulse()

            #reset lamps
            self.reset_lamps()


        def mode_tick(self):
            pass



        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)
     

        def award_score(self,score_value=0):
            score_value = self.score_value_start

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=1)
            self.game.score(score_value)

        def award_completed_score(self,score_value=0):
            score_value = self.score_value_completed

            self.award_layer.set_text(locale.format("%d",score_value,True),blink_frames=10,seconds=2)
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
        