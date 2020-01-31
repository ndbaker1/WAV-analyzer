import wave, struct
import math, numpy
import os
from scipy.fft import rfft
from tkinter import Tk, Canvas, Label, Text, Entry, Button, Frame, DoubleVar, StringVar, filedialog
from time import time

#####################################################
#       Accepts any function and prints the
#   amount of time -in seconds- takes to complete
#####################################################
def measureFunc(function, procedure_name):
    beg_time = time()
    val = function()
    print('Process <', procedure_name, '> completed in', time()-beg_time, 'seconds at Time :', time())
    return val

#################################################################################################
#   Graphs the Intensities for every Frequency(Note) in a given range with TKinter Canvas Lib.
#################################################################################################
class Analyzer:    
    def __init__(self):
        ###############################
        ###############################
        #   CONTANTS AND PROPERTIES   #
        ###############################
        ###############################
        self.wav_file = None
        self.g_prop = {
            'width'         :   1200,
            'height'        :   800,
                
            'freq_lower'    :   1,      #   Lower Bound Frequency < inclusive >
            'freq_upper'    :   1600,   #   Upper Bound Frequency < inclusive >
                
            'ch_pad'        :   20,     #   Audio Channel Padding ( From the Top )
            'top_pad'       :   50,     #   Top Padding
            'bot_pad'       :   50,     #   Bottom Padding
            'left_pad'      :   100,    #   Left Padding
            'right_pad'     :   300,    #   Right Padding

            'freq_gap'      :   50,     #   Pixels between Frequency labels

            'bg_color'      :   "#010119",
            'bar_color'     :   "#8cf2f2",
            'text_color'    :   "#9097b3",
            'dot_color'     :   "#474d61",
            'btn_bg_color'  :   "#8cf2f2",  #   Button Background Color
            'btn_abg_color' :   "#6cd2d2",  #   Button Active Background Color
            'btn_fg_color'  :   "#010119",  #   Button Foreground (text) Color
            'config_color'  :   "#d0d7f3"   #   Statisitics Text Color
        }

        self.graph_width     = self.g_prop['width'] - ( self.g_prop['left_pad'] + self.g_prop['right_pad'] )
        self.graph_height    = self.g_prop['height'] - ( self.g_prop['top_pad'] + self.g_prop['bot_pad'] )
            
        self.frequency_range = self.g_prop['freq_upper'] - self.g_prop['freq_lower']
        self.pixel_interval  = self.graph_width/self.frequency_range
        
        self.num_intervals   = self.graph_width/self.g_prop['freq_gap']
        self.interval_value  = self.frequency_range/self.num_intervals
    
        self.current_graph = [] # Holds the current bars on the graph so that they can be removed later

        ########################
        ########################           
        #   < WINDOW SETUP >   #
        ########################
        ########################
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title('.wav Analyzer')
        self.g = Canvas(self.window, width=self.g_prop['width'], height=self.g_prop['height'], bg=self.g_prop['bg_color'])  # Canvas
        self.g.pack(side='left')
        config = Frame(self.window, bg=self.g_prop['bg_color'], bd=2)                                            # Frame/UI
        self.g.create_window(self.g_prop['width']-self.g_prop['right_pad']/2, self.g_prop['height']/2-self.g_prop['top_pad']/3, window = config)
        
        # CONFIGURABLE VALUES
        self.start_time = DoubleVar()
        self.end_time = DoubleVar()
        self.file_var = StringVar()
        start_Frame = Frame(config)
        end_Frame   = Frame(config)
        button_Frame= Frame(config, bg=self.g_prop['bg_color'])
        Label(config,       font=("Roboto", 16), text='Frequencies',  bg=self.g_prop['bg_color'], fg=self.g_prop['config_color']).pack(side='top', pady=(20,0))
        Label(start_Frame,  font=("Roboto", 12), width=10, text='Start Time',   bg=self.g_prop['bg_color'], fg=self.g_prop['config_color']).pack(side='left', fill='y')
        Label(end_Frame,    font=("Roboto", 12), width=10, text='End Time',     bg=self.g_prop['bg_color'], fg=self.g_prop['config_color']).pack(side='left', fill='y')
        Label(config,       font=("Roboto", 11), width=10, textvariable=self.file_var, bg=self.g_prop['bg_color'], fg=self.g_prop['config_color']).pack(side='bottom', fill='x')
        Entry(start_Frame,  font=("Roboto", 12), width=15, textvariable=self.start_time).pack(side='right', fill='y')
        Entry(end_Frame,    font=("Roboto", 12), width=15, textvariable=self.end_time).pack(side='right', fill='y')
        Load_Graph      =   Button(button_Frame, bd=0, bg=self.g_prop['btn_bg_color'], fg=self.g_prop['btn_fg_color'], activebackground=self.g_prop['btn_abg_color'], text='Update', font=("Roboto", 12), height=2, width=12,
                            command=lambda : measureFunc(lambda : self.drawGraph(self.start_time.get(), self.end_time.get() - self.start_time.get()), 'Graph Frequencies'))
        Load_New_File   =   Button(button_Frame,    bd=0, bg=self.g_prop['btn_bg_color'], fg=self.g_prop['btn_fg_color'], activebackground=self.g_prop['btn_abg_color'], text='Load File', font=("Roboto", 12), height=2, width=12,
                            command=lambda : [self.loadFile(filedialog.askopenfilename(initialdir=os.getcwd(), title='Select Audio File', filetypes=(('wav files', '*.wav'),('all files', '*.*  ')))), Load_Graph.invoke()])
        self.Stat_Log   =   Text(config, font=('Roboto', 12), height=26, width=8, bd=10, bg=self.g_prop['bg_color'], fg=self.g_prop['config_color'], state='disabled')

        # PACK COMPONENTS INTO FRAME
        self.Stat_Log.pack(side='top', fill='both', padx=8, pady=(10,20))
        Load_Graph.pack(side='left', pady=20, padx=8)
        Load_New_File.pack(side='right', pady=20, padx=8)
        start_Frame.pack(side='top')
        end_Frame.pack(side='top')
        button_Frame.pack(side='top')
    
        rnd_dig = (10**5)
        # KEYBINDINGS
        self.window.bind('<Return>',lambda e: [
                                        Load_Graph.config(relief = "sunken"),
                                        Load_Graph.config(state='active'),
                                        self.window.update_idletasks(),
                                        Load_Graph.invoke(),
                                        Load_Graph.config(relief = "raised"),
                                        Load_Graph.config(state='normal')
                                    ])
        self.window.bind('<Up>',    lambda e: [ self.start_time.set(round(rnd_dig*(self.start_time.get()+0.1))/rnd_dig),
                                                self.end_time.set(round(rnd_dig*(self.end_time.get()+0.1))/rnd_dig)])
        self.window.bind('<Down>',  lambda e: [ self.start_time.set(round(rnd_dig*max(0,self.start_time.get()-0.1))/rnd_dig),
                                                self.end_time.set(round(rnd_dig*max(0,self.end_time.get()-0.1))/rnd_dig)])
        self.window.bind('<Shift_R>', lambda e: [
                                        Load_New_File.config(relief = "sunken"),
                                        Load_New_File.config(state='active'),
                                        self.window.update_idletasks(),
                                        Load_New_File.invoke(),
                                        Load_New_File.config(relief = "raised"),
                                        Load_New_File.config(state='normal')
                                    ])

        #########################
        #########################
        #   < GRAPH SETUP >     #
        #########################
        #########################
        self.g.create_text(
            self.g_prop['left_pad']/2, 
            self.g_prop['top_pad']/2, text='Hertz', 
            fill=self.g_prop['text_color'], 
            font=("Roboto", 15))
        for i in range(math.ceil(self.num_intervals)):
            # GRAPH FREQUENCY LABELS
            self.g.create_text(
                i*self.g_prop['freq_gap'] + self.g_prop['left_pad'], 
                self.g_prop['top_pad']/2,text=self.g_prop['freq_lower'] + math.floor(i*self.interval_value), 
                fill=self.g_prop['text_color'], 
                font=("Roboto", 12))
            # DOTTED LINES
            self.g.create_line(
                i*self.g_prop['freq_gap'] + self.g_prop['left_pad'], 
                self.g_prop['top_pad'], i*self.g_prop['freq_gap'] + self.g_prop['left_pad'], 
                self.g_prop['height'] - self.g_prop['bot_pad'], 
                fill=self.g_prop['dot_color'], 
                dash=(3,3))
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #   TKINTER MAINLOOP START
        self.window.mainloop()
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    ##############################
    #   Loads a new WAV File
    #   and resets the timestamp
    ##############################
    def loadFile(self, filepath):
        if (not os.path.exists(filepath)):
            raise Exception('File Not Found.')
        self.file_var.set(filepath[filepath.rindex('/')+1:])
        self.wav_file = wave.open(filepath)
        self.start_time.set(0)
        self.end_time.set(0.5)
        print('File Parameters :: ', self.wav_file.getparams())

    ##################################
    #   Graphs Each Audio Channel
    ##################################
    def drawGraph(self, start_time, duration):
        if self.wav_file is None:
            raise Exception('No Audio File is Loaded')
        # REMOVE OLD ITEMS
        for item in self.current_graph:
            self.g.delete(item)
        transform, freq_max = measureFunc(lambda : self.FourierTransform(start_time, duration), 'Fourier Transform')
        nchannels           = self.wav_file.getnchannels()
        for n in range(nchannels):
            # DISPLAY AUDIO CHANNEL NUMBER
            self.current_graph.append( 
                self.g.create_text(
                    self.g_prop['left_pad']/2,
                    self.graph_height*(n+0.5)/nchannels + self.g_prop['top_pad'],
                    text=f'Channel {n+1}',
                    fill=self.g_prop['text_color'],
                    font=("Roboto", 20),
                    angle=90))
            # ITERATE OVER ALL USABLE FREQUENCIES
            for i in range(int(self.frequency_range*duration)):
                # Strength between 0 and 1 relative to the Max Frequency Strength
                rel_unit_freq = (transform[n][i+self.g_prop['freq_lower']]/freq_max)
                # (x1,y1) and (x2,y2) format
                # ADD NEW ITEMS TO LIST
                self.current_graph.append(
                    self.g.create_rectangle(
                        i*self.pixel_interval/duration + self.g_prop['left_pad'],
                        self.graph_height*(n+1)/nchannels + self.g_prop['top_pad'],
                        (i+1)*self.pixel_interval/duration + self.g_prop['left_pad'],
                        ((n+1-rel_unit_freq)*self.graph_height/nchannels + rel_unit_freq*self.g_prop['ch_pad']) + self.g_prop['top_pad'],
                        fill=self.g_prop['bar_color'],
                        outline=self.g_prop['bar_color']))
    
    ########################################
    #       Fourier Transform based
    #   on a Start Position and Duration
    ########################################
    def FourierTransform(self, start_time, duration):
        ########################
        #   Needed Parameters
        ########################
        nchannels, sampwidth, framerate, nframes, comptype, compname = self.wav_file.getparams()
        frame_interval = min(self.secondsToFrames(duration), nframes) 
        
        ########################################
        #     Set the current Frame of       
        #          the pointer               
        #  Frames = rate( Hz ) * time( Sec ) 
        ########################################
        start_frame = self.secondsToFrames(start_time)
        if (start_frame > nframes):
            raise ValueError('The Start position exceeds file length.')
        if (start_frame+frame_interval > nframes):
            raise ValueError('The End Position exceeds the file Length')
        self.wav_file.setpos(start_frame)
        
        ############################################
        #    Dictionary for Format to Byte-size    
        #    B - unsigned char - 8 bit PCM         
        #    h - signed short  - 16bit PCM         
        #    i - signed int    - 32bit PCM         
        ############################################
        depth_factor = {1: 'B', 2: 'h', 4: 'i'}
        
        #######################################################################
        #    Unpacks each frame of the Wav file according to its bit depth    
        #    and stores each channel in a separate array                      
        #######################################################################
        transform = [[] for i in range(nchannels)]
        for x in range(frame_interval):
            data = struct.unpack(f"<{nchannels}{depth_factor[sampwidth]}", self.wav_file.readframes(1))
            for n in range(nchannels):
                transform[n].append(data[n])

        #############################################################
        #   Performs a DFT on each audio channel
        #   Stores the Magnitude of each resulting complex number     
        #############################################################
        for n in range(nchannels):
            transform[n] = rfft(transform[n])
            for i, freq in enumerate(transform[n]):
                transform[n][i] = numpy.absolute(freq)
            transform[n] = transform[n].real.tolist()
        
        ############################################
        #    Finds the Max for Normalization
        #    -ignores the 0Hz component DC
        #       *finds the mean for later
        ############################################
        freq_max = 0
        for audio_channel in transform:
            for k in range(1, len(audio_channel)):
                freq_max = max(freq_max, audio_channel[k])
        
        ################################################
        #    Find frequencies that are most present
        #       in each of the audio channels
        ################################################
        threshhold_factor = 0.5
        threshhold = []
        for channel in transform:
            max_f = 0
            for k in range(1, len(channel)):
                max_f = max(max_f, channel[k])
            threshhold.append(max_f*threshhold_factor)
        self.Stat_Log.config(state='normal')
        self.Stat_Log.delete(1.0, 'end')
        for n in range(nchannels):
            channel_text = ''
            for k in range(1, len(transform[n])):
                note, interval = self.noteSearch(k*framerate/frame_interval)
                if interval >= 0 and transform[n][k] > threshhold[n] and note+str(interval) not in channel_text:
                    channel_text += f'{note}{interval} on Freq. {round(100*k*framerate/frame_interval)/100}\n'
            if (channel_text != ''):
                self.Stat_Log.insert('insert', f'Channel {n+1}\n{channel_text}\n')
        self.Stat_Log.config(state='disabled')
        return (transform, freq_max)
    
    #################################
    #   Seconds to Frames Converter
    #################################
    def secondsToFrames(self, second):
        return int(second*self.wav_file.getframerate())
    
    ###############################################################
    #   Finds a Note and its Register Given the Frequency (Hertz)
    #   Equal Temperment = 2^(1/12) = 1.05946309436
    ###############################################################
    def noteSearch(self, hertz):
        # Based on a 440 A_4
        fr = 440
        fr_upper = fr*0.02973154717
        fr_lower = fr*0.02806284365
        it = 0
        notes = {
            0 :'A', 1 :'A#', 2 :'B', 3 :'C', 4 :'C#', 5:'D',
            6 :'D#',7 :'E', 8 :'F', 9 :'F#', 10:'G', 11:'G#'
        }
        while(hertz >= fr+fr_upper or hertz < fr-fr_lower):
            if (hertz < 440):
                it-=1
                fr /= 1.05946309436
            else:
                it+=1
                fr *= 1.05946309436
            # Upper found by f = f + (f*c - f)/2 = f*(c+1)/2
            fr_upper = fr*0.02973154717
            # Lower found by f = f - (f - f/c)/2 = f*(1+(1/c))/2
            fr_lower = fr*0.02806284365
        return (notes[it%12], math.ceil(4+it/12)) 

#######
# RUN #
#######
Analyzer()



