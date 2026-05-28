#!/usr/bin/env python3
"""
Suno Style Mishmasher
A desktop GUI for generating <1000 character Suno style prompts by mixing genres,
instruments, production notes, performance directions, moods, eras, and optional
"style bundles" such as thrash metal, synthwave, dark folk, etc.

Dependency:
    pip install PySide6

Run:
    python suno_style_mishmasher.py
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


APP_DIR = Path.home() / ".suno_style_mishmasher"
DB_PATH = APP_DIR / "style_database.json"
PRESET_PATH = APP_DIR / "last_settings.json"
MAX_PROMPT_CHARS = 1000


DEFAULT_DB = {
    "genres": [
        "thrash metal", "groove metal", "doom metal", "blackened folk metal",
        "industrial metal", "post-grunge", "90s alternative rock", "stoner rock",
        "shoegaze", "dream pop", "darkwave", "synthwave", "retrowave",
        "cyberpunk electro", "EBM", "trip-hop", "jungle", "drum and bass",
        "acid jazz", "neo-soul", "gothic country", "dark cabaret", "sea shanty",
        "Celtic punk", "Russian folk", "Balkan brass", "desert blues",
        "Afrobeat", "highlife", "kwaito", "amapiano", "maskandi",
        "Andean folk", "flamenco rock", "surf rock", "spaghetti western",
        "chiptune", "baroque pop", "neoclassical", "minimal techno",
        "witch house", "hauntology", "krautrock", "math rock", "samba rock",
        "tango nuevo", "dub reggae", "psychedelic funk", "sludge blues"
    ],
    "instruments": [
        "twin distorted guitars", "palm-muted rhythm guitars", "wah guitar solo",
        "fretless bass", "fuzz bass", "upright bass", "blast-beat drums",
        "tribal toms", "tight snare", "808 kick", "live hand percussion",
        "accordion", "balalaika", "fiddle", "hurdy-gurdy", "mandolin",
        "nylon guitar", "banjo", "dobro", "sitar", "oud", "kora",
        "shakuhachi", "erhu", "tin whistle", "bagpipes", "theremin",
        "Mellotron choir", "analog synth pads", "FM synth bells",
        "arpeggiated modular synth", "orchestral strings", "brass stabs",
        "choir swells", "taiko drums", "marimba", "vibraphone",
        "field recordings", "vinyl crackle", "sub bass", "distorted organ"
    ],
    "playing": [
        "aggressive downpicking", "galloping rhythm", "syncopated groove",
        "swing feel", "half-time chorus", "double-time bridge",
        "call-and-response vocals", "chant-like backing vocals",
        "layered harmonies", "dramatic key change", "tremolo-picked melody",
        "dissonant chord voicings", "walking bassline", "funky ghost notes",
        "staccato riffs", "legato lead lines", "wide vibrato",
        "motorik pulse", "polyrhythmic percussion", "slow cinematic build",
        "stop-start riffing", "big singalong chorus", "quiet-loud dynamics",
        "tension-and-release arrangement", "improvised solo section"
    ],
    "moods": [
        "playful but melancholic", "darkly triumphant", "haunted and cinematic",
        "reckless tavern energy", "brooding and elegant", "cold neon atmosphere",
        "sun-baked desert mood", "sarcastic and rowdy", "mysterious and ritualistic",
        "dreamy but unsettling", "heroic but tired", "paranoid urban tension",
        "bittersweet nostalgia", "chaotic festival atmosphere", "lonely midnight drive"
    ],
    "eras": [
        "late 80s production", "early 90s metal mix", "mid-90s alternative rock polish",
        "70s analogue warmth", "80s drum machine texture", "2000s compressed rock radio",
        "modern cinematic production", "lo-fi cassette texture", "live tavern recording feel",
        "retro video game soundtrack energy", "arena-sized mix", "underground club mix"
    ],
    "vocals": [
        "gritty male lead vocal", "clean female lead vocal", "raspy gang vocals",
        "low spoken-word verses", "operatic backing vocals", "chanting crowd vocals",
        "whispered intro", "dramatic theatrical vocal delivery", "raw punk vocal delivery",
        "layered call-and-response choir", "no vocals, instrumental"
    ],
    "production": [
        "punchy drums", "wide stereo guitars", "tight low end", "big reverb tails",
        "dry upfront vocals", "cinematic transitions", "distorted tape saturation",
        "clear melodic hook", "bass-forward mix", "crisp transient attack",
        "gritty analogue texture", "high-energy chorus lift", "dark ambient intro",
        "short radio-friendly arrangement", "dynamic arrangement with strong contrast"
    ],
    "avoid": [
        "avoid EDM drop", "avoid generic pop chorus", "avoid cheesy novelty sound",
        "avoid over-polished vocals", "avoid excessive autotune", "avoid thin guitars",
        "avoid slow intro", "avoid spoken dialogue", "avoid comedy vocals"
    ],
    "bundles": {
        "Thrash Metal Variant": {
            "genres": ["thrash metal", "groove metal", "speed metal"],
            "instruments": ["twin distorted guitars", "palm-muted rhythm guitars", "wah guitar solo", "tight snare"],
            "playing": ["aggressive downpicking", "galloping rhythm", "stop-start riffing", "big singalong chorus"],
            "moods": ["darkly triumphant", "reckless tavern energy"],
            "eras": ["early 90s metal mix", "arena-sized mix"],
            "vocals": ["gritty male lead vocal", "raspy gang vocals"],
            "production": ["punchy drums", "wide stereo guitars", "tight low end", "crisp transient attack"],
            "avoid": ["avoid thin guitars", "avoid excessive autotune"]
        },
        "Monkey Island Tavern Folk": {
            "genres": ["sea shanty", "Russian folk", "Balkan brass", "Celtic punk"],
            "instruments": ["accordion", "balalaika", "fiddle", "nylon guitar", "live hand percussion"],
            "playing": ["swing feel", "call-and-response vocals", "chant-like backing vocals"],
            "moods": ["playful but melancholic", "reckless tavern energy", "sarcastic and rowdy"],
            "eras": ["live tavern recording feel"],
            "vocals": ["gritty male lead vocal", "chanting crowd vocals"],
            "production": ["clear melodic hook", "dynamic arrangement with strong contrast"],
            "avoid": ["avoid EDM drop", "avoid generic pop chorus"]
        },
        "Neon Noir Synth": {
            "genres": ["darkwave", "synthwave", "cyberpunk electro", "EBM"],
            "instruments": ["analog synth pads", "FM synth bells", "arpeggiated modular synth", "sub bass"],
            "playing": ["motorik pulse", "slow cinematic build", "staccato riffs"],
            "moods": ["cold neon atmosphere", "paranoid urban tension", "lonely midnight drive"],
            "eras": ["80s drum machine texture", "modern cinematic production"],
            "vocals": ["low spoken-word verses", "clean female lead vocal"],
            "production": ["big reverb tails", "bass-forward mix", "dark ambient intro"],
            "avoid": ["avoid cheesy novelty sound"]
        },
        "Desert Ritual Rock": {
            "genres": ["desert blues", "stoner rock", "psychedelic funk", "doom metal"],
            "instruments": ["fuzz bass", "tribal toms", "oud", "sitar", "distorted organ"],
            "playing": ["slow cinematic build", "wide vibrato", "dissonant chord voicings"],
            "moods": ["sun-baked desert mood", "mysterious and ritualistic", "brooding and elegant"],
            "eras": ["70s analogue warmth", "lo-fi cassette texture"],
            "vocals": ["gritty male lead vocal", "chanting crowd vocals"],
            "production": ["distorted tape saturation", "gritty analogue texture", "tight low end"],
            "avoid": ["avoid generic pop chorus"]
        }
    }
}


ASSOCIATION_PRESETS = {
    "Grunge Rock Expansion": {
        "genres": [
            "90s alternative rock",
            "post-grunge",
            "shoegaze",
            "sludge blues",
            "stoner rock"
        ],
        "instruments": [
            "twin distorted guitars",
            "fuzz bass",
            "tight snare",
            "distorted organ",
            "vinyl crackle"
        ],
        "playing": [
            "quiet-loud dynamics",
            "Loose live drumming",
            "Behind-the-beat groove",
            "wide vibrato",
            "big singalong chorus"
        ],
        "moods": [
            "brooding and elegant",
            "bittersweet nostalgia",
            "dreamy but unsettling",
            "lonely midnight drive"
        ],
        "eras": [
            "mid-90s alternative rock polish",
            "early 90s metal mix",
            "lo-fi cassette texture"
        ],
        "vocals": [
            "gritty male lead vocal",
            "raw punk vocal delivery",
            "raspy gang vocals"
        ],
        "production": [
            "wide stereo guitars",
            "gritty analogue texture",
            "punchy drums",
            "dry upfront vocals",
            "dynamic arrangement with strong contrast"
        ],
        "exclude": {
            "instruments": [
                "accordion",
                "theremin",
                "balalaika",
                "tin whistle",
                "bagpipes",
                "erhu",
                "shakuhachi",
                "kora",
                "sitar",
                "oud",
                "taiko drums",
                "marimba"
            ],
            "genres": [
                "sea shanty",
                "Russian folk",
                "Balkan brass",
                "amapiano",
                "chiptune",
                "Extratone",
                "Harsh Noise Wall"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "trip-hop",
                "industrial metal",
                "darkwave",
                "Blackgaze"
            ],
            "instruments": [
                "analog synth pads",
                "field recordings",
                "Mellotron choir"
            ],
            "playing": [
                "Industrial stomp",
                "motorik pulse"
            ],
            "moods": [
                "paranoid urban tension",
                "haunted and cinematic"
            ]
        }
    },
    "Thrash / Groove Metal Core": {
        "genres": [
            "thrash metal",
            "groove metal",
            "industrial metal",
            "blackened folk metal",
            "Cybergrind"
        ],
        "instruments": [
            "twin distorted guitars",
            "palm-muted rhythm guitars",
            "wah guitar solo",
            "tight snare",
            "blast-beat drums",
            "fuzz bass"
        ],
        "playing": [
            "aggressive downpicking",
            "Chugging palm-muted rhythm",
            "Double-kick drive",
            "galloping rhythm",
            "stop-start riffing",
            "Tremolo-picked momentum"
        ],
        "moods": [
            "darkly triumphant",
            "reckless tavern energy",
            "paranoid urban tension"
        ],
        "eras": [
            "early 90s metal mix",
            "arena-sized mix",
            "modern cinematic production"
        ],
        "vocals": [
            "gritty male lead vocal",
            "raspy gang vocals",
            "raw punk vocal delivery"
        ],
        "production": [
            "punchy drums",
            "wide stereo guitars",
            "tight low end",
            "crisp transient attack",
            "high-energy chorus lift"
        ],
        "exclude": {
            "instruments": [
                "accordion",
                "theremin",
                "Glass Armonica",
                "Hydraulophone",
                "tin whistle",
                "marimba"
            ],
            "genres": [
                "dream pop",
                "neo-soul",
                "amapiano",
                "highlife",
                "baroque pop"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "Dungeon synth",
                "darkwave",
                "Balkan brass"
            ],
            "instruments": [
                "choir swells",
                "taiko drums",
                "orchestral strings"
            ],
            "moods": [
                "haunted and cinematic"
            ]
        }
    },
    "Sea Shanty Tavern Folk": {
        "genres": [
            "sea shanty",
            "Russian folk",
            "Balkan brass",
            "Celtic punk",
            "gothic country"
        ],
        "instruments": [
            "accordion",
            "balalaika",
            "fiddle",
            "nylon guitar",
            "tin whistle",
            "banjo",
            "live hand percussion",
            "mandolin"
        ],
        "playing": [
            "swing feel",
            "Swing shuffle",
            "call-and-response vocals",
            "chant-like backing vocals",
            "Offbeat skank"
        ],
        "moods": [
            "playful but melancholic",
            "reckless tavern energy",
            "sarcastic and rowdy",
            "chaotic festival atmosphere"
        ],
        "eras": [
            "live tavern recording feel",
            "70s analogue warmth"
        ],
        "vocals": [
            "gritty male lead vocal",
            "chanting crowd vocals",
            "layered call-and-response choir"
        ],
        "production": [
            "clear melodic hook",
            "dynamic arrangement with strong contrast",
            "punchy drums"
        ],
        "exclude": {
            "instruments": [
                "808 kick",
                "arpeggiated modular synth",
                "FM synth bells",
                "sub bass",
                "theremin"
            ],
            "genres": [
                "Extratone",
                "Harsh Noise Wall",
                "Vaportrap",
                "minimal techno"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "thrash metal",
                "surf rock",
                "dark cabaret"
            ],
            "instruments": [
                "twin distorted guitars",
                "brass stabs",
                "distorted organ"
            ]
        }
    },
    "Neon Noir Synthwave": {
        "genres": [
            "synthwave",
            "retrowave",
            "darkwave",
            "cyberpunk electro",
            "EBM",
            "Vaportrap",
            "witch house"
        ],
        "instruments": [
            "analog synth pads",
            "FM synth bells",
            "arpeggiated modular synth",
            "sub bass",
            "808 kick",
            "vinyl crackle"
        ],
        "playing": [
            "motorik pulse",
            "Mechanical quantization",
            "Four-on-the-floor",
            "Stuttering percussion",
            "slow cinematic build"
        ],
        "moods": [
            "cold neon atmosphere",
            "paranoid urban tension",
            "lonely midnight drive",
            "dreamy but unsettling"
        ],
        "eras": [
            "80s drum machine texture",
            "late 80s production",
            "modern cinematic production"
        ],
        "vocals": [
            "low spoken-word verses",
            "clean female lead vocal",
            "whispered intro"
        ],
        "production": [
            "big reverb tails",
            "bass-forward mix",
            "dark ambient intro",
            "cinematic transitions"
        ],
        "exclude": {
            "instruments": [
                "accordion",
                "banjo",
                "balalaika",
                "fiddle",
                "tin whistle",
                "bagpipes"
            ],
            "genres": [
                "sea shanty",
                "Celtic punk",
                "Russian folk",
                "maskandi"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "industrial metal",
                "trip-hop",
                "shoegaze"
            ],
            "instruments": [
                "twin distorted guitars",
                "Mellotron choir",
                "field recordings"
            ]
        }
    },
    "Desert Ritual Rock": {
        "genres": [
            "desert blues",
            "stoner rock",
            "psychedelic funk",
            "doom metal",
            "sludge blues"
        ],
        "instruments": [
            "fuzz bass",
            "tribal toms",
            "oud",
            "sitar",
            "distorted organ",
            "live hand percussion",
            "nylon guitar"
        ],
        "playing": [
            "slow cinematic build",
            "wide vibrato",
            "dissonant chord voicings",
            "Tribal hand percussion",
            "syncopated groove"
        ],
        "moods": [
            "sun-baked desert mood",
            "mysterious and ritualistic",
            "brooding and elegant",
            "haunted and cinematic"
        ],
        "eras": [
            "70s analogue warmth",
            "lo-fi cassette texture",
            "modern cinematic production"
        ],
        "vocals": [
            "gritty male lead vocal",
            "chanting crowd vocals",
            "low spoken-word verses"
        ],
        "production": [
            "distorted tape saturation",
            "gritty analogue texture",
            "tight low end",
            "dynamic arrangement with strong contrast"
        ],
        "exclude": {
            "instruments": [
                "accordion",
                "FM synth bells",
                "808 kick",
                "tin whistle"
            ],
            "genres": [
                "chiptune",
                "Seapunk",
                "amapiano",
                "Extratone"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "Dungeon synth",
                "dark cabaret",
                "spaghetti western"
            ],
            "instruments": [
                "choir swells",
                "orchestral strings",
                "Waterphone"
            ]
        }
    },
    "Dark Ambient / Dungeon Synth": {
        "genres": [
            "Dark Ambient",
            "Dungeon synth",
            "Keller synth",
            "hauntology",
            "Illbient",
            "Lowercase"
        ],
        "instruments": [
            "field recordings",
            "Mellotron choir",
            "analog synth pads",
            "choir swells",
            "Waterphone",
            "Glass Armonica",
            "Ondes Martenot"
        ],
        "playing": [
            "slow cinematic build",
            "tension-and-release arrangement",
            "Mechanical quantization",
            "Cinematic tom patterns"
        ],
        "moods": [
            "haunted and cinematic",
            "mysterious and ritualistic",
            "dreamy but unsettling",
            "cold neon atmosphere"
        ],
        "eras": [
            "lo-fi cassette texture",
            "retro video game soundtrack energy",
            "modern cinematic production"
        ],
        "vocals": [
            "whispered intro",
            "no vocals, instrumental",
            "operatic backing vocals"
        ],
        "production": [
            "dark ambient intro",
            "big reverb tails",
            "cinematic transitions",
            "gritty analogue texture"
        ],
        "exclude": {
            "instruments": [
                "wah guitar solo",
                "blast-beat drums",
                "tight snare",
                "accordion"
            ],
            "genres": [
                "Celtic punk",
                "thrash metal",
                "sea shanty",
                "samba rock"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "blackened folk metal",
                "witch house",
                "Blackgaze"
            ],
            "instruments": [
                "twin distorted guitars",
                "taiko drums"
            ]
        }
    },
    "Jazz / Neo-Soul / Acid Groove": {
        "genres": [
            "acid jazz",
            "neo-soul",
            "psychedelic funk",
            "highlife",
            "Afrobeat"
        ],
        "instruments": [
            "fretless bass",
            "upright bass",
            "brass stabs",
            "vibraphone",
            "marimba",
            "live hand percussion"
        ],
        "playing": [
            "walking bassline",
            "funky ghost notes",
            "Ghost note funk",
            "Broken beat",
            "syncopated groove",
            "Jazz brushwork"
        ],
        "moods": [
            "brooding and elegant",
            "playful but melancholic",
            "bittersweet nostalgia"
        ],
        "eras": [
            "70s analogue warmth",
            "underground club mix",
            "modern cinematic production"
        ],
        "vocals": [
            "clean female lead vocal",
            "layered harmonies",
            "low spoken-word verses"
        ],
        "production": [
            "bass-forward mix",
            "clear melodic hook",
            "dry upfront vocals",
            "tight low end"
        ],
        "exclude": {
            "instruments": [
                "blast-beat drums",
                "palm-muted rhythm guitars",
                "bagpipes",
                "hurdy-gurdy"
            ],
            "genres": [
                "Gorenoise",
                "Harsh Noise Wall",
                "Extratone",
                "thrash metal"
            ]
        },
        "mutation_candidates": {
            "genres": [
                "trip-hop",
                "darkwave",
                "spaghetti western"
            ],
            "instruments": [
                "analog synth pads",
                "vinyl crackle"
            ]
        }
    },
    "Noise / Extreme Weirdness": {
        "genres": [
            "Harsh Noise Wall",
            "Japanoise",
            "Vapornoise",
            "Gorenoise",
            "Danger music",
            "Extratone",
            "Breakcore",
            "Mathgrind"
        ],
        "instruments": [
            "field recordings",
            "Prepared piano",
            "Daxophone",
            "Waterphone",
            "Apprehension Engine",
            "theremin",
            "Hydraulophone"
        ],
        "playing": [
            "Blast beat",
            "Stuttering percussion",
            "Footwork tempo",
            "Mechanical quantization",
            "Polyrhythmic drumming"
        ],
        "moods": [
            "chaotic festival atmosphere",
            "dreamy but unsettling",
            "paranoid urban tension",
            "mysterious and ritualistic"
        ],
        "eras": [
            "underground club mix",
            "lo-fi cassette texture",
            "modern cinematic production"
        ],
        "vocals": [
            "raw punk vocal delivery",
            "whispered intro",
            "no vocals, instrumental"
        ],
        "production": [
            "distorted tape saturation",
            "gritty analogue texture",
            "crisp transient attack",
            "dynamic arrangement with strong contrast"
        ],
        "exclude": {
            "genres": [],
            "instruments": []
        },
        "mutation_candidates": {
            "genres": [
                "Clowncore",
                "Black MIDI",
                "Nintendocore",
                "Dungeon synth"
            ],
            "instruments": [
                "accordion",
                "FM synth bells",
                "twin distorted guitars"
            ]
        }
    }
}


@dataclass
class GeneratorSettings:
    mode: str = "Coherent"
    bundle: str = "None"  # Deprecated: kept for older database compatibility
    max_chars: int = MAX_PROMPT_CHARS
    genre_count: int = 3
    instrument_count: int = 5
    playing_count: int = 3
    mood_count: int = 2
    era_count: int = 1
    vocal_count: int = 1
    production_count: int = 4
    avoid_count: int = 1
    seed: str = ""
    base_prompt: str = ""
    auto_match_base_style: bool = True
    simple_append_only: bool = True
    use_associations: bool = True
    base_style: str = "None"
    cohesion: int = 80
    weirdness: int = 15
    allow_excluded: bool = False
    lock_base_genre: bool = True
    blend_enabled: bool = False
    blend_styles: List[str] = field(default_factory=list)


class Mishmasher(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Suno Style Mishmasher")
        self.resize(1120, 760)

        self.db = self.load_db()
        self.settings = GeneratorSettings()

        tabs = QTabWidget()
        tabs.addTab(self.build_generator_tab(), "Generator")
        tabs.addTab(self.build_database_tab(), "Database")
        tabs.addTab(self.build_bulk_import_tab(), "Bulk Import")
        tabs.addTab(self.build_import_packs_tab(), "Import Packs")
        tabs.addTab(self.build_associations_tab(), "Associations")
        tabs.addTab(self.build_help_tab(), "Help")
        self.setCentralWidget(tabs)

        self.refresh_bundle_combo()
        self.refresh_style_combo()
        self.generate_prompt()

    def load_db(self) -> dict:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists():
            default_db = json.loads(json.dumps(DEFAULT_DB))
            default_db["associations"] = json.loads(json.dumps(ASSOCIATION_PRESETS))
            DB_PATH.write_text(json.dumps(default_db, indent=2, ensure_ascii=False), encoding="utf-8")
            return default_db
        try:
            data = json.loads(DB_PATH.read_text(encoding="utf-8"))
            changed = self.ensure_database_shape(data)
            if changed:
                DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return data
        except Exception:
            QMessageBox.warning(self, "Database error", "Could not read the database. Loading defaults instead.")
            default_db = json.loads(json.dumps(DEFAULT_DB))
            default_db["associations"] = json.loads(json.dumps(ASSOCIATION_PRESETS))
            return default_db

    def ensure_database_shape(self, data: dict) -> bool:
        changed = False
        for key in ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"]:
            if key not in data or not isinstance(data.get(key), list):
                data[key] = []
                changed = True
        if "bundles" not in data or not isinstance(data.get("bundles"), dict):
            data["bundles"] = {}
            changed = True
        if "associations" not in data or not isinstance(data.get("associations"), dict):
            data["associations"] = json.loads(json.dumps(ASSOCIATION_PRESETS))
            changed = True
        else:
            # Add new starter associations without overwriting the user's own edits.
            for name, entry in ASSOCIATION_PRESETS.items():
                if name not in data["associations"]:
                    data["associations"][name] = entry
                    changed = True

        # Convert legacy bundles into associations so the user has one mental model:
        # "Base styles" are the main presets. Bundles remain stored, but do not need
        # to be used from the Generator tab.
        bundles = data.get("bundles", {})
        associations = data.get("associations", {})
        if isinstance(bundles, dict) and isinstance(associations, dict):
            for bundle_name, bundle_entry in bundles.items():
                if not isinstance(bundle_entry, dict):
                    continue
                assoc_name = str(bundle_name)
                if assoc_name not in associations:
                    converted = {k: list(bundle_entry.get(k, [])) for k in ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"]}
                    converted.setdefault("exclude", {"genres": [], "instruments": []})
                    converted.setdefault("mutation_candidates", {"genres": [], "instruments": [], "moods": []})
                    associations[assoc_name] = converted
                    changed = True
        return changed

    def save_db(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        DB_PATH.write_text(json.dumps(self.db, indent=2, ensure_ascii=False), encoding="utf-8")

    def build_generator_tab(self) -> QWidget:
        page = QWidget()
        root = QHBoxLayout(page)

        left = QVBoxLayout()
        root.addLayout(left, 1)

        start_group = QGroupBox("Start here")
        start_layout = QVBoxLayout(start_group)

        start_layout.addWidget(QLabel("Base prompt or starting style"))
        self.base_prompt_edit = QPlainTextEdit()
        self.base_prompt_edit.setPlaceholderText(
            "Examples:\n"
            "grunge rock, raw male vocal\n"
            "industrial metal with cinematic tension\n"
            "dark fantasy orchestral horror cue"
        )
        self.base_prompt_edit.setMaximumHeight(110)
        self.base_prompt_edit.textChanged.connect(self.generate_prompt)
        start_layout.addWidget(self.base_prompt_edit)

        style_row = QFormLayout()
        self.base_style_combo = QComboBox()
        self.base_style_combo.currentTextChanged.connect(self.generate_prompt)
        style_row.addRow("Base style", self.base_style_combo)
        start_layout.addLayout(style_row)

        blend_group = QGroupBox("Blend base styles")
        blend_layout = QVBoxLayout(blend_group)
        self.blend_check = QCheckBox("Blend multiple base styles")
        self.blend_check.setChecked(False)
        self.blend_check.stateChanged.connect(self.generate_prompt)
        blend_layout.addWidget(self.blend_check)
        blend_hint = QLabel("Select two or more association styles to merge their genres, instruments, moods, production notes, exclusions, and mutation pools.")
        blend_hint.setWordWrap(True)
        blend_layout.addWidget(blend_hint)
        self.blend_styles_list = QListWidget()
        self.blend_styles_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.blend_styles_list.setMaximumHeight(125)
        self.blend_styles_list.itemSelectionChanged.connect(self.generate_prompt)
        blend_layout.addWidget(self.blend_styles_list)
        blend_buttons = QHBoxLayout()
        add_current_blend_btn = QPushButton("Add current base style")
        add_current_blend_btn.clicked.connect(self.add_current_base_style_to_blend)
        clear_blend_btn = QPushButton("Clear blend")
        clear_blend_btn.clicked.connect(self.clear_blend_selection)
        blend_buttons.addWidget(add_current_blend_btn)
        blend_buttons.addWidget(clear_blend_btn)
        blend_layout.addLayout(blend_buttons)
        start_layout.addWidget(blend_group)

        quick_row = QHBoxLayout()
        self.auto_match_check = QCheckBox("Auto-match from base prompt")
        self.auto_match_check.setChecked(True)
        self.auto_match_check.stateChanged.connect(self.generate_prompt)
        self.append_only_check = QCheckBox("Append extras to my base prompt")
        self.append_only_check.setChecked(True)
        self.append_only_check.stateChanged.connect(self.generate_prompt)
        quick_row.addWidget(self.auto_match_check)
        quick_row.addWidget(self.append_only_check)
        start_layout.addLayout(quick_row)

        add_row = QHBoxLayout()
        add_genre_btn = QPushButton("Add base as genre")
        add_genre_btn.clicked.connect(self.add_base_prompt_as_genre)
        add_style_btn = QPushButton("Create base style")
        add_style_btn.clicked.connect(self.create_base_style_from_prompt)
        add_row.addWidget(add_genre_btn)
        add_row.addWidget(add_style_btn)
        start_layout.addLayout(add_row)

        left.addWidget(start_group)

        control_group = QGroupBox("Style control")
        form = QFormLayout(control_group)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Coherent", "Experimental", "Chaos", "Focused", "Dense"])
        self.mode_combo.currentTextChanged.connect(self.generate_prompt)
        form.addRow("Mode", self.mode_combo)

        self.cohesion_spin = QSpinBox()
        self.cohesion_spin.setRange(0, 100)
        self.cohesion_spin.setValue(80)
        self.cohesion_spin.setSuffix("%")
        self.cohesion_spin.valueChanged.connect(self.generate_prompt)
        form.addRow("Cohesion", self.cohesion_spin)

        self.weirdness_spin = QSpinBox()
        self.weirdness_spin.setRange(0, 100)
        self.weirdness_spin.setValue(15)
        self.weirdness_spin.setSuffix("%")
        self.weirdness_spin.valueChanged.connect(self.generate_prompt)
        form.addRow("Weirdness", self.weirdness_spin)

        self.max_chars_spin = QSpinBox()
        self.max_chars_spin.setRange(200, 1000)
        self.max_chars_spin.setValue(1000)
        self.max_chars_spin.valueChanged.connect(self.generate_prompt)
        form.addRow("Max chars", self.max_chars_spin)

        left.addWidget(control_group)

        actions = QHBoxLayout()
        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self.generate_prompt)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.copy_prompt)
        save_btn = QPushButton("Save prompt")
        save_btn.clicked.connect(self.save_prompt_to_file)
        actions.addWidget(gen_btn)
        actions.addWidget(copy_btn)
        actions.addWidget(save_btn)
        left.addLayout(actions)

        advanced = QGroupBox("Advanced options")
        advanced_form = QFormLayout(advanced)

        self.use_assoc_check = QCheckBox("Use association engine")
        self.use_assoc_check.setChecked(True)
        self.use_assoc_check.stateChanged.connect(self.generate_prompt)
        advanced_form.addRow("Associations", self.use_assoc_check)

        self.allow_excluded_check = QCheckBox("Allow unlikely/excluded pairings")
        self.allow_excluded_check.setChecked(False)
        self.allow_excluded_check.stateChanged.connect(self.generate_prompt)
        advanced_form.addRow("Exclusions", self.allow_excluded_check)

        self.lock_base_genre_check = QCheckBox("Keep base style represented")
        self.lock_base_genre_check.setChecked(True)
        self.lock_base_genre_check.stateChanged.connect(self.generate_prompt)
        advanced_form.addRow("Base lock", self.lock_base_genre_check)

        self.seed_box = QLineEdit()
        self.seed_box.setPlaceholderText("Optional seed for repeatable results")
        self.seed_box.textChanged.connect(self.generate_prompt)
        advanced_form.addRow("Seed", self.seed_box)

        left.addWidget(advanced)

        counts = QGroupBox("Advanced ingredient counts")
        count_form = QFormLayout(counts)
        self.count_spins: Dict[str, QSpinBox] = {}
        for label, key, value in [
            ("Extra genres", "genre_count", 1),
            ("Instruments", "instrument_count", 4),
            ("Playing directions", "playing_count", 3),
            ("Moods", "mood_count", 2),
            ("Era/texture", "era_count", 1),
            ("Vocals", "vocal_count", 1),
            ("Production notes", "production_count", 3),
            ("Avoid notes", "avoid_count", 1),
        ]:
            spin = QSpinBox()
            spin.setRange(0, 12)
            spin.setValue(value)
            spin.valueChanged.connect(self.generate_prompt)
            self.count_spins[key] = spin
            count_form.addRow(label, spin)
        left.addWidget(counts)

        explanation = QLabel(
            "Tip: for normal use, type a base prompt, choose a base style, then use Coherent or Experimental. "
            "Chaos ignores associations and uses the full database."
        )
        explanation.setWordWrap(True)
        left.addWidget(explanation)
        left.addStretch(1)

        right = QVBoxLayout()
        root.addLayout(right, 2)

        self.output = QPlainTextEdit()
        self.output.setPlaceholderText("Generated Suno style prompt appears here.")
        self.output.textChanged.connect(self.update_count)
        right.addWidget(self.output, 1)

        self.char_label = QLabel("0 / 1000")
        self.char_label.setAlignment(Qt.AlignRight)
        right.addWidget(self.char_label)

        self.breakdown = QTextEdit()
        self.breakdown.setReadOnly(True)
        self.breakdown.setMinimumHeight(180)
        right.addWidget(self.breakdown)

        return page


    def build_database_tab(self) -> QWidget:
        page = QWidget()
        root = QHBoxLayout(page)

        left = QVBoxLayout()
        root.addLayout(left, 1)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"])
        self.category_combo.currentTextChanged.connect(self.refresh_item_list)
        left.addWidget(QLabel("Category"))
        left.addWidget(self.category_combo)

        self.item_list = QListWidget()
        left.addWidget(self.item_list, 1)

        edit_row = QHBoxLayout()
        self.new_item = QLineEdit()
        self.new_item.setPlaceholderText("Add new entry")
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        remove_btn = QPushButton("Remove selected")
        remove_btn.clicked.connect(self.remove_selected_items)
        edit_row.addWidget(self.new_item)
        edit_row.addWidget(add_btn)
        edit_row.addWidget(remove_btn)
        left.addLayout(edit_row)

        bulk_group = QGroupBox("Bulk import")
        bulk_layout = QVBoxLayout(bulk_group)

        self.bulk_text = QPlainTextEdit()
        self.bulk_text.setPlaceholderText(
            "Paste one item per line, or comma/semicolon-separated values.\n"
            "Examples:\n"
            "pirate metal\n"
            "goblin folk punk, doom jazz, dungeon synth\n"
            "accordion; hurdy-gurdy; taiko drums"
        )
        self.bulk_text.setMinimumHeight(120)
        bulk_layout.addWidget(self.bulk_text)

        bulk_buttons = QHBoxLayout()
        import_paste_btn = QPushButton("Import pasted")
        import_paste_btn.clicked.connect(self.import_bulk_text)
        import_file_btn = QPushButton("Import file")
        import_file_btn.clicked.connect(self.import_bulk_file)
        clear_bulk_btn = QPushButton("Clear")
        clear_bulk_btn.clicked.connect(self.bulk_text.clear)
        bulk_buttons.addWidget(import_paste_btn)
        bulk_buttons.addWidget(import_file_btn)
        bulk_buttons.addWidget(clear_bulk_btn)
        bulk_layout.addLayout(bulk_buttons)

        self.bulk_status = QLabel("Bulk import supports .txt, .csv, and .json list files.")
        self.bulk_status.setWordWrap(True)
        bulk_layout.addWidget(self.bulk_status)

        left.addWidget(bulk_group)

        right = QVBoxLayout()
        root.addLayout(right, 1)

        right.addWidget(QLabel("Full JSON database"))
        self.db_editor = QPlainTextEdit()
        self.db_editor.setPlainText(json.dumps(self.db, indent=2, ensure_ascii=False))
        right.addWidget(self.db_editor, 1)

        db_buttons = QHBoxLayout()
        reload_btn = QPushButton("Reload from disk")
        reload_btn.clicked.connect(self.reload_database)
        apply_btn = QPushButton("Apply JSON")
        apply_btn.clicked.connect(self.apply_json_database)
        import_db_btn = QPushButton("Import full JSON")
        import_db_btn.clicked.connect(self.import_full_database)
        export_btn = QPushButton("Export JSON")
        export_btn.clicked.connect(self.export_database)
        db_buttons.addWidget(reload_btn)
        db_buttons.addWidget(apply_btn)
        db_buttons.addWidget(import_db_btn)
        db_buttons.addWidget(export_btn)
        right.addLayout(db_buttons)

        self.refresh_item_list()
        return page


    def build_bulk_import_tab(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)

        intro = QLabel(
            "Pick the target list, paste entries, then import. Supports one item per line, comma-separated, semicolon-separated, .txt, .csv, and .json files."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        row = QHBoxLayout()
        row.addWidget(QLabel("Target category"))
        self.bulk_category_combo = QComboBox()
        self.bulk_category_combo.addItems(["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"])
        self.bulk_category_combo.currentTextChanged.connect(self.sync_bulk_category_to_database_tab)
        row.addWidget(self.bulk_category_combo)
        row.addStretch(1)
        root.addLayout(row)

        self.bulk_text_alt = QPlainTextEdit()
        self.bulk_text_alt.setPlaceholderText(
            "Paste items here, for example:\n"
            "pirate metal\n"
            "goblin folk punk\n"
            "doom jazz, dungeon synth, medieval trap\n"
            "accordion; hurdy-gurdy; taiko drums"
        )
        root.addWidget(self.bulk_text_alt, 1)

        button_row = QHBoxLayout()
        import_pasted = QPushButton("Import pasted text")
        import_pasted.clicked.connect(self.import_bulk_text_alt)
        import_file = QPushButton("Import from file")
        import_file.clicked.connect(self.import_bulk_file_alt)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.bulk_text_alt.clear)
        button_row.addWidget(import_pasted)
        button_row.addWidget(import_file)
        button_row.addWidget(clear_btn)
        button_row.addStretch(1)
        root.addLayout(button_row)

        self.bulk_status_alt = QLabel("No import run yet.")
        self.bulk_status_alt.setWordWrap(True)
        root.addWidget(self.bulk_status_alt)
        return page

    def sync_bulk_category_to_database_tab(self, category: str) -> None:
        if hasattr(self, "category_combo"):
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def current_bulk_category(self) -> str:
        if hasattr(self, "bulk_category_combo"):
            return self.bulk_category_combo.currentText()
        return self.category_combo.currentText()

    def import_bulk_text_alt(self) -> None:
        category = self.current_bulk_category()
        items = self.normalise_import_items(self.bulk_text_alt.toPlainText())
        if not items:
            QMessageBox.information(self, "Nothing to import", "Paste some items first, then try again.")
            return
        added, skipped = self.add_bulk_items(category, items)
        self.bulk_status_alt.setText(f"Imported into {category}: {added} added, {skipped} skipped as duplicates.")
        if hasattr(self, "bulk_status"):
            self.bulk_status.setText(self.bulk_status_alt.text())

    def import_bulk_file_alt(self) -> None:
        if hasattr(self, "category_combo") and hasattr(self, "bulk_category_combo"):
            index = self.category_combo.findText(self.bulk_category_combo.currentText())
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        self.import_bulk_file()
        if hasattr(self, "bulk_status_alt") and hasattr(self, "bulk_status"):
            self.bulk_status_alt.setText(self.bulk_status.text())

    def build_import_packs_tab(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)

        intro = QLabel(
            "Import one or many association packs at once. The importer creates/updates base styles, "
            "adds all missing genres, instruments, moods, playing styles, eras, vocals, production notes, "
            "avoid notes, exclusions, and mutation candidates into the main database, then refreshes the generator."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        example = {
            "packs": [
                {
                    "name": "Industrial Metal Core",
                    "genres": ["industrial metal", "groove metal", "EBM"],
                    "instruments": ["palm-muted rhythm guitars", "808 kick", "sub bass"],
                    "playing": ["industrial stomp", "mechanical quantization"],
                    "moods": ["paranoid urban tension", "cold neon atmosphere"],
                    "eras": ["90s industrial metal production", "modern cinematic hybrid mix"],
                    "vocals": ["gritty male lead vocal", "distorted vocal layers"],
                    "production": ["tight low end", "gritty analogue texture"],
                    "avoid": ["avoid generic pop chorus"],
                    "exclude": {
                        "genres": ["sea shanty", "neo-soul"],
                        "instruments": ["accordion", "tin whistle"]
                    },
                    "mutation_candidates": {
                        "genres": ["trip-hop", "witch house"],
                        "instruments": ["Mellotron choir"],
                        "moods": ["towering cinematic tension"]
                    }
                }
            ]
        }

        self.pack_text = QPlainTextEdit()
        self.pack_text.setPlaceholderText(
            "Paste JSON here. Supported shapes:\n"
            "1) {\"packs\": [ ... ]}\n"
            "2) [ {\"name\": \"Pack One\", ...}, {\"name\": \"Pack Two\", ...} ]\n"
            "3) {\"Industrial Metal Core\": { ... }, \"Dark Fantasy Score\": { ... }}\n"
            "4) A single pack object with a name field.\n\n"
            "Example:\n" + json.dumps(example, indent=2, ensure_ascii=False)
        )
        root.addWidget(self.pack_text, 1)

        button_row = QHBoxLayout()
        import_pasted = QPushButton("Import pasted pack(s)")
        import_pasted.clicked.connect(self.import_pack_text)
        import_file = QPushButton("Import pack file")
        import_file.clicked.connect(self.import_pack_file)
        load_example = QPushButton("Load example")
        load_example.clicked.connect(lambda: self.pack_text.setPlainText(json.dumps(example, indent=2, ensure_ascii=False)))
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.pack_text.clear)
        button_row.addWidget(import_pasted)
        button_row.addWidget(import_file)
        button_row.addWidget(load_example)
        button_row.addWidget(clear_btn)
        button_row.addStretch(1)
        root.addLayout(button_row)

        self.pack_status = QTextEdit()
        self.pack_status.setReadOnly(True)
        self.pack_status.setMaximumHeight(160)
        self.pack_status.setPlainText("No packs imported yet.")
        root.addWidget(self.pack_status)
        return page

    def import_pack_text(self) -> None:
        raw = self.pack_text.toPlainText().strip()
        if not raw:
            QMessageBox.information(self, "Nothing to import", "Paste one or more JSON packs first.")
            return
        try:
            payload = json.loads(raw)
            packs = self.parse_pack_payload(payload)
            self.apply_import_packs(packs)
        except Exception as exc:
            QMessageBox.warning(self, "Import failed", str(exc))

    def import_pack_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import association pack file",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
            packs = self.parse_pack_payload(payload)
            self.apply_import_packs(packs, source_name=Path(path).name)
        except Exception as exc:
            QMessageBox.warning(self, "Import failed", str(exc))

    def parse_pack_payload(self, payload) -> List[dict]:
        """Accept several JSON shapes and return normalized pack objects.

        Supported:
        - {"packs": [{"name": "..."}]}
        - [{"name": "..."}, {"name": "..."}]
        - {"Style Name": {association fields}, "Other Style": {...}}
        - {"name": "Single Pack", ...}
        - {"associations": {"Style Name": {...}}}
        """
        raw_packs = []

        if isinstance(payload, list):
            raw_packs = payload
        elif isinstance(payload, dict):
            if isinstance(payload.get("packs"), list):
                raw_packs = payload["packs"]
            elif isinstance(payload.get("associations"), dict):
                raw_packs = [dict(value, name=name) for name, value in payload["associations"].items() if isinstance(value, dict)]
            elif "name" in payload:
                raw_packs = [payload]
            else:
                # Treat a dictionary of named packs as {name: pack_body}.
                for name, value in payload.items():
                    if isinstance(value, dict):
                        item = dict(value)
                        item.setdefault("name", name)
                        raw_packs.append(item)
        else:
            raise ValueError("Pack JSON must be an object or a list.")

        packs = []
        for raw in raw_packs:
            if not isinstance(raw, dict):
                continue
            normalized = self.normalize_pack(raw)
            if normalized:
                packs.append(normalized)

        if not packs:
            raise ValueError("No valid packs found. Each pack needs at least a name and one populated category.")
        return packs

    def normalize_pack(self, raw: dict) -> dict | None:
        name = str(raw.get("name") or raw.get("title") or raw.get("style") or "").strip()
        if not name:
            return None

        category_keys = ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"]

        def to_list(value) -> List[str]:
            if value is None:
                return []
            if isinstance(value, list):
                candidates = value
            elif isinstance(value, str):
                candidates = self.normalise_import_items(value)
            else:
                candidates = [str(value)]
            result = []
            seen = set()
            for candidate in candidates:
                item = re.sub(r"\s+", " ", str(candidate).strip().strip("'\""))
                if not item:
                    continue
                key = item.casefold()
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        pack = {key: to_list(raw.get(key, [])) for key in category_keys}

        # Friendly aliases for pack files produced by GPTs or hand-written notes.
        alias_map = {
            "excluded_genres": ("exclude", "genres"),
            "excluded instruments": ("exclude", "instruments"),
            "excluded_instruments": ("exclude", "instruments"),
            "mutation_genres": ("mutation_candidates", "genres"),
            "mutation instruments": ("mutation_candidates", "instruments"),
            "mutation_instruments": ("mutation_candidates", "instruments"),
            "mutation_moods": ("mutation_candidates", "moods"),
        }

        exclude = raw.get("exclude", {}) if isinstance(raw.get("exclude", {}), dict) else {}
        mutation = raw.get("mutation_candidates", {}) if isinstance(raw.get("mutation_candidates", {}), dict) else {}

        pack["exclude"] = {
            "genres": to_list(exclude.get("genres", [])),
            "instruments": to_list(exclude.get("instruments", [])),
        }
        pack["mutation_candidates"] = {
            "genres": to_list(mutation.get("genres", [])),
            "instruments": to_list(mutation.get("instruments", [])),
            "moods": to_list(mutation.get("moods", [])),
        }

        for alias, target in alias_map.items():
            if alias in raw:
                section, category = target
                pack[section][category].extend(to_list(raw.get(alias)))
                # de-dupe alias merges
                pack[section][category] = to_list(pack[section][category])

        has_content = any(pack[key] for key in category_keys) or any(pack["exclude"].values()) or any(pack["mutation_candidates"].values())
        if not has_content:
            return None

        pack["name"] = name
        return pack

    def apply_import_packs(self, packs: List[dict], source_name: str = "pasted JSON") -> None:
        imported = 0
        overwritten = 0
        added_to_db = 0
        names = []

        self.db.setdefault("associations", {})
        for pack in packs:
            name = pack.pop("name")
            if name in self.db["associations"]:
                overwritten += 1
            self.db["associations"][name] = pack
            added_to_db += self.sync_association_entries_to_database(pack)
            imported += 1
            names.append(name)

        self.save_db()
        if hasattr(self, "db_editor"):
            self.sync_editor()
        self.refresh_style_combo()
        if hasattr(self, "assoc_combo"):
            self.refresh_association_combo()
        if hasattr(self, "category_combo"):
            self.refresh_item_list()
        self.generate_prompt()

        summary = (
            f"Imported {imported} pack(s) from {source_name}.\n"
            f"Updated existing packs: {overwritten}.\n"
            f"Added missing database item(s): {added_to_db}.\n\n"
            + "\n".join(f"• {name}" for name in names[:30])
        )
        if len(names) > 30:
            summary += f"\n...and {len(names) - 30} more."
        if hasattr(self, "pack_status"):
            self.pack_status.setPlainText(summary)
        QMessageBox.information(self, "Import complete", summary)

    def build_associations_tab(self) -> QWidget:
        page = QWidget()
        root = QHBoxLayout(page)

        left = QVBoxLayout()
        root.addLayout(left, 1)

        left.addWidget(QLabel("Association / base style"))
        self.assoc_combo = QComboBox()
        self.assoc_combo.currentTextChanged.connect(self.load_association_into_editor)
        left.addWidget(self.assoc_combo)

        name_row = QHBoxLayout()
        self.assoc_name_edit = QLineEdit()
        self.assoc_name_edit.setPlaceholderText("Association name, e.g. Grunge Rock Expansion")
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_association)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_association_from_editor)
        sync_all_btn = QPushButton("Sync all to DB")
        sync_all_btn.clicked.connect(self.sync_all_associations_button)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_association)
        name_row.addWidget(self.assoc_name_edit)
        name_row.addWidget(new_btn)
        name_row.addWidget(save_btn)
        name_row.addWidget(sync_all_btn)
        name_row.addWidget(delete_btn)
        left.addLayout(name_row)

        help_label = QLabel(
            "Each box is one item per line. These associations are what the generator uses when "
            "'Use style associations' is enabled. Exclusions keep odd pairings out unless you tick "
            "'Allow unlikely/excluded pairings'. Mutation candidates are the controlled weirdness pool."
        )
        help_label.setWordWrap(True)
        left.addWidget(help_label)

        right = QVBoxLayout()
        root.addLayout(right, 2)

        self.assoc_editors: Dict[str, QPlainTextEdit] = {}
        for label, key, placeholder in [
            ("Genres", "genres", "90s alternative rock\npost-grunge"),
            ("Instruments", "instruments", "fuzz bass\ntwin distorted guitars"),
            ("Playing", "playing", "quiet-loud dynamics\nloose live drumming"),
            ("Moods", "moods", "brooding and elegant\nbittersweet nostalgia"),
            ("Eras", "eras", "mid-90s alternative rock polish"),
            ("Vocals", "vocals", "gritty male lead vocal"),
            ("Production", "production", "wide stereo guitars\ngritty analogue texture"),
        ]:
            box = QGroupBox(label)
            layout = QVBoxLayout(box)
            editor = QPlainTextEdit()
            editor.setPlaceholderText(placeholder)
            editor.setMaximumHeight(90)
            layout.addWidget(editor)
            self.assoc_editors[key] = editor
            right.addWidget(box)

        exclusion_box = QGroupBox("Exclusions")
        exclusion_layout = QHBoxLayout(exclusion_box)
        self.exclude_genres_edit = QPlainTextEdit()
        self.exclude_genres_edit.setPlaceholderText("Excluded genres, one per line")
        self.exclude_instruments_edit = QPlainTextEdit()
        self.exclude_instruments_edit.setPlaceholderText("Excluded instruments, one per line")
        exclusion_layout.addWidget(self.exclude_genres_edit)
        exclusion_layout.addWidget(self.exclude_instruments_edit)
        right.addWidget(exclusion_box)

        mutation_box = QGroupBox("Mutation candidates")
        mutation_layout = QHBoxLayout(mutation_box)
        self.mutation_genres_edit = QPlainTextEdit()
        self.mutation_genres_edit.setPlaceholderText("Mutation genres, one per line")
        self.mutation_instruments_edit = QPlainTextEdit()
        self.mutation_instruments_edit.setPlaceholderText("Mutation instruments, one per line")
        self.mutation_moods_edit = QPlainTextEdit()
        self.mutation_moods_edit.setPlaceholderText("Mutation moods, one per line")
        mutation_layout.addWidget(self.mutation_genres_edit)
        mutation_layout.addWidget(self.mutation_instruments_edit)
        mutation_layout.addWidget(self.mutation_moods_edit)
        right.addWidget(mutation_box)

        self.refresh_association_combo()
        return page

    def refresh_association_combo(self) -> None:
        if not hasattr(self, "assoc_combo"):
            return
        current = self.assoc_combo.currentText()
        self.assoc_combo.blockSignals(True)
        self.assoc_combo.clear()
        for name in sorted(self.db.get("associations", {}).keys()):
            self.assoc_combo.addItem(name)
        if current:
            index = self.assoc_combo.findText(current)
            if index >= 0:
                self.assoc_combo.setCurrentIndex(index)
        self.assoc_combo.blockSignals(False)
        self.load_association_into_editor(self.assoc_combo.currentText())

    def list_to_text(self, values) -> str:
        if not isinstance(values, list):
            return ""
        return "\n".join(str(x) for x in values)

    def text_to_list(self, text: str) -> List[str]:
        items = []
        seen = set()
        for line in text.splitlines():
            item = re.sub(r"\s+", " ", line.strip().strip("'\""))
            if not item:
                continue
            key = item.casefold()
            if key not in seen:
                seen.add(key)
                items.append(item)
        return items

    def load_association_into_editor(self, name: str) -> None:
        if not hasattr(self, "assoc_name_edit"):
            return
        assoc = self.db.get("associations", {}).get(name, {}) if name else {}
        self.assoc_name_edit.setText(name or "")
        for key, editor in self.assoc_editors.items():
            editor.setPlainText(self.list_to_text(assoc.get(key, [])))
        exclude = assoc.get("exclude", {}) if isinstance(assoc, dict) else {}
        mutation = assoc.get("mutation_candidates", {}) if isinstance(assoc, dict) else {}
        self.exclude_genres_edit.setPlainText(self.list_to_text(exclude.get("genres", [])))
        self.exclude_instruments_edit.setPlainText(self.list_to_text(exclude.get("instruments", [])))
        self.mutation_genres_edit.setPlainText(self.list_to_text(mutation.get("genres", [])))
        self.mutation_instruments_edit.setPlainText(self.list_to_text(mutation.get("instruments", [])))
        self.mutation_moods_edit.setPlainText(self.list_to_text(mutation.get("moods", [])))

    def new_association(self) -> None:
        base = "New Association"
        name = base
        i = 2
        while name in self.db.get("associations", {}):
            name = f"{base} {i}"
            i += 1
        self.db.setdefault("associations", {})[name] = {
            "genres": [], "instruments": [], "playing": [], "moods": [], "eras": [], "vocals": [], "production": [],
            "exclude": {"genres": [], "instruments": []},
            "mutation_candidates": {"genres": [], "instruments": [], "moods": []},
        }
        self.save_db()
        self.sync_editor()
        self.refresh_style_combo()
        self.refresh_association_combo()
        index = self.assoc_combo.findText(name)
        if index >= 0:
            self.assoc_combo.setCurrentIndex(index)

    def sync_association_entries_to_database(self, entry: dict) -> int:
        """Add association values into the main database lists when missing.

        This keeps the association editor useful as the main data-entry point.
        The generator validates association terms against the main lists, so any
        new genres/instruments/etc. typed into an association must also exist
        in the matching top-level database category.
        """
        added = 0
        category_keys = ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"]

        def add_items(category: str, values) -> None:
            nonlocal added
            if category not in category_keys or not isinstance(values, list):
                return
            self.db.setdefault(category, [])
            existing = {str(x).casefold() for x in self.db.get(category, [])}
            for value in values:
                item = re.sub(r"\s+", " ", str(value).strip().strip("'\""))
                if not item:
                    continue
                key = item.casefold()
                if key not in existing:
                    self.db[category].append(item)
                    existing.add(key)
                    added += 1

        for category in category_keys:
            add_items(category, entry.get(category, []))

        exclude = entry.get("exclude", {})
        if isinstance(exclude, dict):
            add_items("genres", exclude.get("genres", []))
            add_items("instruments", exclude.get("instruments", []))

        mutation = entry.get("mutation_candidates", {})
        if isinstance(mutation, dict):
            for category in category_keys:
                add_items(category, mutation.get(category, []))

        for category in category_keys:
            if isinstance(self.db.get(category), list):
                self.db[category].sort(key=lambda x: str(x).casefold())
        return added

    def sync_all_associations_to_database(self, silent: bool = False) -> int:
        total_added = 0
        associations = self.db.get("associations", {})
        if isinstance(associations, dict):
            for entry in associations.values():
                if isinstance(entry, dict):
                    total_added += self.sync_association_entries_to_database(entry)
        self.save_db()
        if hasattr(self, "db_editor"):
            self.sync_editor()
        if hasattr(self, "category_combo"):
            self.refresh_item_list()
        self.generate_prompt()
        if not silent:
            QMessageBox.information(self, "Associations synced", f"Added {total_added} missing item(s) to the main database lists.")
        return total_added

    def sync_all_associations_button(self) -> None:
        # Save the currently open association first, then sync everything.
        if hasattr(self, "assoc_name_edit") and self.assoc_name_edit.text().strip():
            self.save_association_from_editor(show_message=False)
        added = self.sync_all_associations_to_database(silent=True)
        QMessageBox.information(self, "Associations synced", f"Added {added} missing item(s) to the main database lists.")

    def save_association_from_editor(self, show_message: bool = True) -> None:
        old_name = self.assoc_combo.currentText() if hasattr(self, "assoc_combo") else ""
        name = self.assoc_name_edit.text().strip()
        if not name:
            QMessageBox.information(self, "Missing name", "Give the association a name first.")
            return

        entry = {key: self.text_to_list(editor.toPlainText()) for key, editor in self.assoc_editors.items()}
        entry["exclude"] = {
            "genres": self.text_to_list(self.exclude_genres_edit.toPlainText()),
            "instruments": self.text_to_list(self.exclude_instruments_edit.toPlainText()),
        }
        entry["mutation_candidates"] = {
            "genres": self.text_to_list(self.mutation_genres_edit.toPlainText()),
            "instruments": self.text_to_list(self.mutation_instruments_edit.toPlainText()),
            "moods": self.text_to_list(self.mutation_moods_edit.toPlainText()),
        }

        self.db.setdefault("associations", {})
        if old_name and old_name != name and old_name in self.db["associations"]:
            del self.db["associations"][old_name]
        self.db["associations"][name] = entry

        added_to_db = self.sync_association_entries_to_database(entry)

        self.save_db()
        self.sync_editor()
        self.refresh_style_combo()
        self.refresh_association_combo()
        self.refresh_item_list()
        index = self.assoc_combo.findText(name)
        if index >= 0:
            self.assoc_combo.setCurrentIndex(index)
        self.generate_prompt()
        self.statusBar().showMessage(f"Association saved. Added {added_to_db} missing database item(s).", 3500)
        if show_message and added_to_db:
            QMessageBox.information(
                self,
                "Association saved",
                f"Saved '{name}' and added {added_to_db} missing item(s) to the main database lists."
            )

    def delete_association(self) -> None:
        name = self.assoc_combo.currentText() if hasattr(self, "assoc_combo") else ""
        if not name:
            return
        confirm = QMessageBox.question(self, "Delete association", f"Delete '{name}'?")
        if confirm != QMessageBox.Yes:
            return
        self.db.get("associations", {}).pop(name, None)
        self.save_db()
        self.sync_editor()
        self.refresh_style_combo()
        self.refresh_association_combo()
        self.generate_prompt()

    def build_help_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText(
            "Suno Style Mishmasher\n\n"
            "Simple use: type a base prompt or genre at the top of the Generator tab, then click Generate. The app will append instruments, direction, mood, era, vocals, and production notes while keeping the output under the character limit. Use Blend base styles when you want to merge two or more association profiles, for example Industrial Metal Core + Dark Ambient / Dungeon Synth. "
            "Use this to generate compact style prompts for Suno. The aim is not perfect genre accuracy, "
            "but creative discovery.\n\n"
            "Modes:\n"
            "Balanced: Mostly sensible combinations.\n"
            "Bundle-led: Starts from the selected bundle, then adds a few extra colours.\n"
            "Random: Mixes freely from the whole database.\n"
            "Chaos: Combines unrelated styles and instruments on purpose.\n"
            "Minimal: Short, focused prompt.\n"
            "Dense: More ingredients, still trimmed to the character limit.\n\n"
            "Base styles are the main style anchors. They connect compatible genres, instruments, moods, "
            "production notes, exclusions, and mutation candidates. Old style bundles are kept in the JSON for compatibility, "
            "but normal generation now uses base styles.\n\n"
            "Database file location:\n"
            f"{DB_PATH}\n\n"
            "Tip: Once Suno gives you something interesting, paste the best prompt back into your own notes "
            "and gradually build bundles from the styles that work.\n\n"
            "Bulk import: go to Database, pick a category, then paste one item per line or import a .txt, .csv, or .json file. Duplicate entries are skipped automatically.\n\nAssociations: use the Associations tab to link a base style to compatible genres, instruments, moods, production notes, exclusions, and mutation candidates. The Generator tab uses those links when Use style associations is enabled."
        )
        layout.addWidget(help_text)
        return page

    def refresh_bundle_combo(self) -> None:
        # Style bundles are now treated as legacy presets. They remain in the JSON database for
        # backwards compatibility, but the Generator tab no longer exposes them directly.
        if not hasattr(self, "bundle_combo"):
            return
        current = self.bundle_combo.currentText() if hasattr(self, "bundle_combo") else "None"
        self.bundle_combo.blockSignals(True)
        self.bundle_combo.clear()
        self.bundle_combo.addItem("None")
        for name in sorted(self.db.get("bundles", {}).keys()):
            self.bundle_combo.addItem(name)
        if current:
            index = self.bundle_combo.findText(current)
            if index >= 0:
                self.bundle_combo.setCurrentIndex(index)
        self.bundle_combo.blockSignals(False)

    def refresh_style_combo(self) -> None:
        if not hasattr(self, "base_style_combo"):
            return
        current = self.base_style_combo.currentText()
        self.base_style_combo.blockSignals(True)
        self.base_style_combo.clear()
        self.base_style_combo.addItem("None")
        for name in sorted(self.db.get("associations", {}).keys()):
            self.base_style_combo.addItem(name)
        if current:
            index = self.base_style_combo.findText(current)
            if index >= 0:
                self.base_style_combo.setCurrentIndex(index)
        self.base_style_combo.blockSignals(False)

        if hasattr(self, "blend_styles_list"):
            selected_before = set(self.selected_blend_styles())
            self.blend_styles_list.blockSignals(True)
            self.blend_styles_list.clear()
            for name in sorted(self.db.get("associations", {}).keys()):
                item = QListWidgetItem(name)
                self.blend_styles_list.addItem(item)
                if name in selected_before:
                    item.setSelected(True)
            self.blend_styles_list.blockSignals(False)

    def selected_blend_styles(self) -> List[str]:
        if not hasattr(self, "blend_styles_list"):
            return []
        return [item.text() for item in self.blend_styles_list.selectedItems()]

    def clear_blend_selection(self) -> None:
        if not hasattr(self, "blend_styles_list"):
            return
        self.blend_styles_list.clearSelection()
        self.generate_prompt()

    def add_current_base_style_to_blend(self) -> None:
        if not hasattr(self, "blend_styles_list") or not hasattr(self, "base_style_combo"):
            return
        name = self.base_style_combo.currentText()
        if not name or name == "None":
            return
        for i in range(self.blend_styles_list.count()):
            item = self.blend_styles_list.item(i)
            if item.text() == name:
                item.setSelected(True)
                break
        if hasattr(self, "blend_check"):
            self.blend_check.setChecked(True)
        self.generate_prompt()

    def refresh_item_list(self) -> None:
        category = self.category_combo.currentText()
        self.item_list.clear()
        for entry in self.db.get(category, []):
            item = QListWidgetItem(entry)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.item_list.addItem(item)

    def add_item(self) -> None:
        category = self.category_combo.currentText()
        text = self.new_item.text().strip()
        if not text:
            return
        self.db.setdefault(category, [])
        if text not in self.db[category]:
            self.db[category].append(text)
            self.db[category].sort()
        self.new_item.clear()
        self.save_db()
        self.refresh_item_list()
        self.sync_editor()
        self.generate_prompt()

    def remove_selected_items(self) -> None:
        category = self.category_combo.currentText()
        selected = [i.text() for i in self.item_list.selectedItems()]
        if not selected:
            return
        self.db[category] = [x for x in self.db.get(category, []) if x not in selected]
        self.save_db()
        self.refresh_item_list()
        self.sync_editor()
        self.generate_prompt()

    def normalise_import_items(self, raw_text: str) -> List[str]:
        """Parse pasted or file-loaded text into clean database entries.

        Supported formats:
        - One item per line
        - Comma or semicolon-separated text
        - Basic CSV rows
        - JSON list strings are handled by import_bulk_file() before this fallback
        """
        cleaned_lines: List[str] = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") or line.startswith("//"):
                continue
            cleaned_lines.append(line)

        items: List[str] = []
        for line in cleaned_lines:
            # Try CSV parsing first so quoted commas remain intact.
            try:
                row = next(csv.reader([line]))
            except Exception:
                row = [line]

            split_candidates: List[str] = []
            for cell in row:
                split_candidates.extend(re.split(r"[;\n]", cell))

            # If CSV produced one cell, also allow normal comma-separated paste.
            if len(row) == 1:
                split_candidates = re.split(r"[,;]", line)

            for candidate in split_candidates:
                item = candidate.strip().strip("'\"")
                item = re.sub(r"\s+", " ", item)
                if item:
                    items.append(item)

        # Case-insensitive de-dupe while keeping original wording.
        seen = set()
        unique: List[str] = []
        for item in items:
            key = item.casefold()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique

    def add_bulk_items(self, category: str, items: List[str]) -> tuple[int, int]:
        self.db.setdefault(category, [])
        existing_keys = {str(x).casefold() for x in self.db.get(category, [])}
        added = 0
        skipped = 0

        for item in items:
            key = item.casefold()
            if key in existing_keys:
                skipped += 1
                continue
            self.db[category].append(item)
            existing_keys.add(key)
            added += 1

        self.db[category].sort(key=lambda x: x.casefold())
        self.save_db()
        self.refresh_item_list()
        self.sync_editor()
        self.generate_prompt()
        return added, skipped

    def import_bulk_text(self) -> None:
        category = self.category_combo.currentText()
        items = self.normalise_import_items(self.bulk_text.toPlainText())
        if not items:
            QMessageBox.information(self, "Nothing to import", "Paste some items first, then try again.")
            return
        added, skipped = self.add_bulk_items(category, items)
        self.bulk_status.setText(f"Imported into {category}: {added} added, {skipped} skipped as duplicates.")

    def import_bulk_file(self) -> None:
        category = self.category_combo.currentText()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import list",
            "",
            "Supported Files (*.txt *.csv *.json);;Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        file_path = Path(path)
        try:
            raw = file_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            raw = file_path.read_text(encoding="latin-1")
        except Exception as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return

        items: List[str] = []
        if file_path.suffix.lower() == ".json":
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    items = [str(x).strip() for x in parsed if str(x).strip()]
                elif isinstance(parsed, dict):
                    value = parsed.get(category, [])
                    if isinstance(value, list):
                        items = [str(x).strip() for x in value if str(x).strip()]
                    else:
                        QMessageBox.warning(self, "JSON import", f"No list found for category '{category}'.")
                        return
                else:
                    QMessageBox.warning(self, "JSON import", "JSON must be either a list or a database-style object.")
                    return
            except Exception as exc:
                QMessageBox.warning(self, "Invalid JSON", str(exc))
                return
        else:
            items = self.normalise_import_items(raw)

        if not items:
            QMessageBox.information(self, "Nothing to import", "No usable items were found in that file.")
            return

        added, skipped = self.add_bulk_items(category, items)
        self.bulk_status.setText(f"Imported {file_path.name} into {category}: {added} added, {skipped} skipped as duplicates.")

    def sync_editor(self) -> None:
        self.db_editor.setPlainText(json.dumps(self.db, indent=2, ensure_ascii=False))

    def reload_database(self) -> None:
        self.db = self.load_db()
        self.sync_editor()
        self.refresh_bundle_combo()
        self.refresh_style_combo()
        if hasattr(self, "assoc_combo"):
            self.refresh_association_combo()
        self.refresh_item_list()
        self.generate_prompt()

    def apply_json_database(self) -> None:
        try:
            parsed = json.loads(self.db_editor.toPlainText())
            for key in ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid", "bundles", "associations"]:
                parsed.setdefault(key, {} if key in ["bundles", "associations"] else [])
            self.ensure_database_shape(parsed)
            self.db = parsed
            self.sync_all_associations_to_database(silent=True)
            self.save_db()
            self.refresh_bundle_combo()
            self.refresh_style_combo()
            self.refresh_item_list()
            if hasattr(self, "assoc_combo"):
                self.refresh_association_combo()
            self.generate_prompt()
            QMessageBox.information(self, "Database updated", "Database JSON applied and saved.")
        except Exception as exc:
            QMessageBox.warning(self, "Invalid JSON", str(exc))

    def import_full_database(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import full Suno style database",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            parsed = json.loads(Path(path).read_text(encoding="utf-8-sig"))
            if not isinstance(parsed, dict):
                raise ValueError("Database JSON must be an object with genres, instruments, moods, bundles, and associations.")
            self.ensure_database_shape(parsed)
            self.db = parsed
            self.sync_all_associations_to_database(silent=True)
            self.save_db()
            self.sync_editor()
            self.refresh_bundle_combo()
            self.refresh_style_combo()
            if hasattr(self, "assoc_combo"):
                self.refresh_association_combo()
            self.refresh_item_list()
            self.generate_prompt()
            QMessageBox.information(self, "Database imported", f"Imported and saved:\n{path}")
        except Exception as exc:
            QMessageBox.warning(self, "Import failed", str(exc))

    def export_database(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export database", "suno_style_database.json", "JSON Files (*.json)")
        if path:
            Path(path).write_text(json.dumps(self.db, indent=2, ensure_ascii=False), encoding="utf-8")

    def collect_settings(self) -> GeneratorSettings:
        return GeneratorSettings(
            mode=self.mode_combo.currentText(),
            bundle=self.bundle_combo.currentText() if hasattr(self, "bundle_combo") else "None",
            max_chars=self.max_chars_spin.value(),
            genre_count=self.count_spins["genre_count"].value(),
            instrument_count=self.count_spins["instrument_count"].value(),
            playing_count=self.count_spins["playing_count"].value(),
            mood_count=self.count_spins["mood_count"].value(),
            era_count=self.count_spins["era_count"].value(),
            vocal_count=self.count_spins["vocal_count"].value(),
            production_count=self.count_spins["production_count"].value(),
            avoid_count=self.count_spins["avoid_count"].value(),
            seed=self.seed_box.text().strip(),
            base_prompt=self.base_prompt_edit.toPlainText().strip() if hasattr(self, "base_prompt_edit") else "",
            auto_match_base_style=self.auto_match_check.isChecked() if hasattr(self, "auto_match_check") else True,
            simple_append_only=self.append_only_check.isChecked() if hasattr(self, "append_only_check") else True,
            use_associations=self.use_assoc_check.isChecked(),
            base_style=self.base_style_combo.currentText() if hasattr(self, "base_style_combo") else "None",
            cohesion=self.cohesion_spin.value() if hasattr(self, "cohesion_spin") else 80,
            weirdness=self.weirdness_spin.value() if hasattr(self, "weirdness_spin") else 15,
            allow_excluded=self.allow_excluded_check.isChecked() if hasattr(self, "allow_excluded_check") else False,
            lock_base_genre=self.lock_base_genre_check.isChecked() if hasattr(self, "lock_base_genre_check") else True,
            blend_enabled=self.blend_check.isChecked() if hasattr(self, "blend_check") else False,
            blend_styles=self.selected_blend_styles() if hasattr(self, "blend_styles_list") else [],
        )

    def clean_base_prompt(self) -> str:
        text = self.base_prompt_edit.toPlainText().strip() if hasattr(self, "base_prompt_edit") else ""
        text = re.sub(r"\s+", " ", text)
        return text.strip(" ;,")

    def add_base_prompt_as_genre(self) -> None:
        text = self.clean_base_prompt()
        if not text:
            QMessageBox.information(self, "No base prompt", "Type a genre or base prompt first.")
            return
        # If the base prompt is a longer prompt, use the first comma/semicolon segment as the genre candidate.
        genre = re.split(r"[,;]", text, maxsplit=1)[0].strip()
        if not genre:
            return
        added, skipped = self.add_bulk_items("genres", [genre])
        self.statusBar().showMessage(f"Genre saved: {added} added, {skipped} duplicate", 2500)

    def create_base_style_from_prompt(self) -> None:
        text = self.clean_base_prompt()
        if not text:
            QMessageBox.information(self, "No base prompt", "Type a genre or base prompt first.")
            return
        name = re.split(r"[,;]", text, maxsplit=1)[0].strip()
        name = name[:60].strip() or "New Base Style"
        style_name = name.title()
        genre = name

        self.db.setdefault("genres", [])
        if genre not in self.db["genres"]:
            self.db["genres"].append(genre)
            self.db["genres"].sort(key=lambda x: str(x).casefold())

        self.db.setdefault("associations", {})
        if style_name not in self.db["associations"]:
            self.db["associations"][style_name] = {
                "genres": [genre],
                "instruments": [],
                "playing": [],
                "moods": [],
                "eras": [],
                "vocals": [],
                "production": [],
                "exclude": {"genres": [], "instruments": []},
                "mutation_candidates": {"genres": [], "instruments": [], "moods": []},
            }
        self.save_db()
        self.sync_editor()
        self.refresh_style_combo()
        if hasattr(self, "assoc_combo"):
            self.refresh_association_combo()
        index = self.base_style_combo.findText(style_name)
        if index >= 0:
            self.base_style_combo.setCurrentIndex(index)
        self.generate_prompt()
        self.statusBar().showMessage(f"Base style saved: {style_name}", 2500)

    def auto_find_association_name(self, base_prompt: str) -> str:
        if not base_prompt:
            return "None"
        text = base_prompt.casefold()
        associations = self.db.get("associations", {})
        if not isinstance(associations, dict):
            return "None"

        # First, match association names directly.
        for name in associations.keys():
            if str(name).casefold() in text:
                return name

        # Then match any associated genres or style words contained in the prompt.
        best_name = "None"
        best_score = 0
        for name, assoc in associations.items():
            if not isinstance(assoc, dict):
                continue
            score = 0
            for category in ["genres", "moods", "eras", "production"]:
                for item in assoc.get(category, []):
                    item_text = str(item).casefold()
                    if item_text and item_text in text:
                        score += 3 if category == "genres" else 1
            if score > best_score:
                best_score = score
                best_name = name
        return best_name

    def rng(self, settings: GeneratorSettings) -> random.Random:
        if settings.seed:
            return random.Random(settings.seed)
        return random.Random()

    def get_association(self, style_name: str) -> dict | None:
        if not style_name or style_name == "None":
            return None
        assoc = self.db.get("associations", {}).get(style_name)
        return assoc if isinstance(assoc, dict) else None

    def unique_extend(self, target: List[str], values: List[str]) -> None:
        seen = {str(x).casefold() for x in target}
        for value in values:
            item = re.sub(r"\s+", " ", str(value).strip())
            if not item:
                continue
            key = item.casefold()
            if key not in seen:
                target.append(item)
                seen.add(key)

    def merge_associations(self, names: List[str]) -> dict | None:
        clean_names: List[str] = []
        seen_names = set()
        for name in names:
            if not name or name == "None":
                continue
            key = str(name).casefold()
            if key not in seen_names and self.get_association(name) is not None:
                clean_names.append(name)
                seen_names.add(key)

        if not clean_names:
            return None

        merged = {
            "genres": [],
            "instruments": [],
            "playing": [],
            "moods": [],
            "eras": [],
            "vocals": [],
            "production": [],
            "avoid": [],
            "exclude": {"genres": [], "instruments": []},
            "mutation_candidates": {"genres": [], "instruments": [], "moods": []},
        }

        for name in clean_names:
            assoc = self.get_association(name) or {}
            for category in ["genres", "instruments", "playing", "moods", "eras", "vocals", "production", "avoid"]:
                self.unique_extend(merged[category], list(assoc.get(category, [])))

            exclude = assoc.get("exclude", {}) if isinstance(assoc.get("exclude", {}), dict) else {}
            self.unique_extend(merged["exclude"]["genres"], list(exclude.get("genres", [])))
            self.unique_extend(merged["exclude"]["instruments"], list(exclude.get("instruments", [])))

            mutation = assoc.get("mutation_candidates", {}) if isinstance(assoc.get("mutation_candidates", {}), dict) else {}
            self.unique_extend(merged["mutation_candidates"]["genres"], list(mutation.get("genres", [])))
            self.unique_extend(merged["mutation_candidates"]["instruments"], list(mutation.get("instruments", [])))
            self.unique_extend(merged["mutation_candidates"]["moods"], list(mutation.get("moods", [])))

        return merged

    def valid_items(self, category: str, items: List[str]) -> List[str]:
        valid = set(self.db.get(category, []))
        return [x for x in items if x in valid]

    def exclusion_set(self, assoc: dict | None, category: str) -> Set[str]:
        if not assoc:
            return set()
        exclude = assoc.get("exclude", {})
        if not isinstance(exclude, dict):
            return set()
        return set(exclude.get(category, []))

    def pick_associated(
        self,
        rng: random.Random,
        category: str,
        count: int,
        assoc: dict | None,
        settings: GeneratorSettings,
        bundle_data: dict | None,
        bundle_weight: float,
    ) -> List[str]:
        if count <= 0:
            return []

        base = list(self.db.get(category, []))
        assoc_items = self.valid_items(category, list((assoc or {}).get(category, [])))
        mutation_block = (assoc or {}).get("mutation_candidates", {}) if assoc else {}
        mutation_items = []
        if isinstance(mutation_block, dict):
            mutation_items = self.valid_items(category, list(mutation_block.get(category, [])))
        bundle_items = self.valid_items(category, list((bundle_data or {}).get(category, [])))

        cohesion = max(0, min(100, settings.cohesion)) / 100.0
        weirdness = max(0, min(100, settings.weirdness)) / 100.0

        pool: List[str] = []
        if assoc_items:
            pool.extend(assoc_items * max(1, int(2 + cohesion * 12)))
        if bundle_items and bundle_weight > 0:
            pool.extend(bundle_items * max(1, int(bundle_weight * 3)))
        if mutation_items:
            pool.extend(mutation_items * max(1, int(weirdness * 8)))

        # This keeps the original broad database available, but heavily reduced when cohesion is high.
        broad_repeats = max(1, int((1.0 - cohesion) * 6 + weirdness * 4))
        pool.extend(base * broad_repeats)

        if not settings.allow_excluded:
            excluded = self.exclusion_set(assoc, category)
            if excluded:
                pool = [x for x in pool if x not in excluded]

        if not pool:
            pool = base

        chosen: List[str] = []
        if category == "genres" and settings.lock_base_genre and assoc_items:
            chosen.append(assoc_items[0])

        attempts = 0
        while len(chosen) < count and attempts < 300:
            attempts += 1
            candidate = rng.choice(pool)
            if candidate not in chosen:
                chosen.append(candidate)
        return chosen

    def pick(self, rng: random.Random, category: str, count: int, bundle_data: dict | None, bundle_weight: float) -> List[str]:
        if count <= 0:
            return []

        base = list(self.db.get(category, []))
        bundle_items = list((bundle_data or {}).get(category, []))
        pool: List[str] = []

        if bundle_items and bundle_weight > 0:
            repeats = max(1, int(bundle_weight * 4))
            pool.extend(bundle_items * repeats)

        pool.extend(base)

        if not pool:
            return []

        chosen: List[str] = []
        attempts = 0
        while len(chosen) < count and attempts < 200:
            attempts += 1
            candidate = rng.choice(pool)
            if candidate not in chosen:
                chosen.append(candidate)
        return chosen

    def generate_prompt(self) -> None:
        if not hasattr(self, "mode_combo"):
            return

        settings = self.collect_settings()
        rng = self.rng(settings)

        # Style bundles are legacy presets. The simplified generator uses associations/base styles
        # as the main control system, so bundles are only used if older code still exposes them.
        bundle_data = None
        if settings.bundle != "None":
            bundle_data = self.db.get("bundles", {}).get(settings.bundle, None)

        effective_base_style = settings.base_style
        if settings.auto_match_base_style and effective_base_style == "None" and settings.base_prompt:
            effective_base_style = self.auto_find_association_name(settings.base_prompt)

        blend_names: List[str] = []
        if settings.blend_enabled:
            blend_names.extend(settings.blend_styles)
            if effective_base_style != "None":
                blend_names.insert(0, effective_base_style)

        if settings.blend_enabled and blend_names:
            assoc_data = self.merge_associations(blend_names)
            active_style_label = " + ".join(dict.fromkeys([name for name in blend_names if name and name != "None"]))
        else:
            assoc_data = self.get_association(effective_base_style)
            active_style_label = effective_base_style

        associations_active = settings.use_associations and assoc_data is not None and settings.mode != "Chaos"

        mode = settings.mode
        bundle_weight = 0.0

        counts = {
            "genres": settings.genre_count,
            "instruments": settings.instrument_count,
            "playing": settings.playing_count,
            "moods": settings.mood_count,
            "eras": settings.era_count,
            "vocals": settings.vocal_count,
            "production": settings.production_count,
            "avoid": settings.avoid_count,
        }

        if mode == "Coherent":
            settings.cohesion = max(settings.cohesion, 75)
            settings.weirdness = min(settings.weirdness, 20)
            bundle_weight = 0.0
        elif mode == "Experimental":
            settings.cohesion = min(settings.cohesion, 65)
            settings.weirdness = max(settings.weirdness, 35)
            bundle_weight = 0.0
        elif mode == "Chaos":
            bundle_weight = 0.0
            settings.use_associations = False
            counts["genres"] = max(counts["genres"], 4)
            counts["instruments"] = max(counts["instruments"], 6)
            counts["playing"] = max(counts["playing"], 4)
            counts["moods"] = max(counts["moods"], 3)
        elif mode == "Focused":
            counts = {k: min(v, 1 if k not in ["instruments", "production"] else 2) for k, v in counts.items()}
            settings.cohesion = max(settings.cohesion, 90)
            settings.weirdness = min(settings.weirdness, 5)
            bundle_weight = 0.0
        elif mode == "Dense":
            counts["genres"] = max(counts["genres"], 3)
            counts["instruments"] = max(counts["instruments"], 7)
            counts["playing"] = max(counts["playing"], 5)
            counts["production"] = max(counts["production"], 5)
            bundle_weight = 0.0
        else:
            # Backwards compatibility for older saved settings.
            if mode == "Balanced":
                settings.cohesion = max(settings.cohesion, 75)
            elif mode == "Random":
                settings.cohesion = min(settings.cohesion, 40)
                settings.weirdness = max(settings.weirdness, 45)
            elif mode == "Minimal":
                counts = {k: min(v, 1 if k not in ["instruments", "production"] else 2) for k, v in counts.items()}

        if associations_active:
            picked = {
                "genres": self.pick_associated(rng, "genres", counts["genres"], assoc_data, settings, bundle_data, bundle_weight),
                "instruments": self.pick_associated(rng, "instruments", counts["instruments"], assoc_data, settings, bundle_data, bundle_weight),
                "playing": self.pick_associated(rng, "playing", counts["playing"], assoc_data, settings, bundle_data, bundle_weight),
                "moods": self.pick_associated(rng, "moods", counts["moods"], assoc_data, settings, bundle_data, bundle_weight),
                "eras": self.pick_associated(rng, "eras", counts["eras"], assoc_data, settings, bundle_data, bundle_weight),
                "vocals": self.pick_associated(rng, "vocals", counts["vocals"], assoc_data, settings, bundle_data, bundle_weight),
                "production": self.pick_associated(rng, "production", counts["production"], assoc_data, settings, bundle_data, bundle_weight),
                "avoid": self.pick_associated(rng, "avoid", counts["avoid"], assoc_data, settings, bundle_data, bundle_weight),
            }
        else:
            picked = {
                "genres": self.pick(rng, "genres", counts["genres"], bundle_data, bundle_weight),
                "instruments": self.pick(rng, "instruments", counts["instruments"], bundle_data, bundle_weight),
                "playing": self.pick(rng, "playing", counts["playing"], bundle_data, bundle_weight),
                "moods": self.pick(rng, "moods", counts["moods"], bundle_data, bundle_weight),
                "eras": self.pick(rng, "eras", counts["eras"], bundle_data, bundle_weight),
                "vocals": self.pick(rng, "vocals", counts["vocals"], bundle_data, bundle_weight),
                "production": self.pick(rng, "production", counts["production"], bundle_data, bundle_weight),
                "avoid": self.pick(rng, "avoid", counts["avoid"], bundle_data, bundle_weight),
            }

        if mode == "Chaos":
            rng.shuffle(picked["genres"])
            rng.shuffle(picked["instruments"])
            rng.shuffle(picked["playing"])

        prompt_parts = []
        base_prompt = re.sub(r"\s+", " ", settings.base_prompt).strip(" ;,")
        if base_prompt:
            prompt_parts.append(base_prompt)
        if picked["genres"] and not (settings.simple_append_only and base_prompt):
            prompt_parts.append(", ".join(picked["genres"]))
        if picked["instruments"]:
            prompt_parts.append("featuring " + ", ".join(picked["instruments"]))
        if picked["playing"]:
            prompt_parts.append(", ".join(picked["playing"]))
        if picked["moods"]:
            prompt_parts.append(", ".join(picked["moods"]))
        if picked["eras"]:
            prompt_parts.append(", ".join(picked["eras"]))
        if picked["vocals"]:
            prompt_parts.append(", ".join(picked["vocals"]))
        if picked["production"]:
            prompt_parts.append(", ".join(picked["production"]))
        if picked["avoid"]:
            prompt_parts.append(", ".join(picked["avoid"]))

        prompt = "; ".join(prompt_parts)
        prompt = self.trim_prompt(prompt, settings.max_chars)

        self.output.blockSignals(True)
        self.output.setPlainText(prompt)
        self.output.blockSignals(False)

        self.breakdown.setPlainText(
            "Breakdown\n\n"
            f"Mode: {settings.mode}\n"
            f"Association engine: {'on' if associations_active else 'off'}\n"
            f"Base prompt: {settings.base_prompt or '(none)'}\n"
            f"Base style: {active_style_label}\n"
            f"Blend enabled: {'yes' if settings.blend_enabled and blend_names else 'no'}\n"
            f"Cohesion: {settings.cohesion}% | Mutation: {settings.weirdness}% | Allow excluded: {settings.allow_excluded}\n\n"
            f"Genres: {', '.join(picked['genres'])}\n"
            f"Instruments: {', '.join(picked['instruments'])}\n"
            f"Playing: {', '.join(picked['playing'])}\n"
            f"Moods: {', '.join(picked['moods'])}\n"
            f"Eras: {', '.join(picked['eras'])}\n"
            f"Vocals: {', '.join(picked['vocals'])}\n"
            f"Production: {', '.join(picked['production'])}\n"
            f"Avoid: {', '.join(picked['avoid'])}"
        )
        self.update_count()

    def trim_prompt(self, prompt: str, limit: int) -> str:
        if len(prompt) <= limit:
            return prompt

        parts = [p.strip() for p in prompt.split(";") if p.strip()]
        while parts and len("; ".join(parts)) > limit:
            longest_index = max(range(len(parts)), key=lambda i: len(parts[i]))
            chunk = parts[longest_index]
            comma_parts = [p.strip() for p in chunk.split(",") if p.strip()]
            if len(comma_parts) > 1:
                comma_parts.pop()
                parts[longest_index] = ", ".join(comma_parts)
            else:
                parts.pop(longest_index)

        trimmed = "; ".join(parts)
        if len(trimmed) > limit:
            trimmed = trimmed[: max(0, limit - 3)].rstrip(" ,;") + "..."
        return trimmed

    def update_count(self) -> None:
        count = len(self.output.toPlainText())
        limit = self.max_chars_spin.value() if hasattr(self, "max_chars_spin") else MAX_PROMPT_CHARS
        self.char_label.setText(f"{count} / {limit}")
        self.char_label.setStyleSheet("color: #a33;" if count > limit else "")

    def copy_prompt(self) -> None:
        QGuiApplication.clipboard().setText(self.output.toPlainText())
        self.statusBar().showMessage("Copied to clipboard", 2500)

    def save_prompt_to_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save prompt", "suno_style_prompt.txt", "Text Files (*.txt)")
        if path:
            Path(path).write_text(self.output.toPlainText(), encoding="utf-8")
            self.statusBar().showMessage("Prompt saved", 2500)


def main() -> None:
    app = QApplication(sys.argv)
    win = Mishmasher()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
