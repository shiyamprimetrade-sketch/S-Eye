#!/usr/bin/env python3
"""Audit v1.0 gates without converting implemented prototypes into false completion."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from seye.core.storage import atomic_json, read_json

ROOT = Path(__file__).resolve().parents[1]


def audit():
    registry = read_json(ROOT / 'tasks/stages_086_199.json')
    if [row['stage'] for row in registry['stages']] != list(range(86, 200)):
        raise ValueError('Stage registry must cover every stage 86 through 199 exactly once')
    missing = sorted({path for row in registry['stages'] for path in row['evidence_paths'] if not (ROOT / path).is_file()})
    report_path = ROOT / 'benchmarks/independent_system.json'
    experiment = read_json(report_path) if report_path.exists() else None
    transcript = ROOT / 'benchmarks/system_verification.txt'
    tests_passed = transcript.exists() and '\nOK\n' in transcript.read_text() and '\nFAILED' not in transcript.read_text()
    gates = {'source_inventory_present': not missing,
             'local_regression_suite_passed': tests_passed,
             'independent_model_checkpoint_restored': bool(experiment and experiment['checkpoint_prediction_equivalence']),
             'memory_integrity_and_restore_measured': bool(experiment and experiment['memory']['integrity'] == experiment['memory']['restored_integrity']),
             'controlled_video_measured': bool(experiment and experiment['video']['processed_frames'] > 0),
             'representative_recognition_validated': bool(experiment and experiment.get('representative_validation')),
             'representative_unknown_rejection_validated': False,
             'representative_scene_and_tracking_validated': False,
             'full_security_and_recovery_review_complete': False,
             'all_mandatory_owner_release_criteria_met': False}
    return {'schema_version': 1, 'target_release': 'S-Eye 1.0', 'release_ready': all(gates.values()),
            'gates': gates, 'missing_evidence_paths': missing,
            'stage_count': len(registry['stages']), 'stages_with_explicit_open_requirements': [r['stage'] for r in registry['stages'] if r['engineering_state'] == 'partial'],
            'status': 'experimental_development_checkpoint',
            'reason': 'Controlled implementation tests do not satisfy representative recognition/video/security and all mandatory v1.0 gates.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-release', action='store_true'); args = parser.parse_args()
    result = audit(); atomic_json(args.output, result); print(json.dumps(result, indent=2))
    raise SystemExit(1 if args.require_release and not result['release_ready'] else 0)
