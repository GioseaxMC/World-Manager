import pygame_canvas as c
from utils import font

buttons = {
    "320" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/buttons/button32.png"), (256, 40)),
    "321" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/buttons/button_highlighted32.png"), (256, 40)),
    "322" : c.pygame.transform.scale(c.pygame.image.load("assets/gui/buttons/button_disabled32.png"), (256, 40)),
    }

class Button:
    def __init__(self, size = 32, position = (0,0), text = "unsigned", callback = lambda x: x, id = 0) -> None:
        self.body = c.sprite([buttons[f"{size}{types}"] for types in (0,1,2)], pos = position)
        self.text = text
        self.callback = callback
        self.id = id

    def update(self, selected):
        self.body.frame = int(self.body.touching_mouse())
        self.body.update()
        text_position = self.body.get_position()[0], self.body.get_position()[1] + 2
        c.cool_text(self.text, text_position, 20, 0.1, ("white",(75,75,75)), font, 1, 0)
        if self.body.touching_mouse() and c.get_left_released():
            if self.id == -2:
                self.callback(selected)
            else:    
                self.callback(selected, self.id)
