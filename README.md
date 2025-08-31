# Asteroids – Expanded Version

An expanded and customized version of the classic Asteroids arcade game, originally based on the [Boot.dev guided project](https://boot.dev).  
The Boot.dev version focused on **core mechanics only** — this project builds on that foundation to create a complete game experience with menus, statistics, world expansion, and more.

---
## Status

This project is currently in active development.  
Features, mechanics, and assets may change over time.

---

## Features

- **Complete Game Loop**
  - Main menu, stats menu, and game over menu
  - Persistent in-session **stat tracking** (asteroids destroyed by level, stars collected, shots fired)
- **Larger Play Area** – Move beyond the original single-screen gameplay into a 3×3 world grid.
- **Camera System** – Smoothly pans when the player approaches the edge of the screen.
- **Wrapping Background** – Procedurally generated starfield with layered nebula effects.
- **Asteroid Enhancements**
  - Custom polygon shapes
  - Velocity-based coloring to indicate difficulty
  - Detailed surface textures with rings, craters, and speckles
- **Objectives**
  - Special collectible stars spawn on-screen when certain asteroid levels are destroyed
  - Visible Stars slowly fade/disappear while on visible
- **World Wrapping** – Players, asteroids, and projectiles wrap around the edges of the world.

  - <img width="500" height="500" alt="world connectivity" src="https://github.com/user-attachments/assets/4d464062-1315-4e1e-965a-d995b156d72e" />

- **Dynamic Spawning** – Asteroids spawn relative to the camera’s position for an active game space.

---

## Requirements

- Python **3.12** or newer
- [Pygame](https://www.pygame.org/) **2.6.1**
- (Optional) [NumPy](https://numpy.org/) for certain enhancements or performance benefits

---

## Getting Started

1. Install Python 3.12 or newer.
2. Install the required packages:
   - `pygame==2.6.1`
   - (optional) `numpy`
3. Run `main.py` to start the game.
4. Controls:
   - **Arrow Keys** → Rotate/Move
   - **Shift** → Shoot
   - **M** → Mute/Unmute music

---

## Assets

- This project expects certain **audio assets** in the `assets/` directory (e.g., background music and sound effects).
- These are **not included** in the repository and must be added manually for sound to work.
- You can replace them with your own `.wav` files, or remove audio calls from the code to play without sound.
