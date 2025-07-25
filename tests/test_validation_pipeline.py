import json
from validation_certifier import analyze_validation_integrity

def test_sample_data_analysis():
    with open("sample_validations.json") as f:
        data = json.load(f)
        validations = data.get("validations", [])
    
    result = analyze_validation_integrity(validations)
    
    assert "recommended_certification" in result
    assert result["consensus_score"] > 0
    assert result["validator_count"] == len(validations)
    assert isinstance(result["integrity_analysis"], dict)
