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

        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=8, frames=None, x=0,y=0,dot_type=None):
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
                                    frame.set_dot(x,y,12)
		return frame


class Werewolf(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Werewolf, self).__init__(game, priority)

            self.log = logging.getLogger('ij.werewolf')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen seetup
            #self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(0, 0, self.game.fonts['7x4'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            self.sprite_layer1 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer2 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer3 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)

            #sound setup
            self.game.sound.register_music('mode_play', music_path+"werewolf.aiff")
            self.game.sound.register_sound('mode_intro', sound_path+"werewolf_intro.aiff")
            self.game.sound.register_sound('wolf_shot', sound_path+"werewolf_shot.aiff")
            self.game.sound.register_sound('wolf_move', sound_path+"werewolf_snarl.aiff")
            self.game.sound.register_sound('wolf_attack', sound_path+"werewolf_attack.aiff")
            self.game.sound.register_sound('wolf_howl', sound_path+"werewolf_howl.aiff")
            self.game.sound.register_sound('level_completed', sound_path+"werewolfs_completed.aiff")
            self.game.sound.register_sound('wolf_s0', speech_path+"children_of_the_night.aiff")
           

            #lamps setup
            self.lamps = []


        def reset(self):
            #load stored vars from settings
            #self.timer = int(self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer'])
            #self.log.info("Tank Chase Timer is:"+str(self.timer))

            #var setup
            self.instructions_completed = False
            self.count = 0
            self.level = 1
            self.wolves_start = 18
            self.wolves_remaining = self.wolves_start
            self.extra_bullets = 5
            self.bullets_remaining = self.wolves_remaining+self.extra_bullets
            self.wolf_id = 0
            self.wolf_data = []

            self.score_value_boost = 5000
            self.score_value_start = 10000
            self.score_value_completed = self.score_value_start*2
            self.score_value_extra = 10000
            self.score_total = 0

            self.wolf_bonus_value = 5000000
            self.bullet_bonus_value = 2000000

        def load_scene_anim(self,count):

            if count<4:
