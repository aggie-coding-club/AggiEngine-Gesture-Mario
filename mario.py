from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QLabel

import AggiEngine as ag
from goomba import Goomba
from player import Player


class StartMenu(ag.State):

    def __init__(self, ui_path):
        """
        The initialize doesn't serve much purpose in the context of AggiEngine, here you can name your variables.
        However many of the useful properties of the State superclass have not been initialized.
        :param ui_path: This the path of the .ui file describing the GUI to display.
        """
        ag.State.__init__(self, ui_path)

    def start(self):
        """
        This is the start event called once all Qt Widgets are fully initialized.
        Here we can then access the widgets safely and setup various variables.
        """
        print('Starting StartMenu')
        self.window.setWindowIcon(QIcon('./MarioAssets/MarioRight/mario_standing.png'))   # window icon

        # connect the click event to changeState and the state we want
        self.window.findChild(QPushButton, 'playButton').clicked.connect(self.loadGame)

    def loadGame(self):
        self.window.stateManager.changeState(Game('MarioAssets/game.ui'))


class Game(ag.State):

    def __init__(self, ui_path):
        """
        The initialize doesn't serve much purpose in the context of AggiEngine, here you can name your variables.
        However many of the useful properties of the State superclass have not been initialized.
        :param ui_path: This the path of the .ui file describing the GUI to display.
        """
        ag.State.__init__(self, ui_path)
        self.label = None

    def start(self):
        """
        This is the start event called once all Qt Widgets are fully initialized.
        Here we can then access the widgets safely and setup various variables.
        """
        print('Starting Game')
        self.window.showFullScreen()
        self.label = self.window.findChild(QLabel)
        self.label.setVisible(False)
        self.loadMap('MarioAssets/mario1-1.tmx')  # loads the tile map and generates game objects

    def fixedUpdate(self):
        """
        AggiEngine is a multi-threaded application running on 3 different threads and loops.
        It is important to understand the difference between the GUI, Physics, and Rendering threads.
        Fixed Update ensures that physics related data types are accessible and able to be modifiable.
        This event always occurs immediately after Box2D has been updated.
        """
        if self.label.isVisible():
            self.label.setText('Fixed FPS: {:.3f}\nScreen FPS: {:.3f}\nGame Objects: {}'.format(
                self.window.fixedFps, self.window.screenFps, len(self.gameObjectHandler.gameObjects)))

    def keyPressed(self, event):
        """
        Trigger when a key is pushed down or held.
        :param event: Contains information related to the keyPressed event
        """
        if event.key() == Qt.Key_I:
            self.label.setVisible(False if self.label.isVisible() else True)


state = Game('MarioAssets/game.ui')
#state = StartMenu('MarioAssets/start_menu.ui')
app = ag.Application(state, screenFps=60, fixedFps=60)  # starts the application at 60 hz screen, and 60 hz physics
app.run()
