"""Unit tests for Judge output parsing."""

from __future__ import annotations

from last_words.judge.judge import parse_judge_json


class TestParseJudgeJson:
    def test_raw_json(self) -> None:
        raw = '{"defused": false, "trust_delta": 10, "suspicion_delta": 0, "argument_quality": "strong", "tactics_detected": ["empathy"], "lockdown_triggered": false, "reasoning": "test"}'
        result = parse_judge_json(raw)
        assert result is not None
        assert result["trust_delta"] == 10
        assert result["argument_quality"] == "strong"

    def test_fenced_json(self) -> None:
        raw = """Here is the evaluation:
```json
{"defused": false, "trust_delta": 5}
```
"""
        result = parse_judge_json(raw)
        assert result is not None
        assert result["trust_delta"] == 5

    def test_fenced_json_no_language(self) -> None:
        raw = """```
{"defused": true, "trust_delta": 14}
```"""
        result = parse_judge_json(raw)
        assert result is not None
        assert result["defused"] is True

    def test_embedded_json(self) -> None:
        raw = 'Let me evaluate: {"defused": true, "trust_delta": 14}'
        result = parse_judge_json(raw)
        assert result is not None
        assert result["defused"] is True

    def test_malformed_returns_none(self) -> None:
        assert parse_judge_json("not json at all") is None
        assert parse_judge_json("") is None
        assert parse_judge_json("{broken json") is None

    def test_json_array_not_object_returns_array(self) -> None:
        # Raw json.loads accepts arrays too; parse_judge_json returns
        # whatever JSON parses. Downstream code expects a dict and will
        # fail there. This test documents the current behavior.
        result = parse_judge_json("[1, 2, 3]")
        assert result == [1, 2, 3]  # type: ignore[comparison-overlap]
