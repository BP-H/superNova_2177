#!/usr/bin/env python3
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""
validate_hypothesis.py — CLI Interface for superNova_2177 Validation Pipeline

Command-line interface for comprehensive hypothesis validation using the unified
v4.6 validation pipeline. Provides easy access to quality scoring, diversity
analysis, reputation tracking, temporal consistency, and coordination detection.

Usage Examples:
    python validate_hypothesis.py --demo
    python validate_hypothesis.py --validations data.json
    python validate_hypothesis.py --hypothesis HYP_12345 --db-url sqlite:///test.db
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db_models import HypothesisRecord, LogEntry

# Import the unified validation pipeline
try:
    from validation_certifier import analyze_validation_integrity, certify_validations
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import validation pipeline: {e}")
    print("🔧 Make sure validation_certifier.py and dependencies are available")
    PIPELINE_AVAILABLE = False

def generate_demo_validations() -> List[Dict[str, Any]]:
    """Generate realistic demo validation data for testing."""
    
    # Sample validator profiles
    validators = [
        {"id": "validator_alice", "specialty": "machine_learning", "affiliation": "MIT"},
        {"id": "validator_bob", "specialty": "statistics", "affiliation": "Stanford"}, 
        {"id": "validator_carol", "specialty": "neuroscience", "affiliation": "Harvard"},
        {"id": "validator_david", "specialty": "machine_learning", "affiliation": "Google"},
        {"id": "validator_eve", "specialty": "philosophy", "affiliation": "Oxford"},
        {"id": "validator_frank", "specialty": "statistics", "affiliation": "MIT"},
    ]
    
    # Generate timestamps with some clustering for temporal analysis
    base_time = datetime.utcnow() - timedelta(days=2)
    
    validations = []
    for i, validator in enumerate(validators):
        # Add some temporal variation
        if i < 2:  # First two close together (potential coordination)
            timestamp = base_time + timedelta(minutes=i*2)
        else:
            timestamp = base_time + timedelta(hours=i*4, minutes=random.randint(0, 30))
        
        # Generate realistic scores with some variation
        base_score = 0.75 + random.uniform(-0.2, 0.2)
        if validator["specialty"] == "machine_learning":
            base_score += 0.1  # ML validators slightly more positive
        
        validation = {
            "validator_id": validator["id"],
            "hypothesis_id": "HYP_DEMO_001",
            "score": round(max(0.0, min(1.0, base_score)), 2),
            "confidence": round(random.uniform(0.6, 0.9), 2),
            "signal_strength": round(random.uniform(0.5, 0.8), 2),
            "note": random.choice([
                "Strong empirical evidence supports this hypothesis",
                "Methodology appears sound, results convincing", 
                "Some concerns about sample size but generally positive",
                "Innovative approach with promising results",
                "Well-designed study with clear implications",
                "Statistical analysis is rigorous and appropriate"
            ]),
            "timestamp": timestamp.isoformat(),
            "specialty": validator["specialty"],
            "affiliation": validator["affiliation"]
        }
        validations.append(validation)
    
    return validations

def format_analysis_output(result: Dict[str, Any]) -> str:
    """Format analysis results for readable CLI output."""
    
    output = []
    output.append("🔬 HYPOTHESIS VALIDATION ANALYSIS")
    output.append("=" * 50)
    
    # Basic certification info
    certification = result.get("recommended_certification", "unknown")
    consensus_score = result.get("consensus_score", 0.0)
    validator_count = result.get("validator_count", 0)
    
    # Status emoji based on certification
    status_emoji = {
        "strong": "✅",
        "provisional": "⚠️", 
        "experimental": "🧪",
        "disputed": "❌",
        "weak": "⚠️",
        "insufficient_data": "❓"
    }.get(certification, "❓")
    
    output.append(f"\n{status_emoji} CERTIFICATION: {certification.upper()}")
    output.append(f"📊 Consensus Score: {consensus_score}")
    output.append(f"👥 Validators: {validator_count}")
    
    # Integrity analysis (if available)
    integrity = result.get("integrity_analysis", {})
    if integrity and "overall_integrity_score" in integrity:
        integrity_score = integrity["overall_integrity_score"]
        risk_level = integrity.get("risk_level", "unknown")
        
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")
        
        output.append(f"\n🛡️  INTEGRITY ANALYSIS")
        output.append(f"{risk_emoji} Risk Level: {risk_level.upper()}")
        output.append(f"🎯 Integrity Score: {integrity_score}/1.0")
        
        # Component scores
        components = integrity.get("component_scores", {})
        if components:
            output.append(f"\n📈 Component Breakdown:")
            output.append(f"   🎨 Diversity: {components.get('diversity', 0):.2f}")
            output.append(f"   ⭐ Reputation: {components.get('reputation', 0):.2f}")
            output.append(f"   ⏰ Temporal: {components.get('temporal_trust', 0):.2f}")
            output.append(f"   🤝 Coordination: {components.get('coordination_safety', 0):.2f}")
    
    # Flags and warnings
    flags = result.get("flags", [])
    if flags:
        output.append(f"\n⚠️  FLAGS ({len(flags)}):")
        for flag in flags[:5]:  # Limit to first 5 flags
            output.append(f"   • {flag.replace('_', ' ').title()}")
        if len(flags) > 5:
            output.append(f"   ... and {len(flags) - 5} more")
    
    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations and recommendations != ["No specific recommendations"]:
        output.append(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:3], 1):
            output.append(f"   {i}. {rec}")
    
    # Analysis timestamp
    timestamp = result.get("analysis_timestamp", "unknown")
    if timestamp != "unknown":
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            output.append(f"\n🕒 Analyzed: {formatted_time}")
        except ValueError:
            # Malformed timestamp; fall back to the raw string
            output.append(f"\n🕒 Analyzed: {timestamp}")
    
    return "\n".join(output)

