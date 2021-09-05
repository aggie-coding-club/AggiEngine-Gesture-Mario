import random

from Box2D import Box2D

import AggiEngine as ag
from player import Player


class Goomba(ag.GameObject):

    def __init__(self):
        ag.GameObject.__init__(self)
        self.textures = []
        self.squashed = False
        self.timing = 0
        self.frame = 0
        self.squashedTime = 0
        self.dx = 0
        self.lastx = 0
        self.direction = 1 if random.randint(0, 1) == 0 else -1

    def start(self):
        """
        This is the start event called once all Qt Widgets are fully initialized.
        Here we can then access the widgets safely and setup various variables.
        """
        textureNames = ['goomba_1.png', 'goomba_2.png', 'goomba_3.png']
        for path in textureNames:
            self.textures.append(self.window.gameScreen.loadImageTexture('./MarioAssets/' + path))
        self.lastx = self.body.position[0]
        self.body.linearVelocity = [self.direction * 4, 0]

    def fixedUpdate(self):
        """
        AggiEngine is a multi-threaded application running on 3 different threads and loops.
        It is important to understand the difference between the GUI, Physics, and Rendering threads.
        Fixed Update ensures that physics related data types are accessible and able to be modifiable.
        This event always occurs IMMEDIATELY after Box2D has been updated.
        """
        if abs(self.body.position[0] - self.lastx) < 0.01 and not self.squashed:
            self.body.linearVelocity = [self.direction * 4, 2]

        self.dx += abs(self.body.position[0] - self.lastx)
        self.lastx = self.body.position[0]

        if not self.squashed:
            self.body.linearVelocity = [self.direction * 4, self.body.linearVelocity[1]]
        else:
            self.dx = 0

        if self.dx > 5:
            self.direction *= -1
            self.dx = 0

    def update(self):
        """
        AggiEngine is a multi-threaded application running on 3 different threads and loops.
        It is important to understand the difference between the GUI, Physics, and Rendering threads.
        Update ensures that OpenGL data types are accessible and able to be modifiable.
        This event always occurs IMMEDIATELY after OpenGL has finished rendering.
        """
        if self.timing > 1:
            self.frame = 1 if self.frame == 0 else 0
            self.timing = 0

        self.timing += 0.05

        if self.squashed:
            self.textureID = self.textures[2]
            self.squashedTime += 0.01

            if self.squashedTime > 5:
                self.squashed = False
                self.squashedTime = 0
        else:
            self.textureID = self.textures[self.frame]

    def beginContact(self, body):
        """
        Begin Contact is an event related to Box2D is it called DURING the Box2D update.
        This event is triggered when a body begins colliding with another body, but it is NOT triggered again
        if the two bodies have not separated.
        :param body: the Box2D body we're colliding with
        """
        if type(body.userData) is Player and self.squashed:
            self.gameObjectHandler.removeGameObject(self)

        if type(body.userData) is Player:
            self.squashed = True
            body.linearVelocity = [body.linearVelocity[0], 10]

        if type(body.userData) is Player:
            if abs(self.body.position[1] - body.position[1]) < 0.1:
                body.userData.dead = True

    def postSolve(self, contact, manifold):
        """
        Post Solve is an event related to Box2D is it called DURING the Box2D update.
        This event is triggered when a collision has been solved. This event is triggered anytime two bodies collide.
        This happens to objects that appear to not be moving as well, but applying force like gravity. Because any object with
        velocity well move into another Post Solve is called after this is resolved.
        :param contact: the Box2D body we're colliding with
        :param manifold: contains information related to the collision itself
        """
        if contact.type == Box2D.b2_dynamicBody:
            self.direction *= -1
            self.dx = 0
