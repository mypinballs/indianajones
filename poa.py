import procgame
import locale
from procgame import *
from mini_playfield import *

base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class POA(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(POA, self).__init__(game, priority)
		self.text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['07x5'], "center")
		self.award_layer = dmd.TextLayer(128/2, 17, self.game.fonts['num_14x10'], "center")
		self.layer = dmd.GroupedLayer(128, 32, [self.text_layer, self.award_layer])
		self.time = 0
		self.awards = ['award1','award2']

                #setup global mode variables
                self.lamps=['adventureA','adventureD','adventureV','adventureE1','adventureN','adventureT','adventureU','adventureR','adventureE2']

                self.full_sets_completed = 0
                self.pit_value = 20000000

                #setup sound calls
		self.game.sound.register_sound('good shot', speech_path+'take_the_poa.aiff')
		self.game.sound.register_sound('target', sound_path+'adv_target_1.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_2.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_3.aiff')
                self.game.sound.register_sound('target', sound_path+'adv_target_4.aiff')

                #setup mode links
                self.mini_playfield = Mini_Playfield(game, priority+1)


                #reset variables
                self.reset()

        def reset(self):
                self.letters_spotted = 0
                self.adventureA_lit = False
                self.adventureD_lit = False
                self.adventureV_lit = False
                self.adventureE1_lit = False
                self.adventureN_lit = False
                self.adventureT_lit = False
                self.adventureU_lit = False
                self.adventureR_lit = False
                self.adventureE2_lit = False
                self.set1 = False
                self.set2 = False
                self.set3 = False
                self.reset_lamps()
	
	def mode_started(self):
                print("POA Mode Started")
                pass

        def spell_adventure(self):
                bgnd = dmd.FrameLayer(opaque=False,frame=dmd.Animation().load(game_path+'dmd/adventure_bgnd.dmd').frames[0])     

                A = dmd.FrameLayer(opaque=False)
                D = dmd.FrameLayer(opaque=False)
                V = dmd.FrameLayer(opaque=False)
                E1 = dmd.FrameLayer(opaque=False)
                N = dmd.FrameLayer(opaque=False)
                T = dmd.FrameLayer(opaque=False)
                U = dmd.FrameLayer(opaque=False)
                R = dmd.FrameLayer(opaque=False)
                E2 = dmd.FrameLayer(opaque=False)
                completed = dmd.FrameLayer(opaque=False)

                if self.adventureA_lit:
                     A.frame = dmd.Animation().load(game_path+'dmd/adventure_A.dmd').frames[0]
                     A.composite_op = "blacksrc"
                if self.adventureD_lit:
                     D.frame = dmd.Animation().load(game_path+'dmd/adventure_D.dmd').frames[0]
                     D.composite_op = "blacksrc"
                if self.adventureV_lit:
                     V.frame = dmd.Animation().load(game_path+'dmd/adventure_V.dmd').frames[0]
                     V.composite_op = "blacksrc"
                if self.adventureE1_lit:
                     E1.frame = dmd.Animation().load(game_path+'dmd/adventure_E1.dmd').frames[0]
                     E1.composite_op = "blacksrc"
                if self.adventureN_lit:
                     N.frame = dmd.Animation().load(game_path+'dmd/adventure_N.dmd').frames[0]
                     N.composite_op = "blacksrc"
                if self.adventureT_lit:
                     T.frame = dmd.Animation().load(game_path+'dmd/adventure_T.dmd').frames[0]
                     T.composite_op = "blacksrc"
                if self.adventureU_lit:
                     U.frame = dmd.Animation().load(game_path+'dmd/adventure_U.dmd').frames[0]
                     U.composite_op = "blacksrc"
                if self.adventureR_lit:
                     R.frame = dmd.Animation().load(game_path+'dmd/adventure_R.dmd').frames[0]
                     R.composite_op = "blacksrc"
                if self.adventureE2_lit:
                     E2.frame = dmd.Animation().load(game_path+'dmd/adventure_E2.dmd').frames[0]
                     E2.composite_op = "blacksrc"

                if (self.adventureA_lit and self.adventureD_lit==True and self.adventureV_lit==True):
                    self.set1=True

                if (self.adventureE1_lit==True and self.adventureN_lit==True and self.adventureT_lit==True):
                    self.set2=True

                if (self.adventureU_lit==True and self.adventureR_lit==True and self.adventureE2_lit==True):
                    self.set3=True

                adventure_layer = dmd.GroupedLayer(128, 32, [bgnd,A,D,V,E1,N,T,U,R,E2,completed])
                self.layer = adventure_layer
                

                if self.letters_spotted==9:

                    completed.frame = dmd.Animation().load(game_path+'dmd/adventure_completed.dmd').frames[0]
                    completed.composite_op = "blacksrc"

                    self.delay(name='poa_ready', event_type=None, delay=2, handler=self.poa_ready)

                    
                else:
                    
                    self.delay(name='clear', event_type=None, delay=2, handler=self.clear)

                print(self.letters_spotted)
                


        def poa_ready(self):
            
            #setup poa flasher
            #if self.game.switches.topPost.is_inactive():
            self.game.coils.flasherPOA.schedule(0x33333, cycle_seconds=1, now=False)

            #setup divertor for ball to mini playfield
            #if self.game.switches.rightRampEntrance.is_active():
            self.game.coils.divertorMain.pulse(50)
            self.game.coils.divertorHold.pulse(0)

            #set no. sets of letters completed
            self.full_sets_completed +=1
            print(self.full_sets_completed)

            if self.full_sets_completed==1:
                #run poa ready grpahics
                anim = dmd.Animation().load(game_path+"dmd/poa_lit.dmd")
                animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,frame_time=2)
                #animation_layer.add_frame_listener(-1,xxx)
                self.layer = animation_layer
                
            #display new pit value if second or more time around
            else:
                self.pit_value +=10000000
                pit_layer = dmd.TextLayer(128/2, 11, self.game.fonts['07x5'], "center", opaque=False).set_text("PIT VALUE INCREASED",1)
                self.layer = pit_layer



            #self.delay(name='clear', event_type=None, delay=2, handler=self.clear)

            #reset variables
            self.reset()


        def continue_adventure(self):
            #setup timer for mode length
            self.adventure_continue_timer = self.game.user_settings['Gameplay (Feature)']['Adventure Continue Timer']
            self.delay(name='adventure_continue_timer', event_type=None, delay=adventure_continue_timer, handler=self.adventure_expired)



	def begin(self):
                #self.reset_lamps()
                pass

        def update_lamps(self):
            flags=[self.adventureA_lit,self.adventureD_lit,self.adventureV_lit,self.adventureE1_lit,self.adventureN_lit,self.adventureT_lit,self.adventureU_lit,self.adventureR_lit,self.adventureE2_lit]
            for i in range(len(flags)):
                if flags[i]:
                    self.game.effects.drive_lamp(self.lamps[i],'on')
                else:
                    self.game.effects.drive_lamp(self.lamps[i],'medium')


	def reset_lamps(self):
                for i in range(len(self.lamps)):
                    self.game.effects.drive_lamp(self.lamps[i],'medium')

                    
        def clear(self):
            self.layer=None

	def adventure_expired(self):
		# Manually cancel the delay in case this function was called
		# externally.
		self.cancel_delayed('adventure_continue_timer')
                self.game.coils.divertorHold.disable
                self.reset_lamps()

