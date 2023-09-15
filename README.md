# Rock, Paper, Scissors - The Game!

This repository contains the code for a dynamic visual representation of the classic game "Rock, Paper, Scissors", but with a twist! Instead of just two players, multiple entities (rocks, papers, and scissors) move around the screen, colliding and "playing" with any other entity they bump into.

## Table of Contents

- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [How to Play](#how-to-play)
- [Configuration](#configuration)
- [Credits](#credits)

## Features

- **Dynamic Interaction**: Elements (Rock, Paper, Scissors) move around the screen and interact when they collide.
- **AI Movement**: Elements can optionally be controlled by AI, making them "hunt" their prey and "flee" from their predators.
- **Game Speed Control**: The speed of the game can be controlled in real-time.
- **Statistics**: View game statistics once a winning element type remains.
- **Custom Game Parameters**: Control the number of each element type at the beginning of the game.

## Setup and Installation

1. Clone this repository.
2. Ensure you have Python and Pygame installed.
3. Run `python rpc-game.py` to start the game.
4. Enjoy!

## How to Play

1. Set the initial number of Rocks, Papers, and Scissors using the startup window.
2. Start the game and watch them interact!
3. Control the game speed using the `+` and `-` keys or the mouse wheel.
4. Pause/Resume the game using the `Space` key.
5. Watch until one type of element remains. This type will be the winner!

**Controls**:
- `+`: Increase game speed.
- `-`: Decrease game speed.
- `Space`: Pause/Resume game.

## Configuration

A settings window is provided to adjust game parameters like the speed multiplier, normal speed, hunting speed, fleeing speed, and view range. The game saves these configurations in a `.ini` file for future use.

## Credits

- **Images**: The element images (rock, paper, and scissors) used in the game are placeholders. Feel free to replace them with your preferred graphics.
- **Development**: This game was developed as a fun project to understand game dynamics, AI movement, and Pygame interactions.

---

**Note**: This is a fun representation of the Rock, Paper, Scissors game and is meant for entertainment and educational purposes. It doesn't strictly adhere to the classic game rules.

