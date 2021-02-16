# @file snowball_fight.py
# @brief  雪仗打起來
#author:許芸軒,20210216
#license: MIT


import random


from cocos.director import director
from collections import defaultdict
from cocos.scenes.transitions import SplitColsTransition
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu


class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)

    def __init__(self, x, y):
        super(PlayerCannon, self).__init__('1229.gif', x, y)

        self.speed = eu.Vector2(200, 0)

    def update(self, elapsed):
        pressed = PlayerCannon.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        if PlayerShoot.INSTANCE is None and space_pressed:
            self.parent.add(PlayerShoot(600, 320))


    def collide(self, other):
        other.kill()
        self.kill()


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0

    def __init__(self, hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h
        self.lives = 3
        self.create_player()
        self.create_alien()
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)
        self.schedule(self.update)

    def create_player(self):
        self.player = PlayerCannon(700, 320)
        self.add(self.player)
        self.hud.update_lives(self.lives)

    def create_alien(self):
        self.alien = Alien(100, 320)
        self.add(self.alien)
        #self.hud.update_lives(self.lives)



    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)
        self.collide(PlayerShoot.INSTANCE)
        if self.collide(self.player):
            self.respawn_player()

        for _, node in self.children:
            node.update(dt)

        if random.random() < 0.01:
            self.add(Shoot(200, 320))



    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                node.collide(other)
                return True
        return False

    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            self.unschedule(self.update)
            self.hud.show_game_over()
        else:
            self.create_player()


class Alien(Actor):
    def __init__(self, x, y):
        super(Alien, self).__init__('1229.gif', x, y)
        self.speed = eu.Vector2(200, 0)

    def update(self, elapsed):
        pass

    def collide(self, other):
        other.kill()
        self.kill()




class Shoot(Actor):
    def __init__(self, x, y, img='shoot.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(200, 0)

    def update(self, elapsed):
        self.move(self.speed * elapsed)


class PlayerShoot(Shoot):
    INSTANCE = None

    def __init__(self, x, y):
        super(PlayerShoot, self).__init__(x, y, 'laser.png')
        self.speed *= -1
        PlayerShoot.INSTANCE = self


    def collide(self, other):
        if isinstance(other, Alien):
            other.kill()
            self.kill()
            director.replace(SplitColsTransition(game_over()))
        if isinstance(other, Shoot):
            other.kill()
            self.kill()



    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        PlayerShoot.INSTANCE = None


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.add(self.score_text)
        self.add(self.lives_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game OVER', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)

def game_over():
    w, h = director.get_window_size()
    layer = cocos.layer.Layer()
    text = cocos.text.Label('Game Over', position=(w*0.5, h*0.5),
                            font_name='Oswald', font_size=72,
                            anchor_x='center', anchor_y='center')
    layer.add(text)
    scene = cocos.scene.Scene(layer)
    return scene


if __name__ == '__main__':
    ver = "v0.2"
    cocos.director.director.init(caption='雪仗打起來 '+ ver,
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)
