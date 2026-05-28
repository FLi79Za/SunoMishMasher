# Suno Style Mishmasher

Suno Style Mishmasher is a Python desktop utility for generating compact, Suno-friendly music style prompts.

It is designed for creative exploration rather than strict music theory. The goal is to help you discover interesting genre combinations, build coherent style expansions, blend musical identities, and create unusual but usable prompt ideas for Suno.

The app works especially well for exploring hybrid styles, cinematic scoring prompts, metal subgenres, electronic/industrial blends, folk fusions, weird experimental music, and soundtrack-style ideas.

---

## What it does

Suno Style Mishmasher generates music style prompts by combining:

- genres
- instruments
- playing/performance directions
- moods
- eras and production aesthetics
- vocal styles
- production notes
- avoid/exclusion notes

It can generate fully random mashups, controlled variations around a selected base style, or blends of multiple base styles.

Example output:

```text
industrial metal, groove metal, cyberpunk electro; featuring palm-muted rhythm guitars, 808 kick, sub bass, distorted organ; industrial stomp, mechanical quantization, stop-start riffing; paranoid urban tension, cold neon atmosphere; modern cinematic hybrid mix; gritty male lead vocal; tight low end, gritty analogue texture, punchy drums; avoid generic pop chorus
```

Prompts are capped to 1000 characters or less by default, making them suitable for Suno style prompt workflows.

---

## Main features

### Base prompt expansion

You can type a starting idea such as:

```text
grunge rock with cinematic atmosphere
```

The app can then append compatible instruments, moods, playing directions, production notes, and vocal traits while keeping the prompt under the character limit.

This is useful when you already know the rough idea, but want the app to fill in richer musical detail.

---

### Base styles and associations

A **Base Style** is a structured profile that tells the app what usually belongs together.

Each association can include:

- compatible genres
- compatible instruments
- playing directions
- moods
- eras
- vocals
- production notes
- excluded genres
- excluded instruments
- mutation genres
- mutation instruments
- mutation moods

For example, an industrial metal association may favour distorted guitars, mechanical rhythms, synth layers, low-end-heavy production, cyberpunk moods, and exclude folk instruments unless chaos is enabled.

Associations are the main “intelligence layer” of the app.

---

### Style blending

The app supports blending multiple base styles.

This allows combinations such as:

- Industrial Metal + Dark Ambient
- Grunge Rock + Shoegaze
- Sea Shanty Tavern Folk + Thrash Metal
- Cinematic Orchestral + Cyberpunk Synthwave

When blend mode is enabled, the app merges the selected associations and draws from their combined genres, instruments, moods, production notes, exclusions, and mutation candidates.

---

### Coherent, experimental, and chaos generation

The generator supports different creative modes.

**Coherent** keeps the result close to the selected base style or blend.

**Experimental** introduces more mutation candidates and adjacent ideas while still keeping some structure.

**Chaos** ignores associations and pulls freely from the full database for maximum weirdness.

---

### Cohesion and weirdness controls

The app has two important creative controls.

**Cohesion** controls how strongly the result follows the selected base style or blend.

Higher cohesion means:

- safer combinations
- more genre-faithful output
- fewer random elements

Lower cohesion means:

- broader exploration
- more stylistic drift
- more hybridisation

**Weirdness** controls how much the app uses mutation candidates and unusual combinations.

Higher weirdness means:

- stranger instruments
- more unusual genre pairings
- more experimental results

---

### Import packs

The app includes an Import Pack system for adding one or many association profiles at once.

An import pack is a JSON object with this structure:

```json
[
  {
    "name": "Industrial Metal Core",
    "genres": ["industrial metal", "groove metal", "EBM"],
    "instruments": ["palm-muted rhythm guitars", "808 kick", "sub bass"],
    "playing": ["industrial stomp", "mechanical quantization"],
    "moods": ["paranoid urban tension", "cold neon atmosphere"],
    "eras": ["90s industrial metal production"],
    "vocals": ["gritty male lead vocal"],
    "production": ["tight low end", "gritty analogue texture"],
    "excluded_genres": ["sea shanty", "neo-soul"],
    "excluded_instruments": ["accordion", "tin whistle"],
    "mutation_genres": ["trip-hop", "witch house"],
    "mutation_instruments": ["Mellotron choir"],
    "mutation_moods": ["towering cinematic tension"]
  }
]
```

