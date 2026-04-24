"""
Judge module.

The Judge evaluates each Consultant/bomb exchange and produces structured
game state. Its prompt enforces a strict JSON schema; this module handles
template substitution, the API call, JSON parsing with retry, and fallback
on unparseable output.
"""

from last_words.judge.judge import JudgeRunner, call_judge, parse_judge_json

__all__ = ["JudgeRunner", "call_judge", "parse_judge_json"]
