from protocols.utils.llm_utils import parse_llm_response


def test_parse_llm_response_json():
    out = parse_llm_response('{"x": 1}')
    assert out == {"x": 1}


def test_parse_llm_response_text():
    out = parse_llm_response(' just text ')
    assert out == 'just text'
