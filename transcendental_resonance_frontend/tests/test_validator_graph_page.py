import inspect
from pages.validator_graph_page import validator_graph_page


def test_validator_graph_page_is_async():
    assert inspect.iscoroutinefunction(validator_graph_page)


def test_validator_graph_page_calls_network_analysis_api():
    source = inspect.getsource(validator_graph_page)
    assert "/network-analysis/" in source


def test_validator_graph_page_uses_plotly():
    source = inspect.getsource(validator_graph_page)
    assert "Plotly.newPlot" in source
