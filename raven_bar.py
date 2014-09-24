# Raven Bar Video Mode
# Jim
# September 2014

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
		super(ModeScoreLayer, self).__init__(x, y, font,mode)
		self.mode = mode
                
	def next_frame(self):
		"""docstring for next_frame"""
		# update score data from game mode
		self.mode.update_score()

		return super(ModeScoreLayer, self).next_frame()


##mpc animation layer for sprites
#class SpriteLayer(dmd.AnimatedLayer):
#
#        dot_type=None
#
#        def __init__(self, opaque=False, hold=True, repeat=False, frame_time=24, frames=None, x=0,y=0,dot_type=None):
#		super(SpriteLayer, self).__init__(opaque,x,y,dot_type)
#                self.target_x = x
#                self.target_y = y
#                self.dot_type = dot_type
#                self.composite_op = "blacksrc"
#
#                self.hold = hold
#		self.repeat = repeat
#		if frames == None:
#			self.frames = list()
#		else:
#			self.frames = frames
#
#		self.frame_time = frame_time # Number of frames each frame should be displayed for before moving to the next.
#		self.frame_time_counter = self.frame_time
#
#		self.frame_listeners = []
#
#		self.reset()
#
#	def next_frame(self):
#
#		frame = super(SpriteLayer, self).next_frame()
#
#		if frame:
#			if self.dot_type == 1:
#				for x in range(128):
#					for y in range(32):
#						color = frame.get_dot(x,y)
#						if color == 5: # These are the same dots as in dot_type 2, so we remove them by letting blacksrc hide them. Possibly this could be an additional tint in other animations?
#							frame.set_dot(x,y,0) # Ideally this should be set to alpha 0%
#						elif color == 15:
#							# These are the highlights of the monkeys face, they should remain white
#							pass
#                                                elif color == 10:
#                                                        frame.set_dot(x,y,12)
#			elif self.dot_type == 2:
#				for x in range(128):
#					for y in range(32):
#						color = frame.get_dot(x,y)
#						if color == 5:
#							frame.set_dot(x,y,1) # Ideally this should be 0 at alpha 100% if we could use blendmode alpha. Now we use 1 to come as close to black as possible.
#						elif color == 15:
#							#These are the hightlights of the monkeys body, tone them down a little.
#							frame.set_dot(x,y,6)
#                                                        
#		return frame
            

