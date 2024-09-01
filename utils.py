import json
import os
import pygame_canvas as c
import random as r

c.pygame.font.init()
font = c.pygame.font.Font("assets/mine.otf", 20)

def replace_chars(string: str, old: str, new: str = "random"):
    if not type(string) == str:
        raise TypeError
    if not type(old) == str:
        raise TypeError
    if not type(new) == str and not new == "random":
        raise TypeError
    string = list(string)
    if new == "random":
        for key, char in enumerate(string):
            string[key] = chr(r.randint(65,90)) if char == old else char
    else:
        for key, char in enumerate(string):
            string[key] = new if char == old else char
    return "".join(string)

def serialize_dict(d):
    """Custom function to serialize a dictionary, skipping non-serializable items."""
    serializable_dict = {}
    for key, value in d.items():
        try:
            # Try to serialize the value using json.dumps
            json.dumps(value)
            serializable_dict[key] = value
        except TypeError:
            # Handle the non-serializable item by just noting its type or name
            serializable_dict[key] = f"<Non-serializable: {type(value).__name__}>"
    return serializable_dict

def get_directory_size(directory):
    total_size = 0
    # Walk through all the directory
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # Get the full file path
            filepath = os.path.join(dirpath, filename)
            # Add the file size to the total size
            total_size += os.path.getsize(filepath)
    return total_size / (1024 ** 3)

def print_dict(dict, indent = 4):
    print(json.dumps(serialize_dict(dict), indent=indent))

def det_color(string, default):
    if "error" in string.lower():
        return (200,0,0)
    elif "warning" in string.lower():
        return (200,175,0)
    elif "done" in string.lower():
        return (0,200,0)
    else:
        return default

def debug_list(*list, color = (255,255,255), position = (0,0), font, color_callback = lambda x,y: x):
    
    if color_callback("xcq007", "") == "xcq007":
        color_callback = lambda x, y: color

    if not type(font) == c.pygame.font.Font:
        font = c.pygame.font.Font(font, 25)
    i = 0
    for item in list:
        c.text(str(item), (position[0],position[1]+i*20),color=color_callback(item, color), font=font)
        i += 1