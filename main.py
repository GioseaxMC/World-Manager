import json
import pygame_canvas as c
import random as r
import os
import nbtlib
from utils import *
import datetime
from buttons import Button
import shutil as s
import threading as t
import winsound

VERSION = "1.0.0"

minecraft_saves = "C:/Users/giose/AppData/Roaming/.minecraft/saves/"
worlds = list()
paths = list()
grey = (150, 150, 150)
backingUp = 0
loadingDown = 0
DEBUG = 0
console = ["" for i in range(34)]

def console_append(message, debug = 1):
    if debug:
        console.append(message)
        console.remove(console[0])
        console[0] = "             Esquisite log"

def clear():
    global console
    console = ["" for i in range(34)]
    console[0] = "             Esquisite log"


b_over_s = c.rectangle(256,20,"black")
textures = {
    "bg" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/background/background.png"), (16*3, 16*3)),
    "notfound" : c.pygame.image.load("assets/gui/background/notfound.png"),\
    "over" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/background/over.png"), (548, 72)),
    "selected" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/background/selected.png"), (548, 72)),
    "b_over" : b_over_s,
}
del b_over_s
with open("assets/gui/search_prompt.wmeta", "r") as f:
    chat_prompt = json.load(f)["prompt"]["text"]


gamemodes = ["Survival", "Creative", "Adventure", "Spectator", "Harcore :)"]

c.window(1290,740, title = f"World Manager - {VERSION}", can_resize=1, smallest_window_sizes=(1290, 740), do_draws=0, icon = "assets/icon.png")

