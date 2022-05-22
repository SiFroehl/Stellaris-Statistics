import os
import zipfile
import GameDictConverter
import time
import threading


processed_saves = []
copy = False
path = None
save_games = None
save_game = None
is_initialized = False

def init():
    global path
    global save_games
    global save_game
    global is_initialized
    is_initialized = True
    path = os.path.expanduser("~") + "\\Documents\\Paradox Interactive\\Stellaris\\save games\\"

    if os.path.exists("config.txt"):
        with open("config.txt") as config_file:
            for line in config_file:
                if line.startswith("save_game_path"):
                    path = "".join(line.split("=")[1:]).strip()

    print(path)
    print("Please select a save game to watch!")
    save_games = os.listdir(path)
    for idx, save_game in enumerate(save_games):
        print("[%i] - %s" % (idx, save_game))

    selected_index = -1
    inp = input("Please enter the corresponding index: ")
    while selected_index == -1:
        try:
            idx = int(inp)
            if 0 <= idx < len(save_games):
                selected_index = idx
            else:
                print("That index is out of bounds!")
        except:
            print("Please enter a valid number!")

    save_game = save_games[selected_index]
    print("Selected \"%s\"" % save_game)

    if not os.path.exists(save_game):
        os.mkdir(save_game)

    if not os.path.exists(save_game + "\\copied_saves"):
        os.mkdir(save_game + "\\copied_saves")

    if not os.path.exists(save_game + "\\processed_saves.txt"):
        with open(save_game + "\\processed_saves.txt", "w") as processed_saves_file:
            pass
    
    with open(save_game + "\\processed_saves.txt", "r") as processed_saves_file:
        for line in processed_saves_file:
            processed_saves.append(line)

        
def start_copy():
    global is_initialized
    if not is_initialized:
        init()
    x = threading.Thread(target=internal_copy)
    x.start()
    
def stop_copy():
    global copy
    copy = False
    
def get_processing_path():
    return path + save_game
    
def internal_copy():
    global copy
    global path
    copy = True
    while copy:
        files = os.listdir(path + save_game)
        for file in files:
            if file not in processed_saves and file.endswith(".sav"):
                print("Processing " + file, end="")
                time_start = time.time_ns()
                zip_file = zipfile.ZipFile(path + save_game + "\\" + file)
                zip_file.extract("gamestate", path=save_game + "\\copied_saves")
                zip_file.extract("meta", path=save_game + "\\copied_saves")
                processed_saves.append(file)
                date = ""
                with open(save_game + "\\copied_saves\\meta") as meta:
                    for line in meta:
                        if line.startswith("date"):
                            date = line.split("=")[1].replace("\"", "").strip()
                in_file = save_game + "\\copied_saves\\gamestate"
                out_file = save_game + "\\copied_saves\\gamestate_%s.json" % date
                json_converted = GameDictConverter.create_json_from_file(in_file, out_file,
                                            skipped_top_level_keys=GameDictConverter.USUALLY_SKIPPED_KEYS)
                elapsed_time = (time.time_ns() - time_start) / 1e9
                print(" - took %.3f s" % elapsed_time)

        with open(save_game + "\\processed_saves.txt", "w") as processed_saves_file:
            for line in processed_saves:
                processed_saves_file.write(line)
    print("Stopped processing!")
            
if __name__ == "__main__":
    start_copy()
    x = input("Press enter to stop!")
    stop_copy()