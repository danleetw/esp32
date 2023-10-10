# De BV6LC 73
import sys
import machine
from machine import Pin, TouchPad , Timer

import time
import os
import utime

class KEYBOARD():
    #  Read Keyboard information
    def __init__(self):
        self.key_list={39:0, 35:0, 34:0, 36:0, 12:1, 13:1}
        self.UP_KEY=39
        self.DOWN_KEY=35
        self.LEFT_KEY=34
        self.RIGHT_KEY=36
        self.A_KEY=12
        self.A_KEY_1=36 
        
        self.B_KEY=13
        self.B_KEY_1=34
        
        self.key_status = dict()
        self.key_type = dict()
        
        self.key_last_10_status=dict()
        self.key_lastpress = dict()
        
        # setting keyboard Press / Touch type
        for key in self.key_list:
          self.key_status[key] = 0
          self.key_type[key]=self.key_list.get(key)
          
        print("鍵盤檢查服務啟動 v2023.10.06 ...######")
    
    
    def check(self, timer):
    #   鍵盤檢查  
        # 逐一檢查
        for pin, type in self.key_type.items():
            if type==0: #Key Pin Type
                value = Pin(pin, Pin.IN,Pin.PULL_DOWN).value() ^ 1
                if self.key_status[pin]!=value:
                  self.key_status[pin]=value
            elif type==1: # Touch Pad
                touch_pin = TouchPad(Pin(pin, mode=Pin.IN))
                touch_value=touch_pin.read()
                if touch_value<281 :   # Low 145 High 418
                  value=1
                else:
                  value=0
                if self.key_status[pin]!=value:
                  self.key_status[pin]=value
            

class MORSE_INDICATE():
  #  Morse LED & Sound
  
  def __init__(self,kb):
      self.init=True
      
      self.kb=kb
      self.WPM=25
      self.Tone_length=int(60 / (self.WPM) / 26 *1000 ) # 1 WPM= PARIS (Around 26 di/dash)
      
      self.Di_length=1
      self.Da_length=3
      self.After_word_length=7
      
      
      self.di=False #   .
      self.da=False #   -
      self.dida_end_in=0 # Di/Dash Ending Time

      # Next avaiable Time
      self.next_key_in=utime.ticks_add(time.ticks_ms(), 1 )
      
      self.last_key=0 # Rolltaing DA/DI when press DA/DI together 

      self.Led_Di = machine.Pin(17 , machine.Pin.OUT)
      self.Led_Da = machine.Pin(16 , machine.Pin.OUT)
      
      self.Buzzer = machine.Pin(4 , machine.Pin.OUT)
      self.buzzer_sw=False
      
      self.checking=False
      
      print("Morse Code LED/Buzzer fucntion start v2023.10.10_1 ...######")
      #print("Tone_Length=",self.Tone_length )
      
  def check(self, timer):    
      if self.checking:
         return
      else:
         self.checking=True   
      # Control between key and key 
      if utime.ticks_diff( time.ticks_ms(),self.next_key_in ) >=0:  

        #print("Next Key OK")
        if (self.buzzer_sw==False) and (self.kb.key_status[self.kb.A_KEY]==1 or self.kb.key_status[self.kb.A_KEY_1]==1):
            #   print("Di . ")
               if ((self.kb.key_status[self.kb.B_KEY]==1) or (self.kb.key_status[self.kb.B_KEY_1]==1)) and (self.last_key==0):
                  self.last_key==1
               else:
                 if (self.di==False):
                     self.di=True
                     self.last_key=0
                     
                     # set sound end time
                     self.dida_end_in=utime.ticks_add(time.ticks_ms() , int(self.Di_length * self.Tone_length) )
                     # set next key allow time
                     #self.next_key_in=utime.ticks_add(self.dida_end_in , int(self.Di_length * self.Tone_length*4) )       
                     #print("Set:",time.ticks_ms(),self.dida_end_in,self.next_key_in)
                    
                     # Turn On LED/Buzzer
                     self.buzzer_sw=True
                     self.Buzzer.on()
                     self.Led_Di.on()

        # DASH     
        if (self.buzzer_sw==False) and ((self.kb.key_status[self.kb.B_KEY]==1) or (self.kb.key_status[self.kb.B_KEY_1]==1) ):
                #print("Dash -")
                if ( (self.kb.key_status[self.kb.A_KEY]==1) or (self.kb.key_status[self.kb.A_KEY_1]==1)) and (self.last_key==1):
                  self.last_key==0
                else:
                  if (self.da==False):
                     self.da=True
                     self.last_key=1

                     # set sound end time
                     self.dida_end_in=utime.ticks_add(time.ticks_ms() , int(self.Da_length * self.Tone_length) )
                     # set next key allow time
                     #self.next_key_in=utime.ticks_add(self.dida_end_in, int( self.Di_length * self.Tone_length*4) )
                     
                     # Turn On LED/Buzzer
                     self.buzzer_sw=True
                     self.Buzzer.on()
                     self.Led_Da.on()
      #else:
      #  print("Wait")
      if self.buzzer_sw:
            # Check if time up
            #print("Set:",self.dida_end_in,self.next_key_in,utime.ticks_diff( time.ticks_ms() , self.dida_end_in ))
            if utime.ticks_diff( time.ticks_ms() , self.dida_end_in ) >0:
              #print("Off")
              self.di=False
              self.da=False
              self.buzzer_sw=False
              
              # Turn Off LED/Buzzer
              self.Buzzer.off()
              self.Led_Di.off()
              self.Led_Da.off()
              self.next_key_in=utime.ticks_add(time.ticks_ms(), int(self.Di_length * self.Tone_length*1) )  
      self.checking=False
      
  


kb = KEYBOARD()
morse = MORSE_INDICATE(kb)

# 創建一個計時器(Period More less more quick)
kb_timer = Timer(0)
kb_timer.init(period=80, mode=Timer.PERIODIC, callback=kb.check)

# 創建一個計時器 for Morse Code(Period More less more quick)
morse_timer = Timer(1)
morse_timer.init(period=50, mode=Timer.PERIODIC, callback=morse.check)


try:
    while True:
        # 主循環可以放置其他程式碼，按鍵偵測已經在背景運作
        time.sleep(0.001)

        

            
except KeyboardInterrupt:
    kb_timer.deinit()  # 確保在結束時停止計時器
    morse_timer.deinit()  # 確保在結束時停止計時器