def get_world_data(wlist, directory, silent):
    temp = list()
    for world in wlist:
        world_path = str(directory + world)
        paths.append(world_path)
        if not silent:
            console_append("")
            console_append(f"Loading {world}...")
        try:
            data = nbtlib.load(world_path + "/level.dat")
        except (FileNotFoundError, TypeError):
            if not silent:
                console_append(f"ERROR: Invalid world:")
                console_append(f"{world}")
                console_append(f"skipping ahead.")
            continue
        
        try:
            icon = c.pygame.image.load(str(world_path + "/icon.png"))
        except:
            icon = textures["notfound"]

        try:
            lp = int(data["Data"]["LastPlayed"])
        except:
            lp = 0
            if not silent:
                console_append("- WARNING: Failed to load LastPlayed")

        try:
            version = str(data["Data"]["Version"]["Name"])
        except:
            version = "unknown"
            if not silent:
                console_append("- WARNING: Failed to load Version")

        try:
            name = str(data["Data"]["LevelName"])
        except:
            name = "unknown"
            if not silent:
                console_append("- WARNING: Failed to load LevelName")
        
        world = {
            "icon" : icon,
            "last played" : lp,
            "version" : version,
            "gm" : gamemodes[int(data["Data"]["GameType"])],
            "path" : world_path,
            "name" : name,
            "folder" : world,
            "size" : 0,
            "backup_dir" : str(),
            "backups" : list(),
            "missing" : 0
        }

        world["backup_dir"] = f"./saves/{world["folder"]}"

        try:
            world["backups"] = list(datetime.datetime.fromtimestamp(int(i.split()[-1]) // 1000) for i in list(os.listdir(world["backup_dir"])))
        except FileNotFoundError:
            world["backups"] = list()

        try:
            world["size"] = round(get_directory_size(world["path"]), 2)
        except:
            world["size"] = 0
            if not silent:
                console_append("- WARNING: Failed to calculate level size")
        if not silent:
            console_append("Done")

        temp.append(world)
    return temp

def load_worlds(silent = 0):
    global worlds, paths, world_list, filtered_worlds
    world_list = os.listdir(minecraft_saves)
    temp = get_world_data(world_list, minecraft_saves, silent)
    worlds = list(sorted(temp, key = lambda x: x["last played"], reverse=1))
    try:
        backups = os.listdir("saves/")
    except FileNotFoundError:
        os.mkdir("saves/")
        backups = os.listdir("saves/")
    missing_backups = list(filter(lambda x: x not in world_list, backups))
    for world in missing_backups:
        try:
            icon = c.pygame.transform.scale(c.pygame.image.load(f"saves/{world}/{os.listdir(f"saves/{world}")[0]}/icon.png"), (64,64))
        except FileNotFoundError:
            icon = textures["notfound"]
        worlds.append(
            {
                "icon" : icon,
                "last played" : 0,
                "version" : "---",
                "gm" : "---",
                "path" : minecraft_saves + world,
                "name" : world,
                "folder" : world,
                "size" : "---",
                "backup_dir" : f"./saves/{world}",
                "backups" : list(datetime.datetime.fromtimestamp(int(i.split()[-1]) // 1000) for i in list(os.listdir(f"./saves/{world}"))),
                "missing" : 1
            }
        )
    del temp
    filtered_worlds = worlds
load_worlds()

def backup(world, forced = 0):
    load_worlds(1)
    global filtered_worlds, backingUp
    if (backingUp or loadingDown) and not forced:
        console_append("|-- ERROR --|")
        console_append("another process is running.")
        winsound.MessageBeep(winsound.MB_ICONHAND)
        return
    backingUp = 1
    w = filtered_worlds[world]
    if w["missing"]:
        console_append("")
        console_append("|-- WARNING --|")
        console_append("Cannot backup a deleted world")
        console_append("try restoring it by loading the")
        console_append("latest backup")
        winsound.MessageBeep()
        backingUp = 0
        return    
    path = w["path"]
    dest = f"./saves/{w["folder"]}/{w["folder"]} - {w["last played"]}"
    console_append("Backing up. . .")
    try:
        s.copytree(path, dest)
    except FileExistsError:
        pass
    except:
        console_append("ERROR: World open.")
        console_append("quit the world to back it up.")
        backingUp = 0
        return
    backingUp = 0
    console_append("Done")
    if loadingDown:
        return
    load_worlds(1)

def threaded_backup(world):
    thread = t.Thread(target=backup, args=(world,))
    thread.start()

def load(world, id):
    global filtered_worlds, loadingDown
    if loadingDown or backingUp:
        console_append("|-- ERROR --|")
        console_append("another process is running.")
        winsound.MessageBeep(winsound.MB_ICONHAND)
        return
    loadingDown = 1
    w = filtered_worlds[world]
    try:
        dirs = list(os.listdir(f"./saves/{w["folder"]}"))
        if not len(dirs):
            console_append("No backups available.")
            # message when implemented
            loadingDown = 0
            return
    except FileNotFoundError as e:
        # add message when console is implemented
        console_append("No backups available.")
        loadingDown = 0
        return
    dirs.sort(reverse=1)
    print(id)
    if len(dirs)-1:
        id = id % len(dirs)
        print("wrong")
    else:
        id = 0
    path = "saves/" + w["folder"] + "/" + dirs[id]
    print(dirs)
    print(id)
    console_append(f"Preparing world:")
    console_append(dirs[id])
    dest = w["path"]
    if not w["missing"]:
        if backup(world, 1):
            console_append("ERROR: Cannot load an open world.")
        s.rmtree(dest)
        console_append("Loading from backups. . .")
    else:
        console_append("Restoring from backups. . .")
    s.copytree(path, dest)
    loadingDown = 0
    console_append("Done")
    load_worlds(1)

def threaded_load(world, id):
    thread = t.Thread(target=load, args=(world,id))
    thread.start()

# 47 y coordinate increase lol
buttons = list()
buttons.append(Button(32, (0,0), "Back up", callback=threaded_backup, id=-2))
buttons.append(Button(32, (0,0), "Load last backup", callback=threaded_load))
buttons.append(Button(32, (0,0), "Load selected backup", callback=threaded_load))

background = c.sprite
world_bg = c.sprite
def update_sizes():
    global SCREEN, CENTER, buttons, background, console_bg, world_bg, search_bar
    try:
        world_bg.kill()
    except TypeError:
        pass
    try:
        background.kill()
    except TypeError:
        pass
    SCREEN = c.screen_size()
    CENTER = (c.screen_size()[0] // 2, c.screen_size()[1] // 2)
    for key, button in enumerate(buttons):
        button.body.set_position(SCREEN[0]-136, 370 + key*47)
        button.body.update(1)
    background = c.pygame.Surface(SCREEN)
    background.fill("black")
    with open("assets/gui/background/background.png.wmeta") as f:
        f = json.load(f)
    textures["bg"].set_alpha(f["display"]["alpha"])
    for x in range(0, SCREEN[0] // 48 + 1):
        for y in range(0, SCREEN[1] // 48 + 1):
            background.blit(textures["bg"], (x*16*3,y*16*3))
    background = c.sprite((background,), CENTER)
    background.set_depth(-1)
    console_bg = c.pygame.Surface((350, 704))
    temp = c.pygame.Surface((272, SCREEN[1]))
    temp.fill("black")
    world_bg = c.sprite((temp,), (SCREEN[0]-272//2, SCREEN[1]//2))
    world_bg.set_depth(-1)
    with open("assets/gui/background/console_bg_color.wmeta") as f:
        f = json.load(f)
    console_bg.fill(f["display"]["color"])
    console_bg.set_alpha(f["display"]["alpha"])
    world_bg.alpha = f["display"]["alpha"]
    world_bg.update()
    del f

    search_bar = c.pygame.Surface((SCREEN[0] * 0.4245,30))
    search_bar.fill("white")
    search_bar.blit(c.rectangle(SCREEN[0] * 0.4245 - 4, 26, "black"), (2,2))
update_sizes()

scrollY = 0
over = str()
selected = 0
search = ""
b_over = 0
b_selected = 0

filtered_worlds = worlds
while c.loop(60, "white"):
    if c.is_updating_sizes():
        update_sizes()

    for button in buttons:
        button.update(selected)

    wheel = c.get_wheel()
    scrollY += wheel * 40
    scrollY = min(max(scrollY, -len(worlds)*72+SCREEN[1]-172), 0)
    over = (c.mouse_position()[1] - scrollY - 60) // 72
    b_over = (c.mouse_position()[1] - 509) // 20
    TOUCHING = CENTER[0]-275 < c.mouse_position()[0] and c.mouse_position()[0] < CENTER[0]+275
    B_TOUCHING = SCREEN[0] - 272 < c.mouse_position()[0] and c.mouse_position()[1] > 509
    selected += c.key_clicked(c.pygame.K_DOWN) - c.key_clicked(c.pygame.K_UP)
    selected = min(max(selected,0), len(worlds)-1)

    key = c.get_clicked_key()
    if key:
        console_append(f"DEBUG: pressed: {key}", DEBUG)
        if key == 127:
            clear()
        elif key == 8:
            if c.ctrl():
                search = ""
            else:
                search = search[:-1]
        elif c.ctrl():
            pass
        else:
            try:
                search = search + chr(key)
            except ValueError:
                pass
        console_append("Searching for world. . .", DEBUG)
        filtered_worlds = list(filter(lambda x: search.lower() in x["name"].lower() or search.lower() in x["folder"].lower(), worlds))
        console_append("Done", DEBUG)

    DEBUG = c.flick(c.key_clicked(c.pygame.K_F3), DEBUG)
    if DEBUG:
        c.debug_list(
            f"FPS: {c.get_FPS()}",
            c.mouse_position(),
            f"Over: {over}",
            f"Backup over: {b_over}",
            f"Selected: {selected}",
            f"Backup selected: {b_selected}",
            f"Touching: {TOUCHING}",
            f"Touching backups: {B_TOUCHING}",
            f"Overing in range: {(over < 0 or over > len(worlds)-1)}",
            f"Resolution: {SCREEN}",
            f"Sprites: {len(c.get_all())}",
            f"ScrollY: {scrollY}",
            f"",
            f"BACKING UP {backingUp} WORLDS..." if backingUp else "",
            f"LOADING {loadingDown} WORLDS..." if loadingDown else "",
            font = font
        )

    if c.key_clicked(c.pygame.K_F5):
        #load_worlds()
        temp = t.Thread(target=load_worlds)
        temp.start()

    cursor = "_" if not c.get_frames() % 30 > 15 else " "
    search = search.replace('\x00', '')
    for key, world in enumerate(filtered_worlds):
        color = "red" if world["missing"] else "white"
        if key == over and TOUCHING:
            c.blit(textures["over"], (CENTER[0]-274, 54+(key*72)+scrollY))
            if c.get_left_clicked():
                selected = key
        if selected == key:
            if B_TOUCHING and c.get_left_clicked():
                b_selected = b_over
            b_selected = min(max(b_selected,0), len(world["backups"])-1)
            buttons[2].id = b_selected

            c.blit(textures["b_over"], (SCREEN[0] - 264, 509+b_selected*20))
            c.blit(textures["selected"], (CENTER[0]-274, 54+(key*72)+scrollY))
            c.blit(c.pygame.transform.scale_by(world["icon"], 4), (SCREEN[0] - 256 - 8, 0 + 8))
            c.text(world["name"], (SCREEN[0] - 250, 268), 20, color, font)
            c.debug_list(
                f"Version: {world["version"]}",
                f"Gamemode: {world["gm"]}",
                f"Size: {replace_chars(str(world["size"]), "-")}GB",
                position=(SCREEN[0] - 250, 256 + 32), color=grey, font=font
                )
            c.debug_list(
                "Backups:",
                *world["backups"].__reversed__(),
                position=(SCREEN[0] - 250, 490) , color=grey, font=font
                )
        c.text(world["name"], (CENTER[0]-200, 60+(key*72)+scrollY), size=20, color=color, font = font)
        c.text(f"{world["folder"]}  ({datetime.datetime.fromtimestamp(world["last played"]//1000)})", (CENTER[0]-200, 80+(key*72)+scrollY), size=20, color=grey, font = font)
        c.text(f"{world["gm"]} Mode, Version: {world["version"]}", (CENTER[0]-200, 100+(key*72)+scrollY), size=20, color=grey, font = font)
        c.blit(world["icon"], (CENTER[0]-270, 58+(key*72)+scrollY))

    c.blit(console_bg, (8,8))
    c.cool_text("By @gioseaxmc - not affiliated with MojangAB", (4,SCREEN[1]-24), 20, font=font)
    debug_list(
        *console,
        position=(16,20),
        font = font,
        color=(200,200,200),
        color_callback=det_color
    )
    c.blit(search_bar, (CENTER[0] - SCREEN[0] * 0.4245 // 2 - 1, 8))
    if len(search):
        c.text(f"{search}{cursor}", (CENTER[0] - SCREEN[0] * 0.4245 // 2 + 4, 14), 20, "white", font)
    else:
        c.text(chat_prompt, (CENTER[0] - SCREEN[0] * 0.4245 // 2 + 4, 14), 20, "dark grey", font)

    c.draw_calls(60)