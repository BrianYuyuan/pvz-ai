# PvZ-AI

A Python AI bot that plays *Plants vs. Zombies* using computer vision. It uses screenshots to analyze the game state, tracks zombies, and uses a heuristic scoring function to determine which plants to plant and where, then simulates mouse clicks using pyautogui. The current version can reliably complete Level 1-1.

## Features

- **Screen Perception**: Template matching to locate Sun, zombies, and plant cards
- **Card Status Detection**: Determines cooldown status and whether there is enough Sun based on HSV brightness
- **Zombie Tracking**: Cross-frame correlation of detection results to output the row and column coordinates of each zombie on the lawn
- **Decision-Making Layer**: One scoring function per plant; selects the optimal planting location by comprehensively considering zombies on the field, existing plants, sunlight reserves, and the game phase
- **Waiting Logic**: If the optimal solution requires more sunlight than the current reserve and the difference is worth waiting for, the current round is actively skipped

## Architecture

'''
screenshot

↓

Perception Layer  →  Sunlight Collection / Zombie Location / Card Availability

↓

Tracking Layer  →  Zombie Tracker (Cross-frame merging, cleared upon timeout)

↓

Decision Layer  →  Per-plant scoring → Candidate ranking → Select the best affordable option

↓

Action Layer  →  Click plant card + click lawn cell
'''

## Dependencies

- Python 3.10+
- opencv-python
- numpy
- pyautogui
- pygetwindow
- keyboard

```bash
pip install opencv-python numpy pyautogui pygetwindow keyboard
```

## Usage

1. Launch PvZ, enter a level, and wait until the screen shows that zombies are about to appear.
2. Run `python play_game.py`.
3. Switch back to the PvZ window within 3 seconds.
4. Press `Esc` to exit.

All configurable parameters are centralized in `config.py`, including lawn coordinates, template matching thresholds, and scoring weights for each plant.

## Scoring Function Design

Each plant has its own scoring function, which evaluates performance based on several factors:

- **Base Position Score**: Bonus for being positioned to the left (Sunflowers, defensive plants) or centered (Nuts)
- **In-Row Threat Detection**: Offensive plants receive a bonus if there are zombies in the same row; Sunflowers receive a penalty
- **Teammate Coordination**: Scores decrease if there are already plants of the same type in the same row (to avoid overcrowding)
- **Conflict Avoidance**: Do not place Peashooters or Nuts in front of Ash Plants
- **Time-Based Factors**: Bonus points for Sunflowers and Potato Mines in the early game

## Known Issues

- The AI occasionally uses Nuts to block its own Potato Mines
- Sun count is an estimate based on “collection events × 25”; prolonged play may cause deviation from actual values
- No OCR sun count; relies on estimates
- Hard-coded for a single level; no cross-level generalization
- Failed planting (clicking on an existing plant) leaves the card selected, interfering with subsequent clicks; currently resolved by right-clicking as a fallback

## Roadmap

- [ ] OCR for Sun Count, replacing estimates
- [ ] “Triggered” event detection for Ash Plants (visual verification instead of a timer)
- [ ] Optimization of scoring function parameters (offline analysis based on JSONL logs)
- [ ] Support for more levels / plants / scenes (night, pool)

## Design Notes

A few decisions worth noting:

**Why use HSV luminance instead of direct RGB detection for card status?** PvZ cards darken overall when on cooldown; the V channel in HSV directly reflects luminance, making it more stable than averaging the three RGB channels. By sampling the top 8-pixel band of the card (to avoid pattern details), the luminance difference between “ready” and “on cooldown” remains stable at 150 vs. 40.

**Why use pixel distance instead of row and column indices for zombie tracking?** Row and column indices are too coarse (80×100-pixel grid), and a single zombie flickering at the edge of a grid cell would be mistaken for a new zombie. Using a pixel distance threshold (100px) directly maintains identity continuity.

**Why is there a WAIT_MARGIN parameter?** A short-sighted, greedy strategy would cause the AI to plant potato mines as soon as it sees 25 sunlight, never saving up enough for peas. WAIT_MARGIN ensures the AI chooses the immediate option only when the gap between the “optimal solution” and the “affordable optimal solution” is small enough (≤20 points); when the gap is large, it prefers to wait.

