#!/usr/bin/env python3
"""Functional tests for Secure Coding Web API tutorial flow and event wiring."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from tutorial_engine import TutorialEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
STEPS_DIR = REPO_ROOT / ".tutorial" / "steps"
README = REPO_ROOT / "README.md"
CONFIG = REPO_ROOT / ".tutorial" / "config.yml"


def load_total_steps() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    return int(cfg["tutorial"]["total_steps"])


class TutorialFunctionalTests(unittest.TestCase):
    def test_required_workflows_exist(self) -> None:
        required = [
            "start.yml",
            "validate.yml",
            "reset-tutorial.yml",
            "update-from-template.yml",
            "completion.yml",
            "test-tutorial.yml",
            "functional-tests.yml",
        ]
        for wf in required:
            self.assertTrue((WORKFLOWS / wf).exists(), f"Missing workflow {wf}")

    def test_workflow_events_detected(self) -> None:
        manual = ["start.yml", "validate.yml", "reset-tutorial.yml", "completion.yml"]
        for wf in manual:
            doc = yaml.safe_load((WORKFLOWS / wf).read_text(encoding="utf-8"))
            events = doc.get("on", doc.get(True))
            self.assertIsNotNone(events, f"Workflow {wf} missing 'on'")
            self.assertIn("workflow_dispatch", events, f"Workflow {wf} missing workflow_dispatch")

        test_doc = yaml.safe_load((WORKFLOWS / "functional-tests.yml").read_text(encoding="utf-8"))
        events = test_doc.get("on", test_doc.get(True))
        self.assertIsNotNone(events)
        self.assertIn("workflow_dispatch", events)
        self.assertIn("push", events)
        self.assertIn("pull_request", events)

    def test_readme_guided_flow_is_present(self) -> None:
        text = README.read_text(encoding="utf-8")
        # When the tutorial is complete the README becomes a certificate -- that is valid
        if "Certificado de finalizacion" in text:
            return
        self.assertIn("Empezar tutorial", text)
        self.assertIn("Tabla de pasos", text)
        self.assertIn("Paso 0", text)

    def test_steps_exist_and_have_required_sections(self) -> None:
        total = load_total_steps()
        required_sections = [
            ["## Objetivo de aprendizaje"],
            ["## Por que importa esto"],
            ["## Que vas a cambiar y por que"],
            ["## Archivo y seccion que debes modificar"],
            ["## Cambio base recomendado"],
            ["## Que te esta enseñando este cambio"],
            ["## Como adaptarlo correctamente"],
            ["## Que deberia verse al terminar"],
            ["## Que valida el workflow automaticamente"],
            ["## Criterio de finalizacion"],
        ]

        self.assertTrue((STEPS_DIR / "00-introduccion.md").exists(), "Missing step 00")

        for i in range(1, total + 1):
            matches = list(STEPS_DIR.glob(f"{i:02d}-*.md"))
            self.assertEqual(len(matches), 1, f"Expected one file for step {i:02d}")
            text = matches[0].read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"# Paso {i}."), f"Invalid title in step {i:02d}")
            for variants in required_sections:
                found = any(v in text for v in variants)
                self.assertTrue(found, f"Step {i:02d} missing section: {' or '.join(variants)}")

    def test_end_to_end_tutorial_state_machine(self) -> None:
        total = load_total_steps()
        with tempfile.TemporaryDirectory() as tmp:
            state_file = Path(tmp) / ".tutorial" / "state.test.json"
            engine = TutorialEngine(state_file=state_file, total_steps=total)

            started = engine.start()
            self.assertTrue(started.started)
            self.assertEqual(started.current_step, 1)

            for step in range(1, total):
                state = engine.validate_step(step)
                self.assertEqual(state.current_step, step + 1)
                self.assertFalse(state.completed)

            final_state = engine.validate_step(total)
            self.assertTrue(final_state.completed)

            completed = engine.complete()
            self.assertTrue(completed.completed)

            reset = engine.reset()
            self.assertFalse(reset.started)
            self.assertFalse(reset.completed)
            self.assertEqual(reset.current_step, 0)


if __name__ == "__main__":
    unittest.main()