def load_validations_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Load validation data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Handle both direct list and wrapped format
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "validations" in data:
            return data["validations"]
        else:
            print(f"❌ Error: Invalid JSON format in {filepath}")
            print("Expected either a list of validations or {'validations': [...]}")
            return []
            
    except FileNotFoundError:
        print(f"❌ Error: File {filepath} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {filepath}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="🔬 superNova_2177 Hypothesis Validation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo                           # Run with demo data
  %(prog)s --validations data.json         # Analyze validation file
  %(prog)s --demo --basic                   # Run basic analysis only
  %(prog)s --validations data.json --output result.json  # Save results

For more information: https://github.com/yourusername/superNova_2177
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--demo", 
        action="store_true",
        help="Run analysis with generated demo data"
    )
    input_group.add_argument(
        "--validations",
        type=str,
        help="Path to JSON file containing validation data"
    )
    input_group.add_argument(
        "--hypothesis",
        type=str, 
        help="Hypothesis ID to analyze (requires --db-url)"
    )
    
    # Analysis options
    parser.add_argument(
        "--basic",
        action="store_true",
        help="Run basic certification only (skip full integrity analysis)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--db-url",
        type=str,
        help="Database URL for hypothesis lookup (e.g., sqlite:///data.db)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation data"
    )
    
    args = parser.parse_args()
    
    # Check pipeline availability
    if not PIPELINE_AVAILABLE:
        print("❌ Cannot run analysis: validation pipeline not available")
        return 1
    
    # Load validation data
    validations = []
    
    if args.demo:
        print("🎲 Generating demo validation data...")
        validations = generate_demo_validations()
        print(f"✅ Generated {len(validations)} demo validations")
        
    elif args.validations:
        print(f"📂 Loading validations from {args.validations}...")
        validations = load_validations_from_file(args.validations)
        if not validations:
            return 1
        print(f"✅ Loaded {len(validations)} validations")
        
    elif args.hypothesis:
        if not args.db_url:
            print("❌ --db-url is required when using --hypothesis")
            return 1

        print(f"🔗 Connecting to database at {args.db_url}...")
        engine = create_engine(
            args.db_url,
            connect_args={"check_same_thread": False} if "sqlite" in args.db_url else {},
        )
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            record = (
                session.execute(
                    select(HypothesisRecord).filter_by(id=args.hypothesis)
                )
                .scalars()
                .first()
            )
            if not record:
                print(f"❌ Hypothesis {args.hypothesis} not found in database")
                return 1

            log_ids = record.validation_log_ids or []
            if not log_ids:
                print(f"❌ No validations found for hypothesis {args.hypothesis}")
                return 1

            log_entries = (
                session.execute(
                    select(LogEntry).filter(LogEntry.id.in_(log_ids))
                )
                .scalars()
                .all()
            )
            for entry in log_entries:
                try:
                    payload = json.loads(entry.payload) if entry.payload else {}
                except json.JSONDecodeError:
                    continue

                validation = payload.get("validation", payload)
                if isinstance(validation, dict):
                    validation.setdefault("hypothesis_id", args.hypothesis)
                    validations.append(validation)

            if not validations:
                print(f"❌ No valid validation payloads found for {args.hypothesis}")
                return 1

            print(f"✅ Retrieved {len(validations)} validations from database")
        finally:
            session.close()
    
    # Show validation data if verbose
    if args.verbose and validations:
        print(f"\n📋 VALIDATION DATA:")
        print("-" * 30)
        for i, val in enumerate(validations[:3], 1):
            validator = val.get("validator_id", "unknown")
            score = val.get("score", 0)
            print(f"{i}. {validator}: {score}/1.0")
        if len(validations) > 3:
            print(f"... and {len(validations) - 3} more")
    
    # Run analysis
    print(f"\n🔄 Running {'basic' if args.basic else 'comprehensive'} analysis...")
    
    try:
        if args.basic:
            result = certify_validations(validations)
        else:
            result = analyze_validation_integrity(validations)
        
        # Display results
        print("\n" + format_analysis_output(result))
        
        # Save output if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        print(f"\n✨ Analysis complete!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
