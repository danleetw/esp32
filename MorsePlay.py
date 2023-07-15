import machine
import time

Buzzer = machine.Pin(4 , machine.Pin.OUT)
Led_Da = machine.Pin(16 , machine.Pin.OUT)
Led_Di = machine.Pin(17 , machine.Pin.OUT)

Buzzer.off()
Led_Da.off()
Led_Di.off()

WPM=20
Tone_length=60/(WPM*5)/10
print(Tone_length)
Di_length=1
Da_length=3
After_word_length=7

def play_morse(text):
    #tone_length=0.07
    
    
    for letter in text:
        print(letter," (",end="")
        morse_codes=ascii__to_morse_code(letter)
        for morse_code in morse_codes:
          if morse_code=='-': # Dash
              print('-',end="")
              Buzzer.on()
              Led_Da.on()
              
              time.sleep(Tone_length*Da_length)
              
              Buzzer.off()
              Led_Da.off()
              time.sleep(Tone_length)
              
              time.sleep(Tone_length*Di_length)
          elif morse_code=='.':
              print('.',end="")
              
              Buzzer.on()
              Led_Di.on()
              
              time.sleep(Tone_length*Di_length)
              
              Buzzer.off()
              Led_Di.off()
              
              time.sleep(Tone_length*Di_length)
              
          elif morse_code=='_':
              print('_',end="")
              
              Buzzer.off()
              
              time.sleep(Tone_length*(After_word_length))
                       
        print(")")    
        
    
def ascii__to_morse_code(text):
    morse_code_table = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
        'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----'
    }

    morse_code = ''
    for char in text:
        #print(char," " , end="")
        if char.upper() in morse_code_table:
            morse_code += (morse_code_table[char.upper()] )
            #print ("(", morse_code_table[char.upper()] ,")")
        else:
            morse_code += '_'

    return morse_code  

print('start')    
play_morse('cq cq cq sota de bx2ako k   ' *1)    
#print(ascii__to_morse_code('cq cq cq sota'))
print('Done!!')

