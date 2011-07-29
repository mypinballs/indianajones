# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *
import random
from hand_of_fate import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Indy_Lanes(game.Mode):

	def __init__(self, game, priority):
            super(Indy_Lanes, self).__init__(game, priority)

            self.hof = Hand_Of_Fate(self.game, priority+1)
            self.game.modes.add(self.hof)


            self.bonus_layer = dmd.TextLayer(90, 1, self.game.fonts['num_09Bx7'], "center", opaque=False)
            self.loop_layer = dmd.TextLayer(90, 24, self.game.fonts['6x6_bold'], "center", opaque=False)

            self.game.sound.register_sound('lane_unlit', sound_path+"top_lane_unlit.aiff")
            self.game.sound.register_sound('lane_lit', sound_path+"top_lane_lit.aiff")
            self.game.sound.register_sound('lane_fanfare', sound_path+"top_lane_ff.aiff")

            self.game.sound.register_sound('shorty', speech_path+"shorty_intro.aiff")
            self.game.sound.register_sound('willie', speech_path+"willie_intro.aiff")
            self.game.sound.register_sound('sallah', speech_path+"sallah_intro.aiff")
            self.game.sound.register_sound('marrion', speech_path+"marrion_intro.aiff")
            self.game.sound.register_sound('drJones', speech_path+"dr_jones_intro.aiff")


            self.lane_flag = [False,False,False,False]
            self.lamps = ['indyI','indyN','indyD','indyY']
           
            #setup friend collection order
            self.friends = ['marrion','willie','sallah','shorty','drJones']
            shuffle(self.friends)

            self.friends_collected = 0 #ps
            self.friend_dmd_image =""
            self.friend_sound_call = ""
            self.marrion = False
            self.willie = False
            self.sallah = False
            self.shorty = False
            self.dr_jones = False

            self.bonusx = self.game.get_player_stats('bonus_x') #ps
            self.loop_value =self.game.get_player_stats('loop_value') #ps
            self.loop_base_value = 3000000
            self.loop_increment_value = 1000000
            self.lane_unlit_value = 50000
            self.lane_lit_value = 10000
            self.reset()


        def reset(self):
            self.letters_spotted = 0
            self.lane_flag = [False,False,False,False]
            self.reset_lamps()

        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def completed(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'superfast')


        def mode_started(self):
            print("INDY Lanes Mode Started")
            pass

        def mode_tick(self):
            pass


        def update_lamps(self):
            print("Updating INDY lane Lamps")
            for i in range(len(self.lamps)):
                if self.lane_flag[i]:
                    self.game.effects.drive_lamp(self.lamps[i],'on')

            print("Updating Friend Lamps")
            friend_flags = [self.marrion,self.willie,self.sallah,self.shorty,self.dr_jones]
            for i in range(len(friend_flags)):
                if friend_flags[i]:
                    self.game.effects.drive_lamp(self.lamps[self.friends[i]],'medium')


        def clear(self):
            self.layer = None


        def spell_indy(self):
            if self.letters_spotted ==4:

                if self.friends_collected <len(self.friends):
                    #increase bonus x
                    if self.bonusx >=2:
                        self.bonusx +=2
                    else:
                         self.bonusx +=1
                         
                    self.game.set_player_stats('bonus_x',self.bonusx)
                    print("bonus x "+str(self.bonusx))

                     #add a friend
                    self.add_friend()
                    #set loop value
                    self.loop_value=self.loop_base_value+(self.bonusx*self.loop_increment_value)

                    #load bgnd image layer
                    #anim = dmd.Animation().load(game_path+self.friend_dmd_image)
                    #self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames)
                    self.bgnd_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+self.friend_dmd_image).frames[0])

                    #set text layers
                    self.bonus_layer.set_text("BONUS X"+str(self.bonusx),seconds=2)
                    self.loop_layer.set_text(locale.format("%d", self.loop_value,True),seconds=2)
                    #set display layer
                    self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer, self.bonus_layer, self.loop_layer])#set clear time
                    #set layer clear time
                    self.delay(name='clear', event_type=None, delay=2, handler=self.clear)

                

                if self.bonusx ==8:
                    self.delay(name='bonus_text', event_type=None, delay=2, handler=self.extra_ball_lit)
                elif self.bonusx ==10:
                    self.delay(name='bonus_text', event_type=None, delay=2, handler=self.max_bonus)
                 
                #light hof inlane lights - should we call hof mode instead to do this????
                self.hof.ready()

                #flash all lamps when completed then reset after delay  
                self.completed()
                self.delay(name='reset_lanes', event_type=None, delay=1.5, handler=self.reset)


        def extra_ball_lit(self):
            self.game.extra_ball.lit()

        def max_bonus(self):
            max_bonus_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
            max_bonus_layer.set_text(str(self.bonusx)+"X MAXIMUM BONUS",1.5,10)
            self.layer = max_bonus_layer

        def add_friend(self):
            flag = [self.marrion,self.willie,self.sallah,self.shorty,self.dr_jones]

            if flag[self.friends_collected]==False:
                self.game.effects.drive_lamp(self.friends[self.friends_collected],'medium')
                flag[self.friends_collected] = True
                self.friend_dmd_image = "dmd/"+self.friends[self.friends_collected]+".dmd"

                time = self.game.sound.play_voice('lane_fanfare')
		self.delay(name='intro_speech', event_type=None, delay=time+0.5, handler=self.friend_voice_call)
                #self.game.sound.play_voice(self.friends[self.friends_collected])
                
                
        def friend_voice_call(self):
            self.game.sound.play_voice(self.friends[self.friends_collected])
            #up the count by 1 to get the next friend in the sequence
            self.friends_collected +=1


        def lanes(self,id):
            if self.lane_flag[id] == False:
                
                self.letters_spotted +=1
                self.lane_flag[id]=True;
                #print("indy lamp lit: %s "%(self.lamps[id]))
                self.game.score(self.lane_unlit_value)
                
                #play sounds
                if self.letters_spotted ==4:
                    self.game.sound.play('lane_fanfare')
                else:
                    self.game.sound.play('lane_unlit')
                    self.game.effects.drive_lamp(self.lamps[id],'smarton')

            else:
                self.game.score(self.lane_lit_value)
                #play sounds
                self.game.sound.play('lane_lit')

            self.spell_indy()
            print(self.lane_flag)
            print(self.letters_spotted)



        def sw_indyI_active(self, sw):
            self.lanes(0)

        def sw_indyN_active(self, sw):
            self.lanes(1)

        def sw_indyD_active(self, sw):
            self.lanes(2)

        def sw_indyY_active(self, sw):
            self.lanes(3)


        def lane_change(self,direction):
            list = ['indyI','indyN','indyD','indyY']
            flag_orig = self.lane_flag #[self.indyI_lit,self.indyN_lit,self.indyD_lit,self.indyY_lit]
            flag_new = [False,False,False,False] #[self.indyI_lit,self.indyN_lit,self.indyD_lit,self.indyY_lit]
            carry = False
            j=0

            if direction=='left':
                start = 0
                end = len(list)
                inc =1
            elif direction=='right':
                start = len(list)-1
                end = -1
                inc =-1

            for i in range(start,end,inc):
                if flag_orig[i]:
                    
                    if direction=='left':
                        j=i-1
                        if j<0:
                            j=3
                            carry = True
                    elif direction=='right':
                        j=i+1
                        if j>3:
                            j=0
                            carry = True

                    flag_new[i] = False
                    flag_new[j]= True

                    self.game.effects.drive_lamp(list[i],'off')
                    self.game.effects.drive_lamp(list[j],'on')

            #update the carry index if required
            if carry and direction=='left':
                flag_new[3]= True
                self.game.effects.drive_lamp(list[3],'on')
            elif carry and direction=='right':
                flag_new[0]= True
                self.game.effects.drive_lamp(list[0],'on')


            self.lane_flag=flag_new
            print(self.lane_flag)


        def sw_flipperLwL_active(self, sw):
            self.lane_change('left')


        def sw_flipperLwR_active(self, sw):
            self.lane_change('right')