The app can import multiple packs in one go.

When a pack is imported, the app:

- creates or updates the association
- adds missing genres to the master database
- adds missing instruments to the master database
- adds missing moods, eras, vocals, production notes, and playing styles
- skips duplicates
- saves the updated JSON database

This makes it much easier to grow the system over time.

---

### Bulk list import

The app also supports simpler list importing for individual categories.

You can paste or load:

- one item per line
- comma-separated values
- semicolon-separated values
- `.txt`
- `.csv`
- `.json`

This is useful for quickly adding large lists of instruments, genres, moods, or production terms.

---

## Installation

### Requirements

- Python 3.10 or newer recommended
- PySide6

Install PySide6 with:

```bash
pip install PySide6
```

Then run the app:

```bash
python suno_style_mishmasher_import_packs_blend.py
```

If you rename the script, run the renamed file instead.

---

## Database location

The app stores its working database here:

```text
~/.suno_style_mishmasher/style_database.json
```

On Windows, this will usually resolve to something like:

```text
C:\Users\YourName\.suno_style_mishmasher\style_database.json
```

The JSON database is the main source of truth for the app.

It contains:

```json
{
  "genres": [],
  "instruments": [],
  "playing": [],
  "moods": [],
  "eras": [],
  "vocals": [],
  "production": [],
  "avoid": [],
  "bundles": {},
  "associations": {}
}
```

The `bundles` section is kept for backwards compatibility.

The `associations` section is the preferred system going forward.

---

## Typical workflow

### Quick generation

1. Open the app.
2. Type a base prompt, such as `dark industrial metal`.
3. Select a base style if desired.
4. Adjust cohesion and weirdness.
5. Click Generate.
6. Copy the prompt into Suno.

---

### Creating a new association manually

1. Open the Associations tab.
2. Create a new association.
3. Fill in genres, instruments, moods, playing styles, and production notes.
4. Add exclusions if there are things that should normally not appear.
5. Add mutation candidates for controlled weirdness.
6. Save the association.

When saved, missing entries are synced into the master database automatically.

---

### Importing many associations

1. Open the Import Packs tab.
2. Paste a JSON array of pack objects.
3. Click Import.
4. The app creates/updates associations and syncs missing database entries.

This is the recommended way to expand the app quickly.

---

## Generating import packs with an AI assistant

You can ask an AI assistant to create import packs using a prompt like this:

```text
You are generating structured music association packs for a Suno prompt generation system.

Output ONLY valid JSON.
Do not use markdown.
Do not explain anything.
Always return an array of pack objects.

Each pack must use this exact schema:

[
  {
    "name": "Style Name",
    "genres": [],
    "instruments": [],
    "playing": [],
    "moods": [],
    "eras": [],
    "vocals": [],
    "production": [],
    "excluded_genres": [],
    "excluded_instruments": [],
    "mutation_genres": [],
    "mutation_instruments": [],
    "mutation_moods": []
  }
]

Keep entries concise, Suno-friendly, and musically useful.

Generate packs for:
- Industrial Metal Core
- Dark Fantasy Orchestral
- Cyberpunk Synthwave Horror
```

The resulting JSON can be pasted directly into the Import Packs tab.

---

## Design philosophy

The app is not trying to be a perfect musicology tool.

It is designed as a creative style exploration system.

The priority is:

- useful Suno prompts
- interesting hybridisation
- fast experimentation
- reusable music-style associations
- controlled chaos
- easy database expansion

A technically “wrong” genre combination may still be useful if it creates a compelling prompt.

---

## Suggested use cases

Suno Style Mishmasher is useful for:

- discovering genre hybrids
- building cinematic soundtrack prompts
- making metal/electronic/folk fusion styles
- creating weird experimental prompts
- expanding a simple style idea into a richer Suno prompt
- building reusable association packs
- generating multiple variations of a musical direction
- exploring styles you may never have heard of

---

## Notes

The generated prompts are meant as starting points.

Suno may interpret certain genre names, instruments, or directions unpredictably. That is part of the experimentation process.

If a result works well, save the prompt or turn it into a new association pack.

---

## Licence

This project is released under the MIT License.

See the [`LICENSE`](LICENSE) file for the full licence text.

Copyright (c) 2026 Francois Linde
