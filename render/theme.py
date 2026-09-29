"""Loads theme.json so titles and credits can be re-skinned without touching drawing code."""
import json, os
T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "theme.json"), encoding="utf-8"))
