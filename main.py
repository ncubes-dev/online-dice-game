
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.uix.screenmanager import ScreenManager , Screen
from kivy.clock import mainthread, Clock
from kivy.core.audio import SoundLoader 
import socket
import threading
import random


"""
Awaiting draw condition text and handle other errors like a disconnection both server and clients
"""
class MainInterface(ScreenManager):
    dice=StringProperty( )
    image=StringProperty( )
    message=StringProperty( )
    state=StringProperty( )
    score1=NumericProperty(0)
    score2=NumericProperty(0)
    counter=NumericProperty(0)
    moves=DictProperty({})
    player1=True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.loop=True
    def roll(self):
        if self.player1:
            dice_faces=['1.jpeg', '6.jpeg','2.png', '5.jpeg' , '3.jpg', '4.jpeg']
            dice_roll_sound=SoundLoader.load("roll.WAV")
            dice_roll_sound.volume=1
            dice_roll_sound.play()
            self.image=random.choice(dice_faces) 
            self.moves['you']=self.image
            self.send_msg(self.image)
            self.player1=False
        else:
            pass




    def send_msg(self, *args):
        self.client.send(f"{self.image}".encode("utf-8"))

    
    def receive(self):
       
       # print('receive called')
        while self.loop:
            try:
                self.message=self.client.recv(1024).decode("utf-8")
                if self.message!=self.image and self.message!='reset':
                    self.moves['challenger']=self.message
                if self.message=='reset':
                    self.reset() 
                    

                self.counter+=0
                self.updater()
                self.counter+=1
               
                
                if self.counter==2:
                    Clock.schedule_once(self.results, 2)
            except (ConnectionResetError) as e:
                pass
    @mainthread   
    def updater(self): 
        self.dice=self.message
        
    @mainthread
    def results(self, dt):
        try:
            if self.moves['you']>self.moves['challenger']:
                self.state='WIN' 
            elif self.moves['you']<self.moves['challenger']:
                self.state='LOSE' 
            elif self.moves['you']==self.moves['challenger']:
                self.state='DRAW'
        except:
            self.state='DRAW'
        
        self.current='3'


    def synchro_reset(self):
        self.client.send('reset'.encode("utf-8"))
        
    

        
    @mainthread
    def reset(self):
        print('reset method called') 
        self.counter=0
        self.current='game_screen'
        self.moves.clear()
        self.dice=''
        self.message=''
        self.image=''
        self.player1=True
        #self.dice=' '



    def connect_to_server(self):
        if self.ids.text_input.text!="":
            self.client.connect((self.ids.text_input.text, 5050))
            message=self.client.recv(1024).decode("utf-8")
            if message=="game":
                self.client.send(self.ids.text_input.text.encode("utf-8"))
                thread=threading.Thread(target=self.receive , daemon=True)
                thread.start()

        
class MainApp(App):
    def on_stop(self):
        self.root.client.close()
        self.root.loop=False

MainApp().run()
