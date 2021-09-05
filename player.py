from PySide2.QtCore import Qt

import AggiEngine as ag
from HandTracker import HandInput


class Player(ag.GameObject):

    def __init__(self):
        ag.GameObject.__init__(self)
        self.y_pos = 0
        self.jumps = 0
        self.rightTex = []
        self.leftTex = []
        self.running = False
        self.jumping = False
        self.timing = 0
        self.frame = 0
        self.startPos = 0
        self.dead = False
        self.handInput = HandInput()

    def start(self):
        """
        This is the start event called once all Qt Widgets are fully initialized.
        Here we can then access the widgets safely and setup various variables.
        """
        textureNames = ['mario_standing.png', 'mario_run1.png', 'mario_run2.png',
                        'mario_run3.png', 'mario_slide.png', 'mario_jump.png']
        for path in textureNames:
            self.rightTex.append(self.window.gameScreen.loadImageTexture('./MarioAssets/MarioRight/' + path))
            self.leftTex.append(self.window.gameScreen.loadImageTexture('./MarioAssets/MarioLeft/' + path))

        self.gameObjectHandler.world.gravity = (0, -20)
        self.window.gameScreen.cameraScale = 0.15 / self.getWidth()
        self.y_pos = self.position[1] + 0.285
        self.startPos = (self.body.position[0], self.body.position[1])

    def fixedUpdate(self):
        """
        AggiEngine is a multi-threaded application running on 3 different threads and loops.
        It is important to understand the difference between the GUI, Physics, and Rendering threads.
        Fixed Update ensures that physics related data types are accessible and able to be modifiable.
        This event always occurs immediately after Box2D has been updated.
        """
        self.window.gameScreen.cameraPosition = [self.position[0] - 0.275, self.y_pos]
        if self.window.gameScreen.cameraPosition[0] > -0.715:
            self.window.gameScreen.cameraPosition[0] = -0.715
        elif self.window.gameScreen.cameraPosition[0] < -12.65:
            self.window.gameScreen.cameraPosition[0] = -12.65

        if self.position[1] < -1 or self.dead:
            self.body.position = self.startPos
            self.body.linearVelocity = [0, 0]
            self.dead = False

    def update(self):
        """
        AggiEngine is a multi-threaded application running on 3 different threads and loops.
        It is important to understand the difference between the GUI, Physics, and Rendering threads.
        Update ensures that OpenGL data types are accessible and able to be modifiable.
        This event always occurs IMMEDIATELY after OpenGL has finished rendering.
        """

        if self.timing > 1:
            self.frame += 1
            self.timing = 0

        if self.frame == 3:
            self.frame = 0

        self.timing += 0.2

        if abs(self.body.linearVelocity[0]) > 1 and self.running:
            if self.body.linearVelocity[0] > 0:
                self.textureID = self.leftTex[self.frame + 1]
            else:
                self.textureID = self.rightTex[self.frame + 1]
        elif abs(self.body.linearVelocity[0]) > 0.5:
            if self.body.linearVelocity[0] > 0:
                self.textureID = self.leftTex[-2]
            else:
                self.textureID = self.rightTex[-2]

            self.frame = 0
        else:
            if self.body.linearVelocity[0] > 0:
                self.textureID = self.leftTex[0]
            else:
                self.textureID = self.rightTex[0]

            self.frame = 0

        if self.jumping:
            if self.body.linearVelocity[0] > 0:
                self.textureID = self.leftTex[-1]
            else:
                self.textureID = self.rightTex[-1]

        handDelta = self.handInput.getHandInput()
        print(handDelta)

        if abs(handDelta[0]) > 0.1:
            self.body.linearVelocity = (32 * handDelta[0], self.body.linearVelocity.y)
            self.running = True
        else:
            self.running = False

        if handDelta[1] < 0.4 and self.jumps < 2:
            self.body.linearVelocity = (self.body.linearVelocity.x, 10)
            self.jumps += 1

    def keyPressed(self, event):
        """
        Trigger when a key is pushed down or held.
        :param event: Contains information related to the keyPressed event
        """
        if event.key() == Qt.Key_A:
            self.body.linearVelocity = (8, self.body.linearVelocity.y)

        if event.key() == Qt.Key_D:
            self.body.linearVelocity = (-8, self.body.linearVelocity.y)

        if event.key() == Qt.Key_Space and self.jumps < 2:
            self.body.linearVelocity = (self.body.linearVelocity.x, 10)
            self.jumps += 1

        if event.key() == Qt.Key_A or event.key() == Qt.Key_D:
            self.running = True
        else:
            self.running = False

    def beginContact(self, body):
        """
        Begin Contact is an event related to Box2D is it called DURING the Box2D update.
        This event is triggered when a body begins colliding with another body, but it is NOT triggered again
        if the two bodies have not separated.
        :param body: the Box2D body we're colliding with
        """
        self.jumping = False
        self.jumps = 0

    def endContact(self, body):
        """
        Begin Contact is an event related to Box2D is it called DURING the Box2D update.
        This event is triggered when a body stops colliding with another body, but it is NOT triggered when Box2D
        finishes calculating a collision the bodies have move away from one another.
        :param body: the Box2D body we're colliding with
        """
        if abs(self.body.linearVelocity[1]) > 0.5:
            self.jumping = True

    def exit(self):
        self.handInput.exit()
