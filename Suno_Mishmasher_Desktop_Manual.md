# Suno Style Mishmasher Desktop Manual

## Purpose

Suno Style Mishmasher is a creative prompt-building tool for Suno. It helps you generate compact music style prompts by combining genres, instruments, moods, playing directions, vocal styles, eras, and production notes.

The goal is not strict music theory accuracy. The goal is fast creative exploration, controlled hybridisation, and discovering style combinations you may not have thought of manually.

## Recommended Basic Workflow

1. Type a starting idea in Base prompt, for example `grunge rock with cinematic atmosphere`.
2. Choose a Base style if you have one that matches the idea.
3. Keep Mode on `Coherent` for sensible outputs.
4. Set Cohesion high, usually 80-100%, if you want the result to stay close to the chosen style.
5. Set Mutation / Weirdness low, around 0-15%, if you want small variations rather than wild genre jumps.
6. Click Generate.
7. Copy the Main prompt into Suno.
8. If you want exclusions, copy the separate Negative prompt into Suno's negative prompt field.

## Main Prompt vs Negative Prompt

The Main prompt contains only the positive musical direction you want Suno to follow.

The Negative prompt is separate. It contains things to avoid, such as unwanted genres, instruments, or vocal styles.

The app intentionally does not add avoid instructions to the main prompt. Suno has a separate negative prompt field, so avoid/exclusion material is kept separate.

## Key Controls

### Base Prompt

The Base prompt is your starting text. It is always kept at the front of the generated main prompt.

### Append Extras to Base Prompt

When enabled, the app treats your Base prompt as the core identity and mainly appends instruments, moods, playing directions, vocals, eras, and production notes. This prevents the generator from stuffing too many extra genre names into the main prompt when you already typed the genre yourself.

### Base Style

A Base style is an association profile. It tells the app which musical ingredients usually belong together.

### Use Association Engine

This is the main smart-generation switch. When enabled, the app uses base styles, blend styles, source filters, exclusions, mutation candidates, and weighted association pools. When disabled, the app behaves more like a flat randomiser.

### Mode

Coherent keeps the output controlled and sensible.

Experimental still uses the association engine but leans harder into mutation candidates.

Chaos ignores associations and pulls broadly from the database.

Focused keeps prompts shorter and tighter.

Dense adds more ingredients.

### Cohesion

Cohesion controls how strongly the generator follows the selected base style, blend styles, or source filter.

### Mutation / Weirdness

Mutation controls how much the app uses mutation candidates from associations.

### Keep Base Style Represented

This forces the selected base style's core genre to remain represented in the output.

### Blend Multiple Base Styles

Blend mode actively combines several selected base styles into one prompt. Each selected style has a weight slider.

### Prompt Source Filter

Prompt Source Filter limits what the generator is allowed to draw from. Blend is the recipe. Source Filter is the allowed pantry.

## Strict No-Bleed Settings

Use these when you do not want unrelated genres appearing:

- Mode: Coherent
- Use Association Engine: On
- Cohesion: 100%
- Mutation / Weirdness: 0%
- Allow Excluded Pairings: Off
- Prompt Source Filter: On
- Select only the allowed base styles

## Prompt Variants

Generate Variants creates 3-5 prompts using the current locked-in settings. This is useful when you like the current direction but want several nearby alternatives to try in Suno.

## Prompt History

The app keeps the last 10 generated prompts in the Prompt History panel. You can restore or copy a previous prompt.

## Saved Settings

The app remembers generation preferences between sessions, including mode, cohesion, mutation, base style, blend settings, source filter selections, ingredient counts, and max characters. Temporary prompts are not saved as preferences.

## Import Packs

Import Packs are the easiest way to add many styles at once. They create or update associations and sync missing values into the database.

## Python / iOS Sync

The Python and iOS versions are designed to share compatible JSON structures. Use full database export/import when you want both versions to have the same complete data. Use pack export/import when you only want to move base styles/associations.

## Practical Tips

- Use Base Prompt when you already know the idea.
- Use Base Style when you want the app to understand the musical DNA.
- Use Blend when you want a deliberate hybrid.
- Use Source Filter when you want to prevent genre bleed.
- Use Negative Prompt when certain instruments or styles keep appearing unwanted.
- Use Variants when you like the current direction and want several nearby alternatives.
- Use Import Packs to grow the app quickly.

## Troubleshooting

Problem: unrelated genres appear.  
Solution: enable Prompt Source Filter, set Cohesion to 100%, Mutation to 0%, and disable Allow Excluded Pairings.

Problem: prompts feel too samey.  
Solution: increase Mutation, lower Cohesion slightly, or switch to Experimental mode.

Problem: prompts are too long.  
Solution: lower ingredient counts or use Focused mode.

Problem: the app keeps using things you dislike.  
Solution: add them to the Negative prompt or to association exclusions.

Problem: the app does not use a new style from an association.  
Solution: use Sync All Associations to Database or save the association again.

## Final Note

Suno Style Mishmasher is best used as a creative assistant, not a rulebook. Some strange combinations will fail, but some will lead to interesting results you would not have written manually.
