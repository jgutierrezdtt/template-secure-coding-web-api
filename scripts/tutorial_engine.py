#!/usr/bin/env python3
"""Simple tutorial state engine used by functional tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TutorialState:
    started: bool = False
    completed: bool = False
    current_step: int = 0
    total_steps: int = 30


class TutorialEngine:
    def __init__(self, state_file: Path, total_steps: int = 30) -> None:
        self.state_file = state_file
        self.total_steps = total_steps

    def _write(self, state: TutorialState) -> None:
        payload = {
            "started": state.started,
            "completed": state.completed,
            "current_step": state.current_step,
            "total_steps": state.total_steps,
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _read(self) -> TutorialState:
        if not self.state_file.exists():
            return TutorialState(total_steps=self.total_steps)
        raw = json.loads(self.state_file.read_text(encoding="utf-8"))
        return TutorialState(
            started=raw.get("started", False),
            completed=raw.get("completed", False),
            current_step=raw.get("current_step", 0),
            total_steps=raw.get("total_steps", self.total_steps),
        )

    def start(self) -> TutorialState:
        state = TutorialState(started=True, completed=False, current_step=1, total_steps=self.total_steps)
        self._write(state)
        return state

    def validate_step(self, step: int) -> TutorialState:
        state = self._read()
        if not state.started:
            raise ValueError("Tutorial not started")
        if state.completed:
            raise ValueError("Tutorial already completed")
        if step != state.current_step:
            raise ValueError(f"Expected step {state.current_step}, got {step}")

        if state.current_step < state.total_steps:
            state.current_step += 1
        else:
            state.completed = True
        self._write(state)
        return state

    def complete(self) -> TutorialState:
        state = self._read()
        if not state.started:
            raise ValueError("Tutorial not started")
        if state.current_step != state.total_steps and not state.completed:
            raise ValueError("Cannot complete tutorial before final step")
        state.completed = True
        self._write(state)
        return state

    def reset(self) -> TutorialState:
        state = TutorialState(started=False, completed=False, current_step=0, total_steps=self.total_steps)
        self._write(state)
        return state