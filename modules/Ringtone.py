from threading import Timer
import time
import alsaaudio
import wave
import pygame

class Ringtone:
    shouldring = 0
    shouldplayhandset = 0
    ringtone = None
    ringfile = None
    ringstart = 0

    handsetfile = None
 

    config = None

    def __init__(self, config):
        self.config = config
        pygame.mixer.init()
        
    def start(self):
        self.shouldring = 1
        self.ringtone = Timer(0, self.doring)
        self.ringtone.start()
        self.ringstart = time.time()

    def stop(self):
        self.shouldring = 0
        if self.ringtone is not None:
            self.ringtone.cancel()

    def starthandset(self, file, loop=True):
        self.shouldplayhandset = 1
        self.handsetfile = file
        pygame.mixer.music.load(file)  
        loops = -1 if loop else 0
        pygame.mixer.music.play(loops=loops)

    def stophandset(self):
        self.shouldplayhandset = 0
        pygame.mixer.music.stop()
        pygame.mixer.music.rewind()


                
    def playfile(self, file):
        pygame.mixer.music.load(file)  
        pygame.mixer.music.play(loops=-1)

    def doring(self):
        if self.ringfile is not None:
            self.ringfile.rewind()
        else:
            self.ringfile = wave.open(self.config["soundfiles"]["ringtone"], 'rb')
            self.device = alsaaudio.PCM(card="plughw:1,0")
            self.device.setchannels(self.ringfile.getnchannels())
            self.device.setrate(self.ringfile.getframerate())
            self.device.setperiodsize(320)


        while self.shouldring:
            data = self.ringfile.readframes(320)
            while data:
                self.device.write(data)
                data = self.ringfile.readframes(320)

            self.ringfile.rewind()
            time.sleep(2)
            if time.time() - 60 > self.ringstart:
                self.stop()