#                self.scene_anim = "dmd/tank_chase_scene_"+str(count)+".dmd"
#                anim = dmd.Animation().load(game_path+self.scene_anim)
#                self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=False,opaque=False,repeat=False,frame_time=2)
#                self.scene_layer.add_frame_listener(-1,self.award_score)
#                self.scene_layer.add_frame_listener(-1, self.load_bgnd_anim)
#                self.layer = self.scene_layer

                #move the horse sprite
                self.move_sprite(self.sprite_layer)
                self.award_score()
                self.game.sound.play('tc_shot_hit')

            elif count<5:
                #run rescue animation
                self.rescue_part1()
                self.award_score()
                self.voice_call(count)
            else:
                #cancel the scene timout timer
                #self.cancel_delayed("scene_timeout")
                self.mode_select.cancel_timeout()
                #run completion animation
                self.completed()
                self.voice_call(count)


        def create_werewolf(self,xposn=0,yposn=0,layer=0):
            wolf_frames = dmd.Animation().load("dmd/werewolf_sprites.dmd").frames

            #set the sprite posn
            offset = 50
            x = xposn - offset
            y = 0

            if layer==1:
                self.sprite_layer1 = SpriteLayer(frames=wolf_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                self.sprite_layer1.add_frame_listener(-1,self.wolf_bite)
            elif layer==2:
                self.sprite_layer2 = SpriteLayer(frames=wolf_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                self.sprite_layer2.add_frame_listener(-1,self.wolf_bite)
            elif layer==3:
                self.sprite_layer3 = SpriteLayer(frames=wolf_frames, opaque=False, hold=True, repeat=False, x=x,y=y)
                #load next animation part at end of this part
                self.sprite_layer3.add_frame_listener(-1,self.wolf_bite)

            #decrement the wolf counter
            self.wolves_remaining-=1
            self.wolf_info_layer.set_text('Wolves '.upper()+str(self.wolves_remaining),color=dmd.BROWN)

            #update the display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_border_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.gun_layer,self.wolf_info_layer,self.bullet_info_layer,self.award_layer])

            #inc the wolf id and update the wolf data
            self.wolf_id+=1
            data = {'id':self.wolf_id,'xposn':xposn,'layer':layer}
            self.wolf_data.append(data)
            self.log.info('wolf data: %s',self.wolf_data)

            #play sound
            self.game.sound.play('wolf_move')


        def wolf_bite(self):
            self.cancel_delayed('wolf_repeat')
            
            bgnd_frame = dmd.Animation().load(game_path+"dmd/werewolf_bgnd_die.dmd")
            self.bgnd_layer = dmd.FrameLayer(frame=bgnd_frame.frames[0])
            self.bullet_info_layer.set_text(str(self.bullets_remaining)+' Bullets'.upper(),color=dmd.RED)
            self.wolf_info_layer.set_text('Wolves '.upper()+str(self.wolves_remaining),color=dmd.RED)
            
            #update the display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_border_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.gun_layer,self.wolf_info_layer,self.bullet_info_layer,self.award_layer])

            self.game.sound.play('wolf_attack')
            self.end_scene_delay()

        def start_wolf(self):

            x1 = random.randint(20,128/2)
            x2 = random.randint(128/2,108)
            x3 = random.randint(20,108)
            x4 = random.randint(20,108)

            if self.wolves_remaining>0:
                #position wolf left half of screen then right half of screen
                if self.wolves_remaining%2==0:
                    self.create_werewolf(xposn=x1,layer=1)
                else:
                    self.create_werewolf(xposn=x2,layer=1)

                #extra wolfs
                if self.wolves_remaining<13:
                    self.create_werewolf(xposn=x3,layer=2)

                if self.wolves_remaining<8:
                    self.create_werewolf(xposn=x4,layer=3)
                
                self.delay(name='wolf_repeat', delay=3, handler=self.start_wolf)
            else:
                self.completed()
            

        def shoot_wolf(self,dirn):

            text_offset = 15
            #wolf_sprite_offset = 38

            self.game.sound.play('wolf_shot')
            self.bullets_remaining-=1
            self.bullet_info_layer.set_text(str(self.bullets_remaining)+' Bullets'.upper(),color=dmd.CYAN)

            #self.log.debug("list size is:%s",len(self.wolf_data))
            for i in range(len(self.wolf_data)): #if wolves on screen
                xposn = self.wolf_data[i]['xposn'] # get the item in list
                self.log.debug('wolf shot posn:%s, i:%s',xposn,i)
                layer = self.wolf_data[i]['layer']

                if (xposn>=60 and dirn==1) or (xposn<=68 and dirn==0): #work out if player shot in correct direction 20 pixels either side of center leeway
                    self.log.debug('wolf being shot is at:%s',xposn)
                    #update gun movement and shot
                    gun_anim = dmd.Animation().load(game_path+"dmd/wolf_gun.dmd")
                    gun_id=2
                    if dirn==0:
                        if xposn<32:
                            gun_id=0
                        elif xposn<64:
                            gun_id=1
                    elif dirn==1:
                        if xposn<96:
                            gun_id=3
                        elif xposn<128:
                            gun_id=4
                
                    self.gun_layer = dmd.FrameLayer(frame=gun_anim.frames[gun_id])
                    self.gun_layer.composite_op = "blacksrc"
                    self.delay(name='reset_gun',delay=0.5,handler=self.reset_gun_posn)
                    
                    if layer==1:
                        frame_no = self.sprite_layer1.frame_pointer
                        self.sprite_layer1 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
                    elif layer==2:
                        frame_no = self.sprite_layer2.frame_pointer
                        self.sprite_layer2 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
                    elif layer==3:
                        frame_no = self.sprite_layer3.frame_pointer
                        self.sprite_layer3 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)


                    self.play_award_anim([xposn+text_offset,15,frame_no])

                    self.wolf_data.pop(i) # remove the item from list
                    return


        def play_award_anim(self,posn_data):
            frame_posn = posn_data[2]
            #calc score
            score_multiplier = (frame_posn/3)+1 #calc a multiplier for the score based on how far the animation was played
            score = self.score_value_start*score_multiplier
            self.score_total+=score
            
            self.award_layer.x=posn_data[0]
            self.award_layer.y=posn_data[1]
            self.award_layer.set_text(locale.format("%d", score, True),color=dmd.RED)

            y_posn_moved = posn_data[1]-2
            
            if posn_data[1]>10:
                self.delay(name='award_anim_repeat', delay=0.3, handler=self.play_award_anim,param=[posn_data[0],y_posn_moved,frame_posn])
            else:
                self.award_layer.set_text('')

            #update the display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_border_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.gun_layer,self.wolf_info_layer,self.bullet_info_layer,self.award_layer])


        def reset_gun_posn(self):
            gun_anim = dmd.Animation().load(game_path+"dmd/wolf_gun.dmd")
            self.gun_layer = dmd.FrameLayer(frame=gun_anim.frames[2])
            self.gun_layer.composite_op = "blacksrc"
            
            
#        def rescue_part1(self):
#            escape_frames = dmd.Animation().load("dmd/tank_chase_jones_snr_escape.dmd").frames
#
#            #set the sprite posn
#            x = 24
#            y = -10
#
#            #remember - frames start at 0
#            even_frames = escape_frames[0::2] # This layer gets hilight frames
#            odd_frames = escape_frames[1::2] # This layer gets the low colour and mask frames
#
#            sprite_data1 = SpriteLayer(frames=even_frames, opaque=False, hold=False, repeat=False, x=x,y=y, dot_type=1)
#            sprite_data2 = SpriteLayer(frames=odd_frames, opaque=False, hold=False, repeat=False, x=x,y=y, dot_type=2)
#            #load next animation part at end of this part
#            sprite_data1.add_frame_listener(-1,self.rescue_part2)
#
#            #join the data together using group layer
#            sprite_data_layers = []
#            sprite_data_layers += [sprite_data2]
#            sprite_data_layers += [sprite_data1]
#
#            self.sprite_layer2 = dmd.layers.GroupedLayer(128,32, sprite_data_layers)
#            self.sprite_layer2.composite_op ="blacksrc"
#
#            self.log.info("jones snr escape sprite created")
#
#            #update the display layer
#            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.sprite_layer2,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])
#
#
#        def rescue_part2(self):
#            file = "dmd/tank_chase_jones_snr_horse.dmd"
#            anim = dmd.Animation().load(game_path+file)
#            self.sprite_layer2 = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False)
#            self.sprite_layer2.composite_op ="blacksrc"
#            self.sprite_layer2.target_x =24
#            self.sprite_layer2.target_y =4
#
#            #update the display layer
#            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.sprite_layer,self.sprite_layer2,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])
#
#            #setup the reverse movement of both sprites
#            self.reverse_sprite(self.sprite_layer)
#            self.reverse_sprite(self.sprite_layer2)


#        def completed(self):
#
#            #create the completion animation
#            self.bgnd_anim = "dmd/tank_chase_completed.dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            frame_time = 6
#            self.scene_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=frame_time)
#            self.scene_layer.add_frame_listener(-2*frame_time,self.award_completed_score)
#            self.scene_layer.add_frame_listener(-2*frame_time,lambda:self.game.sound.play('tc_tank_fall'))
#            self.scene_layer.add_frame_listener(-1*frame_time,lambda:self.game.sound.play('tc_tank_crash'))
#            self.scene_layer.add_frame_listener(-1,self.end_scene_delay)
#            self.layer = dmd.GroupedLayer(128, 32, [self.scene_layer,self.award_layer])


        def completed(self):
            self.game.sound.play('wolf_howl')

            anim = dmd.Animation().load(game_path+"dmd/werewolf_bgnd.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)

            #set text layers
            title_layer = dmd.TextLayer(64, 2, self.game.fonts['8x6'], "center", opaque=False)
            award_layer = dmd.TextLayer(64, 12, self.game.fonts['num_09Bx7'], "center", opaque=False)
            info_layer = dmd.TextLayer(64, 24, self.game.fonts['7x4'], "center", opaque=False)

            title_layer.composite_op ="blacksrc"
            award_layer.composite_op ="blacksrc"
            info_layer.composite_op ="blacksrc"

            title_layer.set_text("Werewolf Bonus "+str(self.level).upper(),color=dmd.RED)
            award_layer.set_text(locale.format("%d", self.wolf_bonus_value, True),color=dmd.YELLOW)
            info_layer.set_text(str(self.bullets_remaining)+" Bullets Left".upper()+"+"+locale.format("%d", self.bullet_bonus_value*self.bullets_remaining, True),color=dmd.GREEN)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,award_layer,info_layer])


            self.delay(name='scene_cleanup', event_type=None, delay=4, handler=self.mode_select.end_scene)


        def end_scene_delay(self):
            self.delay(name='scene_cleanup', event_type=None, delay=2, handler=self.mode_select.end_scene)


