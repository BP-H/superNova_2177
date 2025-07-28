import json
from pathlib import Path
from validation_certifier import analyze_validation_integrity

DATA_FILE = Path(__file__).resolve().parents[1] / "sample_validations.json"


def test_sample_data_analysis():
    with open(DATA_FILE) as f:
        data = json.load(f)
        validations = data.get("validations", [])
    
    result = analyze_validation_integrity(validations)
    
    assert "recommended_certification" in result
    assert result["consensus_score"] in (0, 100)
    assert result["validator_count"] == len(validations)
    assert isinstance(result["integrity_analysis"], dict)
