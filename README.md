# OoT HFR

Early test release.

A fan patch that runs The Legend of Zelda: Ocarina of Time (USA 1.0) at higher frame rates on N64 hardware. Game logic stays at the original 20 updates per second, so the game does not run faster.

> **This is a fork** of [64-bites/oot-hfr](https://github.com/64-bites/oot-hfr). It adds two optional ROM changes, normal (non-inverted) aim and faster text. See [Fork options](#fork-options). Fork patcher page: **https://abarchin.github.io/oot-hfr/**

**Original patcher page: https://64-bites.github.io/oot-hfr/**

No ROM comes with this patch. You need your own legally obtained copy of the game. This project is free, and it is not affiliated with or endorsed by Nintendo.

## Install

1. Open the patcher page.
2. Choose your USA 1.0 ROM. `.z64`, `.n64` and `.v64` files all work. The ROM stays on your computer, and the page does not upload or store it.
3. Your browser saves `OoT HFR (fork).z64` on the fork page (`OoT HFR.z64` on the original page). Your original file does not change.
4. Copy that file to your flash cart, or open it in an emulator.

The patcher rejects any other version of the game. It checks your ROM and the result by MD5.

To use your own patcher, take the BPS file from the Releases page and apply it to a `.z64` ROM.

## Fork options

This fork adds two options to the patcher page, both on by default:

| Option | What it does |
|---|---|
| Normal aim | Pushing the stick up aims up instead of down. It covers first-person aiming with the bow, slingshot and hookshot, the C-up view, and aiming a ranged item in third person. Turn it off for the original inverted aim. |
| Faster text | Text appears twice as fast, the same change as Patcher64+'s "2x Text Speed". Ruto's confession stays at normal speed, and the pauses after Phantom Ganon's defeat are longer, to keep their timing. |

The options are small `.hfro` patches in `options/` that the page applies after the HFR patch. `tools/build_options.py` builds them from the HFR ROM and lists each edit with its offset. The options do not touch the first 1 MiB of the ROM, so the boot checksum does not change. The patcher checks each result by MD5:

| Options | MD5 |
|---|---|
| None | `a7a3528afce3d04a36534a9854ae343e` |
| Normal aim | `240cc199490674141626911c31eba87f` |
| Faster text | `70f4182dbcc0779b4e8ddd7a1fb259d1` |
| Both | `f300d71debbfc0e67aff45c34aa7bd05` |

## Requirements

- USA 1.0 ROM, MD5 `5bd1fe107bf8106b2ab6650abecd54d6` (`.z64` byte order). The patched ROM has MD5 `a7a3528afce3d04a36534a9854ae343e`.
- An Expansion Pak for the settings below. Without one, the game runs as Standard with full anti-aliasing, and hides these settings.

## Settings

- **Before you start a game:** on the file select screen, open Options and move down to Performance. Move the stick left or right to change it. Anti-aliasing is the next row down, then Flipbooks.
- **During a game:** press Start, then B, move the stick down to Options, and press A. Move to a row and press A to choose it. The last two rows switch Anti-aliasing and Flipbook animations. Press B to return. Changes take effect when the pause menu closes.

The game remembers your settings.

| Performance | What it does |
|---|---|
| Standard (20 fps) | The original frame rate. |
| Enhanced (up to 30 fps) | Falls to 20 under load, to keep the pacing even. |
| Variable (smoothed) | Up to 60 fps. Lowers its target under load, to keep the pacing even. |
| Variable | Up to 60 fps. Never lowers its target, so the pacing may vary. |

| Anti-aliasing | What it does |
|---|---|
| Full | The original edge smoothing. |
| Reduced | Draws room surfaces faster, with less smoothing on their edges. The higher rates are easier to hold. |

| Flipbook animations | What it does |
|---|---|
| Enhanced | Gives effects that the game animates picture by picture, such as explosions, flames and smoke, new in-between pictures at the higher frame rates. Their color fades are smooth too. It also gives the flickering energy balls of Phantom Ganon and Ganondorf a new angle in every picture. |
| Original | Shows only the game's own pictures. |

## What to expect

The higher settings are for overclocked hardware. Rates depend on your console and the scene. The FPGA rows are bench results from 13 scenes on a scripted walk, measured on an earlier version with full anti-aliasing. Real play can differ.

| Console | Enhanced | Variable (smoothed) |
|---|---|---|
| FPGA N64, overclocked | 30 fps in all 13 scenes | 58 fps or better in 9 of 13 scenes |
| FPGA N64, stock speed | About 30 fps in 4 of 13 scenes, 20 to 24 in the others | About 30 fps in 5 of 13 scenes, 19 to 25 in the others |
| Original N64 console | In play, mostly 20 fps, and 30 fps when few actors are on screen | Not measured |

In play at stock speed, expect mostly 20 fps, the same as the original game. 30 fps holds only when little is on screen.

On an overclocked FPGA N64, Reduced anti-aliasing gave about 5 to 6 fps more in busy scenes at 60 fps.

## Known limits

- Some motion can still look stepped at high frame rates: the start of a thrown cuckoo's arc, and the slow drift of some water textures.
- At the fastest point of a sword swing, the blade and its trail move 20 times a second for one game update.
- When Volvagia comes out of the lava, its large clouds of fire can drop the rate to 20 fps for a second or two. At high frame rates, the console must draw these clouds more often than the original game does.
- During the Song of Storms, the color fade of the layer over the screen changes 20 times a second.
- Some things that the game turns to a random angle at each update keep that flicker at 20 per second, by design, while their movement is smooth: the pieces of a rupee broken in the shooting gallery and, with Flipbook animations set to Original, Phantom Ganon's and Ganondorf's energy balls.
- The patch is tested on an FPGA N64 and an original N64, each with a flash cart, and in the ares emulator.

## Changes

**v0.5.0**

- Fixes characters, enemies and chests that could fail to appear in busy rooms. In the Fire Temple, this could leave a room's doors shut. With an Expansion Pak, the game now gives them a much larger block of memory.
- The effects of the songs are smooth at high frame rates: the Song of Time's blue vignette, and the effects of Epona's Song, Saria's Song, Scarecrow's Song, the Song of Storms and the Sun's Song.
- In the Fire Temple, the puffs of fire from the flame jets and the fireballs of the moving fire platform no longer move back and forth.
- The Great Fairy's sparkles are smooth at high frame rates.
- Smoother at high frame rates: the Poe Sisters' torches and flame trails, the fireballs of Anubis, the glow of the light that the Mirror Shield reflects, and the floor tiles that fall in Ganondorf's fight.
- Fixes a rare fault: when the game skipped drawing an update because its drawing memory was full, the next pictures could use old data.

**v0.4.0**

- New setting, Flipbook animations, in both Options menus. Enhanced (the default) gives effects that the game animates picture by picture new in-between pictures at the higher frame rates: explosions, flames, smoke, hit sparks, dust, Barinade's electricity, the Biri jellyfish's tentacles, the lava in Dodongo's Cavern and more. Their color fades are smooth too. Enhanced also gives the flickering energy balls of Phantom Ganon and Ganondorf a new angle in every picture. Original shows only the game's own pictures.
- Sword trails now grow with the blade instead of reaching ahead of it. The same holds for arrows, the boomerang and the weapons of enemies such as Stalfos, Lizalfos and Iron Knuckles.
- Smoother at high frame rates: the boomerang, the hookshot's chain, Phantom Ganon's and Ganondorf's energy balls, the light around a new sage, the flames in the Deku Tree Sprout's story, the walls inside Jabu-Jabu's Belly, the waterfall under King Zora, rolling Gorons, the pieces of a rupee broken in the shooting gallery, Freezards, Morpha's core, Volvagia's mane, and the fishing rod, lure and line.
- The pause menu's item cursor shows again. In v0.3.0 it could be missing.

**v0.3.0**

- In the pause menu's Options card, A chooses a row and the card stays open. B returns. The card now covers the whole save page.
- Smoother at high frame rates: horses, the Z-targeting triangles and the arrow over a target, the Z-targeting letterbox bars, the fade when you enter a house, the wipe between some scenes, and moving textures such as water, waterfalls, lava and torch flames.
- The fade when you enter a house now also covers the corners of the screen. The original game leaves them uncovered, and modern displays show them.
- Opening the pause menu no longer flashes garbage at the top of the screen.

**v0.2.0**

- New Anti-aliasing setting. Reduced draws room surfaces faster.
- With the Expansion Pak, the depth buffer uses the Pak's memory. Drawing is slightly faster, mostly at stock speed.
- The sky no longer stutters when you switch to first person or pan the camera quickly.
- The camera no longer hitches when it pans past the sun.
- The Great Fairy's appearance, and Link as he walks in her fountain, no longer look stepped.
- Auto-jumps, Z-targeting backflips and rolling uphill no longer look stepped. A thrown cuckoo is smooth after the start of its arc.
- At 60 fps, the motion stays even when the console falls behind for a moment.

**v0.1.0**

- First test release.

## How it was made

Made with [Claude Code](https://claude.com/claude-code), an AI coding agent, working from the [Ocarina of Time decompilation project](https://github.com/zeldaret/oot).

The patcher page uses modules from [Rom Patcher JS](https://github.com/marcrobledo/RomPatcher.js) by Marc Robledo, under the MIT License.