#        def load_bgnd_anim(self):
#            self.bgnd_anim = "dmd/werewolf_bgnd.dmd"
#            anim = dmd.Animation().load(game_path+self.bgnd_anim)
#            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
#            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_layer,self.timer_layer,self.info_layer,self.award_layer])


        def load_main_anim(self,x_posn=0,y_posn=0,delay=None):

            self.instructions_completed = True

            self.bgnd_anim = "dmd/werewolf_bgnd.dmd"
            anim = dmd.Animation().load(game_path+self.bgnd_anim)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False,repeat=True,frame_time=6)
            
            #set all items to blank initially
            score_border_frame = dmd.Animation().load(game_path+"dmd/werewolf_score_border.dmd")
            self.score_border_layer = dmd.FrameLayer(frame=score_border_frame.frames[0])
            self.score_border_layer.composite_op ="blacksrc"

            gun_anim = dmd.Animation().load(game_path+"dmd/wolf_gun.dmd")
            self.gun_layer = dmd.FrameLayer(frame=gun_anim.frames[2])
            self.gun_layer.composite_op ="blacksrc"

            self.bullet_info_layer = dmd.TextLayer(0, -1, self.game.fonts['7x4'], "left", opaque=False)
            self.bullet_info_layer.set_text(str(self.bullets_remaining)+' Bullets'.upper(),color=dmd.CYAN)
            
            self.wolf_info_layer = dmd.TextLayer(128, -1, self.game.fonts['7x4'], "right", opaque=False)
            self.wolf_info_layer.set_text('Wolves '.upper()+str(self.wolves_remaining),color=dmd.BROWN)
            
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.score_border_layer,self.gun_layer,self.wolf_info_layer,self.bullet_info_layer,self.award_layer])

            #add the wolf sprites
            self.start_wolf()


        def move_sprite(self,layer):
            layer.target_x +=2
            
            self.delay(name='move_sprite_forward',delay=0.2,handler=lambda:self.move_sprite(layer))

            if layer.target_x%22==0:
                self.cancel_delayed('move_sprite_forward')

        def reverse_sprite(self,layer,callback=None):
            layer.target_x -=5

            self.delay(name='move_sprite_back',delay=0.2,handler=lambda:self.reverse_sprite(layer))

            if layer.target_x<-80:
                self.cancel_delayed('move_sprite_back')
                #if callback:
                    #callback()

        def instructions(self):
            anim = dmd.Animation().load(game_path+"dmd/werewolf_splash_bgnd.dmd")
            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,opaque=False)

            #set text layers
            title_layer = dmd.TextLayer(64, 0, self.game.fonts['8x6'], "center", opaque=False)
            text_layer1 = dmd.TextLayer(64, 10, self.game.fonts['7x4'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(64, 17, self.game.fonts['7x4'], "center", opaque=False)
            text_layer3 = dmd.TextLayer(64, 26, self.game.fonts['7x4'], "center", opaque=False)
            
            title_layer.composite_op ="blacksrc"
            text_layer1.composite_op ="blacksrc"
            text_layer2.composite_op ="blacksrc"
            text_layer3.composite_op ="blacksrc"

            title_layer.set_text("Video Wave "+str(self.level).upper(),color=dmd.RED)
            text_layer1.set_text("Left Flipper Shoots Left".upper(),color=dmd.CYAN)
            text_layer2.set_text("Right Flipper Shoots Right".upper(),color=dmd.CYAN)
            text_layer3.set_text("5 Extra Bullets".upper(),blink_frames=4,color=dmd.GREEN)
            

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,text_layer1,text_layer2,text_layer3])

            #start mode music & speech
            self.game.sound.stop_music()
            self.game.sound.play('mode_intro')

            self.voice_call(self.count)
            
            self.delay(name='music_delay', delay=2.5, handler=self.start_music)
            self.delay(name='start_animation_delay', delay=8, handler=self.load_main_anim)



        def start_music(self):
            self.game.sound.play_music('mode_play', loops=-1)
            

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


            #score_value = (self.wolves_start-self.wolves_remaining)*self.score_value_start
            if self.wolves_remaining==0:
                self.score_total+=self.wolf_bonus_value
                self.score_total+=self.bullet_bonus_value*self.bullets_remaining
                
            self.game.set_player_stats('werewolf_score',self.score_total)
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


        def voice_call(self,count,delay=None,label="wolf_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            if count==0:
                self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True),color=dmd.YELLOW)
     

        def mode_progression(self):

            self.count+=1

            #load progression animation
            #self.delay(name='scene_anim_delay', event_type=None, delay=2, handler=self.load_scene_anim, param=self.count)

            
            self.load_scene_anim(self.count)


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


        #switch handlers
        def sw_flipperLwL_active(self, sw):

            if self.instructions_completed:
                self.shoot_wolf(0)

            return procgame.game.SwitchStop

        def sw_flipperLwR_active(self, sw):

            if self.instructions_completed:
                self.shoot_wolf(1)

            return procgame.game.SwitchStop

        def sw_gunTrigger_active(self, sw):

            if self.instructions_completed:
                self.shoot_wolf(1)

            return procgame.game.SwitchStop
        