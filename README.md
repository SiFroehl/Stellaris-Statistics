# Stellaris-Statistics
Collection of scripts to track progression in stellaris

## How it works:
This project uses Python 3 to run. The usage can be split into two parts:
- Copying the games autosaves:<br>
Copying needs to happen while playing as only a limited number of autosaves are kept by the game (5 by default, to have a better sampling rate, decrease the autosave interval). This means the copy part needs to have been started while you are playing!<br>
Saves are saved converted into JSON files in a folder created in the location the code is executed named the same as the observed game (i.e. EmpireName_123456789). These can be read by other programs if needed and you can use this program soly to copy the saves and process them in some other way.<br>
By default, some parts of the save are not copied to reduce file bloat (see USUALLY_SKIPPED_KEYS in GameDictConverter.py).<br>
Note that the actual gamesaves are not changed in any way but only copied to a working directory to be processed.<br>
Also note that due to the way the game saves ironman games, these are currently not supported.
- Processing the saves
This part processes the copied save files. To process, some prebuild tools are available (I might add more in the future but there are no concrete plans) for instance plotting of the gross domestic product of empires, their resource production, consumption and balance and other stats the game tracks like military power, number of pops etc. 

## TLDR What do I do?
The ExampleNotebook.ipynb is already set up to provide basic functionality like starting and stopping the copying and simple processing and can be modified to generate more detailled analysis.

## Additional stuff and disclaimer
This is a hobby project started years ago. The basic functionality has kept working for multiple major updates however this is not guaranteed to be the case in the future, use at your own risk!<br>
I'm not a professional coder and I know this code is messy, feel free to scream at my avatar as long as you don't use dictation software to actually contact me with said screaming :P
