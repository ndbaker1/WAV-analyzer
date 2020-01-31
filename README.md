# WAV-analyzer
A Python App built with tkinter.

Visualizes Musical Pitches/Frequencies found in WAV files using Fourier Transforms.

![screenshot](https://user-images.githubusercontent.com/48701178/73523177-e2c3de80-43cf-11ea-828b-7dfa3168991e.png)

## Features
- A given WAV file will have its frequencies graphed by Hertz for each respective Audio Channel 
- The user can load any WAV file and its name will be displayed in the bottom right of the window.
- New **Start Time** and **End Time** values may be entered in order to adjust the interval of time that will be looked at during the Fourier Transform 
  > *Time read as seconds in decimal form*
- Strongly present frequencies and their respective pitch/note will be displayed in the text box on the right for each respective Audio Channel

### Keybindings
```
RETURN      :   Update Graph
RIGHT-SHIFT :   Load New File
UP ↑        :   Shift the Time Interval by +0.1s
DOWN ↓      :   Shift the Time Interval by -0.1s
```
### Tools
- python  3.8.1
- tkinter 8.6
- scipy   1.4.1