class Raven_Bar(game.Mode):

	def __init__(self, game, priority,mode_select):
            super(Raven_Bar, self).__init__(game, priority)

            self.log = logging.getLogger('ij.raven_bar')

            #setup link back to mode_select mode
            self.mode_select = mode_select

            #screen seetup
            #self.score_layer = ModeScoreLayer(0, -1, self.game.fonts['07x5'], self)
            self.award_layer = dmd.TextLayer(0, 0, self.game.fonts['7x4'], "center", opaque=False)
            self.award_layer.composite_op ="blacksrc"
            #self.bgnd_layer = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer1 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer2 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer3 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.sprite_layer4 = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False) #extra sprite layer invoked as mode progresses
            self.medallion_layer = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
            self.extra_ball_layer = dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)

            #sound setup
            self.game.sound.register_music('rvb_bgnd_play', music_path+"raven_bar.aiff")
            self.game.sound.register_sound('rvb_badguy_hit', sound_path+"gun_shot4.aiff")
            self.game.sound.register_sound('rvb_indy_hit', sound_path+"gun_shot3.aiff")
            self.game.sound.register_sound('rvb_medallion', sound_path+"medallion_collected.aiff")
            self.game.sound.register_sound('rvb_level_completed', sound_path+"werewolfs_completed.aiff")
            self.game.sound.register_sound('rvb_s0', speech_path+"shoot_them_both.aiff")
            self.game.sound.register_sound('rvb_s1', speech_path+"my_medallion.aiff")
           

            #lamps setup
            self.lamps = []
            


        def reset(self):
            #load stored vars from settings
            #self.timer = int(self.game.user_settings['Gameplay (Feature)']['Tank Chase Timer'])
            #self.log.debug("Tank Chase Timer is:"+str(self.timer))

            #var setup
            self.instructions_completed = False
            self.count = 0
            self.level = self.game.user_settings['Gameplay (Feature)']['Raven Bar Level Start'] #1
            self.lives = self.game.user_settings['Gameplay (Feature)']['Raven Bar Lives'] #5
            self.hits_for_medallion = self.game.user_settings['Gameplay (Feature)']['Raven Bar Hits For Medallion'] #20
            self.hits_for_eb = self.game.user_settings['Gameplay (Feature)']['Raven Bar Hits For Extra Ball'] #5
            self.hits = 0
            self.medallion_ready = False
            self.medallion_collected = False
            self.eb_ready = False
            self.eb_collected = False
            self.show_animated_scores_for_hits = self.game.user_settings['Gameplay (Feature)']['Raven Bar Animate Scores For Hits'] #true
            self.badguy_posns = [-40,-32,-24,-16,-8,0,8,16,40,48]  #storage for the xposn of bad guys, randomly created?
            self.badguy_standing_posns = [-56,24] 
            self.indy_shot_flag = False
            self.bar_position = 0
            self.badguy_id = 0
            self.badguy_data = []

            #setup score values - add settings here instead
            self.score_value_start = 1000000
            self.score_value_boost = 5000
            self.score_value_extra = 10000
            self.medallion_value = 15000000 
     
        
        def create_bar_bgnd(self,xposn=0,blinded=False):
            if blinded:
                bgnd_anim = dmd.Animation().load(game_path+"dmd/raven_bar_bgnd_blinded.dmd") 
            else:
                bgnd_anim = dmd.Animation().load(game_path+"dmd/raven_bar_bgnd.dmd") 
           
            x = xposn
            frame_layers = []
            
            for i in range(len(bgnd_anim.frames)):
                frame = dmd.FrameLayer(frame=bgnd_anim.frames[i])
                frame.target_x = x
                frame_layers += [frame]
                
                x+=128
                
            self.bgnd_layer = dmd.layers.GroupedLayer(256,32, frame_layers)
            #adjust the positioning
            self.bgnd_layer.target_x-=64

            self.log.debug("bar background created")


        def create_gun(self,xposn=0,fire=False):
            if fire:
                gun_sprites = dmd.Animation().load("dmd/raven_bar_sprites_gun_fire.dmd").frames
            else:
                gun_sprites = dmd.Animation().load("dmd/raven_bar_sprites_gun.dmd").frames
            
            #set the sprite posn
            x = xposn
            y = 7
            
            self.gun_layer = dmd.AnimatedLayer(frames=gun_sprites,hold=True,frame_time=6)
            self.gun_layer.target_x=x
            self.gun_layer.target_y=y
            self.gun_layer.composite_op ="blacksrc"

            self.log.debug("indy gun created")
            

        def create_standing_badguy(self, posn_id=0, layer=None):
            badguy_sprites = dmd.Animation().load("dmd/raven_bar_sprites_badguy_standing.dmd").frames

            #set the sprite posn
            x= self.badguy_standing_posns[posn_id]
            y = 0
            
            #create the layer
            self.sprite_layer1 = dmd.AnimatedLayer(frames=badguy_sprites,hold=True,frame_time=6)
            self.sprite_layer1.target_x=x
            self.sprite_layer1.target_y=y
            self.sprite_layer1.add_frame_listener(-2,self.indy_hit)
            self.sprite_layer1.composite_op ="blacksrc"
            
            #create tracking data
            self.badguy_id+=1
            data = {'id':self.badguy_id,'posn_id':posn_id,'xposn':x,'layer':1,'type':'standing'}
            self.badguy_data.append(data)
            self.log.debug('badguy data: %s',self.badguy_data)

            self.log.debug("standing badguy created at posn:%s",x)
            
            
        def create_badguy(self,posn_id=0,layer=0):
            badguy_sprites = dmd.Animation().load("dmd/raven_bar_sprites_badguy.dmd").frames

            #set the sprite posn
            x = self.badguy_posns[posn_id]
            y =-9
            
            #create the layer
            sprite_layer = dmd.AnimatedLayer(frames=badguy_sprites,hold=True,frame_time=6)
            sprite_layer.target_x=x
            sprite_layer.target_y=y
            sprite_layer.add_frame_listener(-2,self.indy_hit)
            sprite_layer.composite_op ="blacksrc"
            
            if layer==2:
                self.sprite_layer2 = sprite_layer
            elif layer==3:
                self.sprite_layer3 = sprite_layer

            #create tracking data
            self.badguy_id+=1
            data = {'id':self.badguy_id,'posn_id':posn_id,'xposn':x,'layer':layer,'type':'std'}
            self.badguy_data.append(data)
            self.log.debug('badguy data: %s',self.badguy_data)
            
            self.log.debug("badguy created at posn:%s",x)
            
        
        def create_standing_badguy_shot(self, posn_id=0, layer=None):
            badguy_sprites = dmd.Animation().load("dmd/raven_bar_sprites_badguy_standing_shot.dmd").frames

            self.log.debug('posn_id:%s',posn_id)
            #set the sprite posn
            x= self.badguy_standing_posns[posn_id]+self.bar_position
            y = 0
                            
            #create the layer
            sprite_layer = dmd.AnimatedLayer(frames=badguy_sprites,hold=False,frame_time=6)
            sprite_layer.target_x=x
            sprite_layer.target_y=y
            
            self.sprite_layer1 = dmd.layers.GroupedLayer(128,32, [sprite_layer,self.award_layer])
            self.sprite_layer1.composite_op ="blacksrc"
            
            self.play_award_anim([x+64,12])
            
            self.log.debug("standing badguy shot sprite created at posn:%s",x)
            
            
        def create_badguy_shot(self,posn_id=0,layer=0):
            badguy_sprites = dmd.Animation().load("dmd/raven_bar_sprites_badguy_shot.dmd").frames

            #set the sprite posn
            x = self.badguy_posns[posn_id]+self.bar_position
            y =-9
            
            #create the layer
            sprite_layer = dmd.AnimatedLayer(frames=badguy_sprites,hold=False,frame_time=6)
            sprite_layer.target_x=x
            sprite_layer.target_y=y
            
            if layer==2:
                self.sprite_layer2 = dmd.layers.GroupedLayer(128,32, [sprite_layer,self.award_layer])
                self.sprite_layer2.composite_op ="blacksrc"
            elif layer==3:
                self.sprite_layer3 = dmd.layers.GroupedLayer(128,32, [sprite_layer,self.award_layer])
                self.sprite_layer3.composite_op ="blacksrc"

            self.play_award_anim([x+64,12])
            
            self.log.debug("badguy shot sprite created at posn:%s",x)
            
            
        def create_medallion(self,posn_id=0):
            
            medallion_sprites = dmd.Animation().load("dmd/raven_bar_sprites_medallion.dmd").frames

            #create the layer
            self.medallion_layer = dmd.FrameLayer(frame=medallion_sprites[0])
            #set the sprite posn
            self.medallion_layer.target_x=self.badguy_posns[posn_id]
            self.medallion_layer.target_y=-9
            self.medallion_layer.composite_op ="blacksrc"
            
            #create tracking data
            self.badguy_id+=1
            data = {'id':self.badguy_id,'posn_id':posn_id,'xposn':x,'layer':0,'type':'medallion'}
            self.badguy_data.append(data)
            self.log.debug('badguy data: %s',self.badguy_data)

            self.log.debug("medallion created")
            self.medallion_ready = True
        
        
        def create_eb(self,posn_id=0):
            
            extra_sprites = dmd.Animation().load(game_path+"dmd/raven_bar_sprites_extras.dmd").frames
            
            #create the layer
            self.extra_ball_layer = dmd.FrameLayer(frame=extra_sprites[0])
            #set the sprite posn
            self.extra_ball_layer.target_x = self.badguy_posns[posn_id]
            self.extra_ball_layer.target_y = -7
            self.extra_ball_layer.composite_op ="blacksrc"
            
            #create tracking data
            self.badguy_id+=1
            data = {'id':self.badguy_id,'posn_id':posn_id,'xposn':self.badguy_posns[posn_id],'layer':0,'type':'eb'}
            self.badguy_data.append(data)
            self.log.debug('sprite data: %s',self.badguy_data)

            self.log.debug("extra ball created")
            self.eb_ready = True
            
            
        def create_extras_shot(self,posn_id=0):
            sprites = dmd.Animation().load("dmd/raven_bar_sprites_extras_shot.dmd").frames

            #set the sprite posn
            x = self.badguy_posns[posn_id]+self.bar_position
            y =-9
            
            #create the layer
            self.extra_ball_layer = dmd.AnimatedLayer(frames=sprites,hold=False,frame_time=6)
            #set the sprite posn
            self.extra_ball_layer.target_x = x
            self.extra_ball_layer.target_y = y
            self.extra_ball_layer.composite_op ="blacksrc"
            
            self.log.debug("extras shot sprite created at posn:%s",x)
        
        
        def play_medallion_animation(self):
            if self.medallion_layer.target_y>-14:
                self.medallion_layer.target_y-=2
                self.delay(name='animate_medaillion_delay',delay=0.1,handler=self.play_medallion_animation)
                
        def indy_hit(self):
            
            if not self.indy_shot_flag:
                self.create_bar_bgnd(xposn=self.bar_position,blinded=True)
                self.indy_shot_flag = True
                self.update_lives(-1)
                self.game.sound.play('rvb_indy_hit')
                self.delay(name='shot_delay',delay=0.5,handler=self.indy_hit)
                
            else:
                self.create_bar_bgnd(xposn=self.bar_position,blinded=False)
                self.indy_shot_flag = False
                self.cancel_delayed('shot_delay')
                
                #end mode if lives have run out
                if self.lives==0:
                    self.end_scene_delay(1)
            
            if not self.medallion_collected:
                self.layer = dmd.GroupedLayer(256, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.sprite_layer4,self.medallion_layer,self.extra_ball_layer,self.gun_layer,self.lives_info_layer,self.enemy_info_layer])

     
        def start_badguys(self):

            x1 = random.randint(0,1)
            x2 = random.randint(0,9)
            x3 = random.randint(0,9)

            self.create_standing_badguy(posn_id=x1,layer=self.sprite_layer1)
            self.create_badguy(posn_id=x2,layer=2)
            self.create_badguy(posn_id=x3,layer=3)
            
        
        def next_badguy(self,layer):
            #create new badguy
            new_posn_id = random.randint(0,9)
            
            #create better randomness for standing bad guys as mode progresses
            if layer==1:
                layer=4
            elif layer==4 and self.hits%6==0:
                layer=1
                new_posn_id = random.randint(0,1)
                
            self.create_badguy(posn_id=new_posn_id,layer=layer)
            #adjust the positioning after creation to be inline with current movements
            sprite_layers =[self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.sprite_layer4]
            sprite_layers[layer-1].target_x+=self.bar_position
            
            #create the medallion once allowed
            if self.hits>=self.hits_for_medallion and not self.medallion_ready:
                id = random.randint(0,9)
                self.create_medallion(posn_id=id)
                #adjust the positioning after creation to be inline with current movements
                self.medallion_layer.target_x+=self.bar_position
            
            #create the extra ball once allowed
            if self.hits>=self.hits_for_eb and not self.eb_ready:
                id = random.randint(0,9)
                self.create_eb(posn_id=id)
                #adjust the positioning after creation to be inline with current movements
                self.extra_ball_layer.target_x+=self.bar_position
                
            if not self.medallion_collected:
                #update layers
                self.layer = dmd.GroupedLayer(256, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.sprite_layer4,self.medallion_layer,self.extra_ball_layer,self.gun_layer,self.lives_info_layer,self.enemy_info_layer])


        def shoot_badguy(self,id):
            self.log.debug('ID of badguy is:%s',id)

            text_offset = 64
            #wolf_sprite_offset = 37

            self.create_gun(fire=True)
            self.game.sound.play('rvb_badguy_hit')
            
            xposn = self.badguy_data[id]['xposn']+self.bar_position
            posn_id = self.badguy_data[id]['posn_id']
            layer = self.badguy_data[id]['layer']
            type = self.badguy_data[id]['type']
            
            self.log.debug("sprite type :%s",type)
            
            if type=='medallion':
                self.completed()
            elif type=='eb':
                self.create_extras_shot(posn_id=posn_id)
                self.collect_eb()
                self.badguy_data.pop(id) # remove the item from list
            else:
                self.update_enemies(1)
            
                if layer==1:
                    #self.sprite_layer1 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
                    self.create_standing_badguy_shot(posn_id=posn_id,layer=layer)
                elif layer==2:
                    #self.sprite_layer2 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
                    self.create_badguy_shot(posn_id=posn_id,layer=layer)
                elif layer==3:
                    #self.sprite_layer3 =dmd.AnimatedLayer(frames=None,hold=True,opaque=False,repeat=False)
                    self.create_badguy_shot(posn_id=posn_id,layer=layer)

                #self.play_award_anim([xposn+text_offset,12])

                self.badguy_data.pop(id) # remove the item from list
            
                self.delay(name='next_badguy_delay',delay=1,handler=self.next_badguy,param=layer)
                

        def play_award_anim(self,posn_data):
            
            self.award_layer.x=posn_data[0]
            self.award_layer.y=posn_data[1]
            self.award_layer.set_text(locale.format("%d", self.score_value_start, True),color=dmd.RED)

            y_posn_moved = posn_data[1]-2
            
            if posn_data[1]>4:
                self.delay(name='award_anim_repeat', delay=0.1, handler=self.play_award_anim,param=[posn_data[0],y_posn_moved])
            else:
                self.cancel_delayed('award_anim_repeat')
                #reset layer
                #self.award_layer = dmd.TextLayer(0, 0, self.game.fonts['7x4'], "center", opaque=False)
                self.award_layer.set_text("")


        def collect_eb(self):
            self.game.sound.stop('rvb_badguy_hit')
            self.game.extra_ball.collect(play_anim=False)
            
            
        def uncompleted(self):
            pass
            
        def completed(self):
            #play speech
            self.game.sound.stop('rvb_badguy_hit')
            self.voice_call(1)
            
            #update tracking var
            self.medallion_collected = True
            #stop movement if active
            self.cancel_delayed('move_repeat')
            
            self.delay(name='queue_completed_part1',delay=1,handler=self.completed_part1)
            
        def completed_part1(self): #animated medallion section
            self.game.sound.play('rvb_medallion')
            #play animation
            self.play_medallion_animation()
            #queue next part of completion
            self.delay(name='queue_completed_part2',delay=1.2,handler=self.completed_part2)
                
                
        def completed_part2(self):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])

            #set text layers
            title_layer = dmd.TextLayer(64, 2, self.game.fonts['8x6'], "center", opaque=False)
            award_layer = dmd.TextLayer(64, 12, self.game.fonts['num_09Bx7'], "center", opaque=False)
            info_layer = dmd.TextLayer(64, 24, self.game.fonts['7x4'], "center", opaque=False)

            #title_layer.composite_op ="blacksrc"
            #award_layer.composite_op ="blacksrc"
            #info_layer.composite_op ="blacksrc"

            title_layer.set_text("Medallion Found",color=dmd.BROWN)
            award_layer.set_text(locale.format("%d", self.medallion_value, True),color=dmd.GREEN)
            info_layer.set_text('Level '.upper()+str(self.level)+'. '+str(self.hits)+" Bad Guys Hit".upper()+"="+locale.format("%d", self.hits*self.score_value_start, True),color=dmd.PURPLE)

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,award_layer,info_layer])

            self.log.debug('completed running')
            #queue the end of scene cleanup
            self.cancel_delayed('scene_cleanup')
            self.delay(name='scene_cleanup', event_type=None, delay=4, handler=self.mode_select.end_scene)


        def end_scene_delay(self,timer):
            self.delay(name='scene_cleanup', event_type=None, delay=timer, handler=self.mode_select.end_scene)

        def update_lives(self,value=0):
            self.lives+=value
            self.lives_info_layer = dmd.TextLayer(45,23,self.game.fonts['7x4'], "right", opaque=False)
            self.lives_info_layer.set_text(str(self.lives)+' Lives'.upper(),color=dmd.GREEN)
            
        def update_enemies(self,value=0):
            self.hits+=value
            self.enemy_info_layer = dmd.TextLayer(70,23,self.game.fonts['7x4'], "left", opaque=False)
            self.enemy_info_layer.set_text('Enemies Hit '.upper()+str(self.hits),color=dmd.PURPLE)
            

        def load_main_anim(self,x_posn=0,y_posn=0,delay=None):

            self.instructions_completed = True

            #update player info
            self.update_lives()
            self.update_enemies()

            
            #create the bar
            self.create_bar_bgnd(xposn=self.bar_position)
            #create gun
            self.create_gun()
            #add the bad guy sprites
            self.start_badguys()

            self.layer = dmd.GroupedLayer(256, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.sprite_layer4,self.medallion_layer,self.extra_ball_layer,self.gun_layer,self.lives_info_layer,self.enemy_info_layer])

                    
        def move(self,dirn):
            amount=0
            if dirn==0 and self.bar_position<64:
                amount=+8
            elif dirn==1 and self.bar_position>-64:
                amount=-8

            if amount!=0:
                self.bar_position+=amount
                self.bgnd_layer.target_x+=amount 
                self.move_bad_guy(self.sprite_layer1,amount)
                self.move_bad_guy(self.sprite_layer2,amount)
                self.move_bad_guy(self.sprite_layer3,amount)
                
                if self.medallion_ready:
                    self.move_bad_guy(self.medallion_layer,amount)
                if self.eb_ready:
                    self.move_bad_guy(self.extra_ball_layer,amount)
                    
                self.layer = dmd.GroupedLayer(256, 32, [self.bgnd_layer,self.sprite_layer1,self.sprite_layer2,self.sprite_layer3,self.sprite_layer4,self.medallion_layer,self.extra_ball_layer,self.gun_layer,self.lives_info_layer,self.enemy_info_layer])

                self.log.debug('Bar Position:%s',self.bar_position)
                

        def move_bad_guy(self,layer,amount):
            layer.target_x +=amount
            
            for i in range(len(self.badguy_data)):
                #if self.badguy_data[i]['posn_id']==layer.target_x or (layer.target_x>=self.badguy_data[i]['posn_id']-4 and layer.target_x<=self.badguy_data[i]['posn_id']+4):
                if self.badguy_data[i]['xposn']==(self.bar_position*-1):
                    self.shoot_badguy(i)
                    break
                    
            
        def instructions(self):
            bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+"dmd/mode_bonus_bgnd.dmd").frames[0])

            #set text layers
            title_layer = dmd.TextLayer(64, 0, self.game.fonts['8x6'], "center", opaque=False)
            text_layer1 = dmd.TextLayer(64, 10, self.game.fonts['7x4'], "center", opaque=False)
            text_layer2 = dmd.TextLayer(64, 17, self.game.fonts['7x4'], "center", opaque=False)
            text_layer3 = dmd.TextLayer(64, 25, self.game.fonts['7x4'], "center", opaque=False)
            
            #title_layer.composite_op ="blacksrc"
            #text_layer1.composite_op ="blacksrc"
            #text_layer2.composite_op ="blacksrc"
            #text_layer3.composite_op ="blacksrc"
            title_layer.set_text("Level "+str(self.level),color=dmd.BROWN)
            text_layer1.set_text("Use Flippers To Aim Gun".upper(),color=dmd.YELLOW)
            text_layer2.set_text("Hit ".upper()+str(self.hits_for_medallion)+" Guys To Find Medallion".upper(),color=dmd.RED)
            text_layer3.set_text("Watch For Hidden Extras".upper(),blink_frames=4,color=dmd.ORANGE)
            

            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [bgnd_layer,title_layer,text_layer1,text_layer2,text_layer3])

            #start mode music & speech
            self.game.sound.stop_music()
            self.game.sound.play_music('rvb_bgnd_play', loops=-1)

            self.voice_call(self.count)
            
            #self.delay(name='music_delay', delay=1.5, handler=self.start_music)
            self.delay(name='start_animation_delay', delay=4, handler=self.load_main_anim)


        def start_music(self):
            self.game.sound.play_music('rvb_bgnd_play', loops=-1)
            

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

            bonus_value=0
            if self.hits>=self.hits_for_medallion:
                bonus_value+=self.medallion_value

            score_value = (self.hits*self.score_value_start)+bonus_value
                
            self.game.set_player_stats('raven_bar_score',score_value)
            self.game.set_player_stats('last_mode_score',score_value)


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


        def voice_call(self,count,delay=None,label="rvb_s"):
            if delay==None:
                self.game.sound.play_voice(label+str(count))
            else:
                self.delay(name='mode_speech_delay', event_type=None, delay=delay, handler=self.voice_call, param=count)

            #additional speech calls
            #if count==0:
            #    self.delay(name='aux_mode_speech_delay', event_type=None, delay=2, handler=self.voice_call, param=1)


        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))
     

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
            
        def move_repeat(self,dirn):
            if not self.medallion_collected:
                self.move(dirn)
                self.delay(name='move_repeat',delay=0.1,handler=lambda:self.move_repeat(dirn))

        #switch handlers
        def sw_flipperLwL_active(self, sw):

            if self.instructions_completed and not self.medallion_collected and self.lives>0:
                self.cancel_delayed('move_repeat')
                self.move_repeat(0)
               
            return procgame.game.SwitchStop

        def sw_flipperLwR_active(self, sw):

            if self.instructions_completed and not self.medallion_collected and self.lives>0:
                self.cancel_delayed('move_repeat')
                self.move_repeat(1)
                
            return procgame.game.SwitchStop
        
        def sw_flipperLwL_inactive(self, sw):
            if self.game.switches.flipperLwR.is_inactive():
                self.cancel_delayed('move_repeat')
            
        def sw_flipperLwR_inactive(self, sw):
            if self.game.switches.flipperLwL.is_inactive():
                self.cancel_delayed('move_repeat')

#        def sw_gunTrigger_active(self, sw):
#
#            if self.instructions_completed:
#                self.shoot_wolf(1)
#
#            return procgame.game.SwitchStop
        