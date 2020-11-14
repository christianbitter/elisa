# elisa
A collection of Pygame - python game programming - tutorials focused on 2D games, starting from a simple template and gradually moving up the ladder.

## Introduction and Motivation

Elisa is the set of examples and actual game code produced for personal education and my blog. The code is intended to guide you from being a beginner in 2D game programming using pygame to a beginner with some finished studies and game prototypes using pygame and a concrete idea for where to look further in order to advance your game development skills.

There is a host of topics that is typically associated with programming a game. In order to avoid having to deal with too many things at once, we deliberately limit each example to a specific aspect, such as drawing a shape or a sprite, using keyboard input etc. Whenever, the concept is presented (this includes I am exploring it as well), it is presented in a visible form in the code. However, in later elisa samples, we may already build upon some discovered feature or functionality and use its absorbed form, i.e. from the elisa package.

Note, as this is a living project you will (initially) not find elisa files for all aspects of a somewhat advanced game, but only
some starter code that deals with standard (and simple but fun) issues you would encounter researching the topic yourself.  You may realize that over time the code files change or certain topics are introduced "between" alrady existing topics - whenever I feel there should have been something explained differently, a bug needs fixing, etc. ... invariably this will happen. Furthermore, the code presented may not be the most advanced or best optimized piece of finished work, but it should get you and myself off the ground.

In certain cases you will see files with no actual content. In these cases the files act as a placeholder, for content I believe s relevant at that state but needs to be fleshed out.

Lastly, our github-based blog discusses some of the developments happening here. So if you are the reader type, just head over to <https://christianbitter.github.io/>.

With that - Enjoy and Build!

## Mapping Intent to Source

- **start_template.py**:  
A simple template to kick our coding off. It is based on the official pygame starter code.
- **elisa_0_init.py**:  
Based of the initial template, we are going to look into pygame initialization procedures to arrive at a point where we have a displayed window and a double-buffer based drawing setup. For simplicity's sake we only fill the drawing canvas with white colour. But stay tuned for future examples.
- **elisa_0_1_drawing_shapes.py**:  
This is a simple example, building on geometric primitives provided by the pygame.draw module. Specifically, we are going to draw a circle, square, polygon and some lines. Part of the drawing, will make use of some basic linear algebra (projection of 2D vectors). This is a very basic, non-animated example, to show the composition of scenes from basic pygame elements.
- **elisa_1_spritesheet.py**:
- **elisa_2_animation.py**:
- **elisa_3_multiple_animation.py**:
- **elisa_5_statemachine.py**:
- **elisa_6_environment_map.py**:  
In this example, we take what we learnt about displaying sprites and define a simple list-based environment map structure. This structure lays out our game world in terms of different atomic environmental entities, i.e. tiles. For this example, there are only a limited number of tiles and the game world is really just a 2D grid with no life in it.
- **elisa_7_anim_statemachine.py**:
- **elisa_8_-_tilemap.py**:  
This example combines our foray into drawing a tiled game world introduced in elisa_6 and what we learnt in terms of expressing behaviour and animation using a statemachine. Consequently, this example greets you with a simple tile map world in which you can steer a simplistic game character up, down, left or right. The steering is controlled by the mentioned state machine. Since, the visual for our moving friend are somewhat simplistic no animation highlights the notion of dynamic behaviour. But for that we have our beloved elise character, who is waiting idly in the middle of the screen.
- **elisa_9_particles.py**:
- **elisa_10_screens.py**:
- **elisa_12_sound.py**:  
This is a quite simplistic example that does not involve a lot of visual trickery (apart from the instructional text). Here, we simply play a single sound when the player presses a mouse button. The longer the mouse button is pressed, the longer the sound is played.
- **elisa_14_camera.py**:
- **elisa_16_-_ecs.py**:
- **elisa_18_actor_camera.py**:  
This is an integrated example binding together the composition of scenes via the entity-component-system approach (shown in elisa_16_-_ecs) and **allowing** for independent of game world specification and its depiction via a camera (introduced in elisa_14_camera). Now, what this example does is the following. The player represented by a simple circle, moves through a simple environment depicted by multiple somewhat arbitrarily placed boxes. A camera is setup that follows the player, i.e. the camera is offset by -50 in x and y from the player's position. When moving through the scene, you will see that objects are moved and eventually drop out of view, which is the expected behaviour. Furthermore, through the camera's internal transformation pipeline from world space to normalized clip space and then to viewport space, a very simple visibility test is implemented, which does not draw objects that are fully outside of the camera's field of reception.

## Credits and References

(c) Copyright Christian Bitter 2020