#		self.game.modes.remove(self)

        def letter_hit(self,toggle,lamp_name):
            if toggle == False:
                self.game.effects.drive_lamp(lamp_name,'smarton')
                self.letters_spotted +=1
                toggle=True;
                print("adventure lamp lit: %s "%(lamp_name))
                print("toggle value: %s "%(str(toggle)))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()

        def light_next_in_sequence(self):

            if self.adventureA_lit==False:
                self.sw_adventureA_active(self)
            elif self.adventureD_lit==False:
                self.sw_adventureD_active(self)
            elif self.adventureV_lit==False:
                self.sw_adventureV_active(self)
            elif self.adventureE1_lit==False:
                self.sw_dropTargetLeft_active(self)
            elif self.adventureN_lit==False:
                self.sw_dropTargetMiddle_active(self)
            elif self.adventureT_lit==False:
                self.sw_dropTargetRight_active(self)
            elif self.adventureU_lit==False:
                self.sw_adventureU_active(self)
            elif self.adventureR_lit==False:
                self.sw_adventureR_active(self)
            elif self.adventureE2_lit==False:
                self.sw_adventureE2_active(self)


	def sw_adventureA_active(self, sw):
            #self.letter_hit(self.adventureA_lit,'adventureA')
            if self.adventureA_lit == False:
                lamp_name ='adventureA'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureA_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)
                if self.set1==True:
                    self.light_next_in_sequence()

            self.game.sound.play("target")
            self.spell_adventure()
        
        def sw_adventureD_active(self, sw):

            if self.adventureD_lit == False:
                lamp_name ='adventureD'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureD_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_adventureV_active(self, sw):
            if self.adventureV_lit == False:
                lamp_name ='adventureV'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureV_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_dropTargetLeft_active(self, sw):
            if self.adventureE1_lit == False:
                lamp_name ='adventureE1'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureE1_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
        
        def sw_dropTargetMiddle_active(self, sw):
            if self.adventureN_lit == False:
                lamp_name ='adventureN'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureN_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_dropTargetRight_active(self, sw):
            if self.adventureT_lit == False:
                lamp_name ='adventureT'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureT_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_adventureU_active(self, sw):
            if self.adventureU_lit == False:
                lamp_name ='adventureU'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureU_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_adventureR_active(self, sw):
            if self.adventureR_lit == False:
                lamp_name ='adventureR'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureR_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()
                
        def sw_adventureE2_active(self, sw):
            if self.adventureE2_lit == False:
                lamp_name ='adventureE2'
                self.game.drive_lamp(lamp_name,'on')
                self.letters_spotted +=1
                self.adventureE2_lit=True;
                print("adventure lamp lit: %s "%(lamp_name))
                self.game.score(500000)
            else:
                self.game.score(100000)

            self.game.sound.play("target")
            self.spell_adventure()

        def sw_topPost_active_for_500ms(self, sw):
            self.game.coils.flasherPOA.disable()
            self.game.modes.add(self.mini_playfield)




