# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import logging
from protocols.utils.llm_response_parser import parse_llm_response


def test_parse_llm_response_json():
    text = '{"foo": 1}'
    assert parse_llm_response(text) == {"foo": 1}


def test_parse_llm_response_invalid_returns_text_and_logs(caplog):
    text = '{foo}'
    with caplog.at_level(logging.WARNING):
        result = parse_llm_response(text)
    assert result == text
    assert any('Failed to parse LLM response' in rec.message for rec in caplog.records)
