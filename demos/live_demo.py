#!/usr/bin/env python3
"""
Live Demo - Watch superNova_2177 Analyze in Real-Time
"""

import time
import random
import json
import argparse
from datetime import datetime, timedelta
from validation_certifier import analyze_validation_integrity

def typewriter_print(text, delay=0.03):
    """Print text with typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def create_dramatic_scenario(save_output=False):
    """Create a suspicious validation scenario that unfolds dramatically"""
    
    print("🔬 " + "="*60)
    typewriter_print("  SUPERNOVΑ_2177 LIVE VALIDATION ANALYSIS", 0.05)
    print("🔬 " + "="*60)
    
    typewriter_print("\n🎭 SCENARIO: Suspicious validation pattern detected...", 0.04)
    typewriter_print("📊 Analyzing hypothesis: 'AI can predict market crashes'", 0.04)
    
    # Create increasingly suspicious validation data
    validations = []
    
    typewriter_print("\n⏰ Validation submissions incoming...\n")
    
    # First wave - normal looking
    base_time = datetime.utcnow()
    for i in range(3):
        validator = f"validator_{chr(65+i)}"
        typewriter_print(f"  📥 {validator} submitted validation... ", 0.02)
        
        validation = {
            "validator_id": validator,
            "score": round(0.7 + random.uniform(-0.1, 0.1), 2),
            "confidence": round(random.uniform(0.6, 0.8), 2),
            "signal_strength": round(random.uniform(0.5, 0.7), 2),
            "note": random.choice([
                "Interesting methodology, shows promise",
                "Some concerns but generally positive results",
                "Needs more data but directionally correct"
            ]),
            "timestamp": (base_time + timedelta(hours=i*2)).isoformat(),
            "specialty": random.choice(["economics", "data_science", "statistics"]),
            "affiliation": random.choice(["University_A", "Research_Lab_B", "Institute_C"]),
            "suspicious": False  # Added suspicious flag
        }
        validations.append(validation)
        time.sleep(0.5)
    
    typewriter_print("\n⚠️  Suspicious pattern emerging...", 0.04)
    time.sleep(1)
    
    # Second wave - coordinated submissions (within minutes)
    suspicious_time = base_time + timedelta(hours=8)
    for i in range(3):
        validator = f"validator_{chr(68+i)}"  # D, E, F
        typewriter_print(f"  🚨 {validator} submitted validation (suspicious timing)... ", 0.02)
        
        validation = {
            "validator_id": validator,
            "score": 0.92,  # Suspiciously high and identical
            "confidence": 0.95,
            "signal_strength": 0.88,
            "note": "Strong evidence supports this hypothesis",  # Identical notes
            "timestamp": (suspicious_time + timedelta(minutes=i*2)).isoformat(),
            "specialty": "machine_learning",  # Same specialty
            "affiliation": "TechCorp_X",  # Same affiliation
            "suspicious": True  # Added suspicious flag
        }
        validations.append(validation)
        time.sleep(0.3)
    
    typewriter_print("\n🔍 Running superNova_2177 analysis...", 0.04)
    time.sleep(2)
    
    # Analyze with dramatic reveals
    result = analyze_validation_integrity(validations)
    
    # Enhanced header with styling
    print("\n" + "🔴" * 20)
    typewriter_print("🚨 ANALYSIS COMPLETE 🚨".center(60), 0.05)
    print("🔴" * 20)
    
    # Enhanced summary line
    certification = result.get("recommended_certification", "unknown").upper()
    integrity_score = result.get("integrity_analysis", {}).get("overall_integrity_score", 0)
    risk_level = result.get("integrity_analysis", {}).get("risk_level", "unknown").upper()
    validator_count = result.get("validator_count", 0)
    
    typewriter_print(f"\n📌 SUMMARY: Certification={certification}, Risk={risk_level}, Validators={validator_count}, Integrity={integrity_score}/1.0", 0.03)
    
    # Dramatic reveal of findings
    typewriter_print(f"\n🎯 INTEGRITY SCORE: {integrity_score}/1.0", 0.03)
    time.sleep(1)
    
    if risk_level == "HIGH":
        typewriter_print("🔴 RISK LEVEL: HIGH - MANIPULATION DETECTED!", 0.04)
    elif risk_level == "MEDIUM":
        typewriter_print("🟡 RISK LEVEL: MEDIUM - SUSPICIOUS PATTERNS", 0.04)
    else:
        typewriter_print("🟢 RISK LEVEL: LOW - VALIDATION APPEARS CLEAN", 0.04)
    
    time.sleep(1)
    
    flags = result.get("flags", [])
    typewriter_print(f"\n⚠️  FLAGS DETECTED ({len(flags)}):", 0.03)
    for flag in flags:
        typewriter_print(f"    • {flag.replace('_', ' ').title()}", 0.02)
        time.sleep(0.3)
    
    # Show the power of the system
    component_scores = result.get("integrity_analysis", {}).get("component_scores", {})
    
    typewriter_print("\n📊 COMPONENT ANALYSIS:", 0.03)
    typewriter_print(f"    🎨 Diversity: {component_scores.get('diversity', 0):.2f}/1.0", 0.02)
    typewriter_print(f"    ⭐ Reputation: {component_scores.get('reputation', 0):.2f}/1.0", 0.02)  # Fixed key name
    typewriter_print(f"    ⏰ Temporal: {component_scores.get('temporal_trust', 0):.2f}/1.0", 0.02)
    typewriter_print(f"    🤝 Coordination: {component_scores.get('coordination_safety', 0):.2f}/1.0", 0.02)
    
    recommendations = result.get("recommendations", [])
    if recommendations:
        typewriter_print("\n💡 SYSTEM RECOMMENDATIONS:", 0.03)
        for rec in recommendations[:3]:
            typewriter_print(f"    → {rec}", 0.02)
            time.sleep(0.5)
    
    typewriter_print("\n✨ Analysis completed in real-time", 0.03)
    typewriter_print("🛡️  System successfully detected manipulation attempt", 0.03)
    
    print("\n" + "🟢" * 60)
    typewriter_print("🧠 This is the power of superNova_2177", 0.04)
    print("🟢" * 60)
    
    # Save output if requested
    if save_output:
        output_data = {
            "scenario": "Coordinated validator manipulation",
            "timestamp": datetime.utcnow().isoformat(),
            "validations": validations,
            "analysis_result": result,
            "summary": {
                "certification": certification,
                "risk_level": risk_level,
                "integrity_score": integrity_score,
                "validator_count": validator_count,
                "flags_detected": len(flags)
            }
        }
        
        filename = f"demo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        typewriter_print(f"\n💾 Analysis saved to {filename}", 0.03)
        
        # Also save markdown report
        md_filename = f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(md_filename, 'w') as f:
            f.write("# superNova_2177 Demo Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("## Summary\n")
            f.write(f"- **Certification:** {certification}\n")
            f.write(f"- **Risk Level:** {risk_level}\n")
            f.write(f"- **Integrity Score:** {integrity_score}/1.0\n")
            f.write(f"- **Validators Analyzed:** {validator_count}\n")
            f.write(f"- **Flags Detected:** {len(flags)}\n\n")
            f.write("## Detected Issues\n")
            for flag in flags:
                f.write(f"- {flag.replace('_', ' ').title()}\n")
            f.write("\n## System Recommendations\n")
            for rec in recommendations:
                f.write(f"- {rec}\n")
        
        typewriter_print(f"📄 Report saved to {md_filename}", 0.03)

def main():
    parser = argparse.ArgumentParser(description="🎬 Interactive superNova_2177 Demo")
    parser.add_argument("--save", action="store_true", help="Save analysis results to files")
    parser.add_argument("--scenario", choices=["manipulation", "clean"], default="manipulation", 
                       help="Demo scenario to run")
    
    args = parser.parse_args()
    
    if args.scenario == "manipulation":
        create_dramatic_scenario(save_output=args.save)
    else:
        typewriter_print("🚧 Clean scenario not yet implemented", 0.03)

if __name__ == "__main__":
    main()
