import wx
import threading
import queue
import time
import os
import wave
import numpy as np
import whisper
import pyaudio
import sys
import tempfile

whisperModel = whisper.load_model("base")

###############################################################################
# Audio transcription panel
###############################################################################
class TranscriptPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(100,100))

        # audio file path queue (used as thread inter-communication)
        self._audioQueue = queue.Queue()

        # Text control to display commands "as string"
        self._text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH) # | wx.TE_READONLY

        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(self._text, 1, wx.EXPAND)

        # Start a thread to handle audio capture
        self._audioTask = threading.Thread(target=self._audioAquisitionTask)
        self._audioTask.setDaemon(True)
        self._audioTask.start()

        # Start a thread to handle audio file transcription
        self._transcriptTask = threading.Thread(target=self._audioTranscriptionTask)
        self._transcriptTask.setDaemon(True)
        self._transcriptTask.start()

    def appendText(self, text):
        if text:
            self._text.AppendText(text + '\n')

    def setText(self, text, fireEvent=False):
        if fireEvent :
            self._text.SetValue(text) #true
        else :
            self._text.ChangeValue(text) #false

    def getText(self):
        return self._text.GetValue()

    def _audioAquisitionTask(self):
        CHUNK = 1024*4
        FORMAT = pyaudio.paInt16
        CHANNELS = 1 #mono
        RATE = 22050
        NOISE_LEVEL = 1000
        GAIN = 4
        
        outDir = tempfile.gettempdir()
        wfOutFilePath = None
        
        p=pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
        wfOut = None
        
        while self:
            chunck = stream.read(CHUNK)
            npChunck = np.frombuffer(chunk, dtype=np.int16)
            try:
                maxAmp = abs(npChunck.max() - npChunck.min())
            except:
                maxAmp = NOISE_LEVEL+1
                
            if wfOut == None:
                if maxAmp>NOISE_LEVEL:
                    wfOutFilePath=tempfile.mktemp(dir=outDir) + '.wav'
                    wfOut=wave.open(wfOutFilePath, 'wb')
                    wfOut.setnchannels(CHANNELS)
                    wfOut.setsampwidth(p.get_sample_size(FORMAT))
                    wfOut.setframerate(RATE)
                    print("Create audio file.")
                    t0=time.time() #chrono
            if wfOut != None:
                wfOut.writeframes(npChunck*GAIN)
                
                if (time.time() - t0)>3 and (maxAmp<NOISE_LEVEL):
                    wfOut.close()
                    wfOut=None
                    print("Send audio file", wfOutFilePath)
                    self._audioQueue.put_nowait(wfOutFilePath)
        stream.close()
        p.terminate()
        
        if xfOut != None:
            wfOut.close()
        
        try:
            os.unlink(wfOutFilePath)
        except:
            pass
        
    def _audioTranscriptionTask(self):
        while self:
            audioFilePath=self._audioQueue.get()
            
            print("Transcript...", audioFilePath)
            
            if False:
                result=whisperModel.transcribe(audioFilePath, language="fr", fp16=False)
                text=result['text']
            else:
                audio=whisper.load_audio(audioFilePath)
                audio=whisper.pas_or_trim(audio)
                
                mel=whisper.log_mel_spectogram(audio).to(whisperModel.device)
                
                options = whisper.DecodingOptions(
                        task = 'transcribe',        # or "translate" for X -> English
                        language = 'fr',            # force language to French
                        without_timestamps = True,  # no need for timestamps info
                        fp16 = False                # crash if True
                    )
                result = whisper.decode(whisperModel, mel, options)
                text = result.text

            print('Transcript Done')
            os.unlink(audioFilePath)

            wx.CallAfter(self.appendText, text)