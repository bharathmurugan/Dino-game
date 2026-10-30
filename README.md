# Dino Run — Cinematic Edition

A browser endless-runner inspired by the Chrome offline dinosaur game, rebuilt with a cinematic presentation. The whole project is one Python file: Flask serves a single page that contains the HTML, CSS, and JavaScript, and the game runs on an HTML5 canvas.

When the screen "powers off," a CRT-style shutdown plays, followed by a glowing title card. Press **Start Run** to play.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Game](#running-the-game)
- [Controls](#controls)
- [Gameplay](#gameplay)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Power-off intro:** a white flicker, then a CRT-style collapse that reveals the game card
- **Cinematic scene:** gradient sky, twinkling starfield, pulsing sun, parallax mountain layers, and drifting clouds
- **Animated dinosaur:** running legs, periodic blinking, jumping, and ducking
- **Three obstacle types:**
  - Cactus clusters (one or two cacti)
  - Rocks
  - Pterodactyls, which appear after 200 points and fly at three heights, so you must jump or duck
- **Increasing difficulty:** speed ramps up with score, capped at a maximum
- **Particle effects:** a burst on collision and a golden burst every 100 points
- **Persistent high score:** stored in the browser's `localStorage`
- **Pause and restart:** pause at any time, and restart from the game-over screen
- **Single-file deployment:** no build step and no static asset folder

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Rendering | HTML5 `<canvas>` (2D context) |
| Storage | Browser `localStorage` |

## Requirements

- Python 3.8 or newer
- pip
- A modern browser (Chrome, Edge, Firefox, or Safari)

## Installation

Clone the repository and install Flask:

```bash
git clone https://github.com/bharathmurugan/dino-game.git
cd dino-game
pip install flask
```

On Windows, you can also run the install in Command Prompt or PowerShell from the project folder.

## Running the Game

```bash
python app.py
```

The server starts in debug mode. Open **http://127.0.0.1:5000** in your browser.

> Debug mode is for development only. Turn it off (`app.run()` without `debug=True`) before deploying.

## Controls

| Key | Action |
| --- | --- |
| `Space` or `↑` | Jump |
| `↓` (hold) | Duck |
| `P` | Pause or resume |

Jumps and ducks are ignored while the game is not running. The **EXIT** button in the bottom-right corner returns you to the title card.

## Gameplay

- Your score rises every frame you survive. The top-left HUD shows the current score, and the top-right shows the best score.
- Hitting any obstacle ends the run. The game-over screen shows your final score and a **Run Again** button.
- The game gets faster as the score grows, so timing matters more the longer you last.
- Pterodactyls only appear after 200 points, so early runs are cacti and rocks only.

## Project Structure

```
dino-game/
├── app.py        # Flask server, HTML, CSS, and JavaScript for the game
└── README.md     # This file
```

Everything is in `app.py`. The HTML template is stored in the `PAGE` string, and the Flask route `/` returns it.

## How It Works

**Server.** Flask defines one route, `/`, which renders the `PAGE` template with `render_template_string`. The server does not handle game state, so the game runs entirely in the browser.

**Intro sequence.** Two timers control the opening. At 1.4 seconds, the `collapse` class starts the CRT animation. At 2.3 seconds, the power screen is hidden and the title card appears.

**Game loop.** `requestAnimationFrame` drives `update()` (physics, spawning, collision, scoring) and `render()` (drawing). The loop stops when the player crashes and restarts on Run Again.

**Physics.** The dinosaur has gravity (`G = 0.65`) and a jump velocity (`JUMP_V = -12.5`). It can only jump while on the ground.

**Collision.** Each entity has a bounding box. A 4-pixel padding is subtracted on every side, so near-misses don't count as hits. Ducking uses a shorter, wider box.

**Spawning.** Obstacles spawn on a timer that shortens as speed increases, with a random chance of extra spawns. Cactus clusters are the most common, followed by rocks and then pterodactyls.

**High score.** When a run ends, the score is compared with `localStorage["dino_hi"]` and saved if it's higher.

## Customization

Most tuning values live near the top of the `<script>` block in `app.py`:

| Setting | Location | Effect |
| --- | --- | --- |
| `G` | `const G = 0.65` | Gravity. Higher values make jumps shorter. |
| `JUMP_V` | `const JUMP_V = -12.5` | Jump strength. More negative means higher jumps. |
| Starting speed | `speed = 6` in `resetGame()` | How fast the game begins. |
| Speed cap | `Math.min(6 + score / 300, 16)` in `update()` | Maximum speed. |
| Pterodactyl threshold | `score > 200` in `spawnObstacle()` | Score at which pterodactyls start appearing. |
| Colors | `:root` variables in the `<style>` block | Sky, sun, ground, and accent colors. |

## Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`:** run `pip install flask`.
- **Port 5000 is in use:** change the port with `app.run(debug=True, port=5001)` and open that port.
- **Game doesn't respond to keys:** click the page once so it has focus, then press Start.
- **High score resets:** `localStorage` is per browser and per address. Using a different browser or `127.0.0.1` vs `localhost` gives a separate score.
- **Jumps feel too floaty or too sharp:** adjust `G` and `JUMP_V` as described in Customization.

## Roadmap

- Mobile touch controls
- Sound effects and background music
- Day and night cycle
- Difficulty modes
- Saving the high score on the server instead of the browser

## Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push the branch: `git push origin feature/your-feature`.
5. Open a pull request.

## License

No license has been chosen yet. Add a `LICENSE` file (for example, MIT) before others reuse the code.
