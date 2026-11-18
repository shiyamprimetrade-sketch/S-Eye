#!/usr/bin/env python3
"""Audit v1.0 gates without converting implemented prototypes into false completion."""
import argparse
import json
import hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from seye.core.storage import atomic_json, read_json

ROOT = Path(__file__).resolve().parents[1]


def audit(checkpoint=None):
    registry = read_json(ROOT / 'tasks/stages_086_199.json')
    if [row['stage'] for row in registry['stages']] != list(range(86, 200)):
        raise ValueError('Stage registry must cover every stage 86 through 199 exactly once')
    missing = sorted({path for row in registry['stages'] for path in row['evidence_paths'] if not (ROOT / path).is_file()})
    current_evidence = None
    if checkpoint is not None:
        current_evidence = read_json(checkpoint)
        inventory = {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / 'src/seye').rglob('*.py'))
        }
        if (current_evidence.get('source_sha256') != inventory
                or current_evidence.get('schema_version') != 1
                or current_evidence.get('scope') != 'controlled generated development checkpoint'):
            raise ValueError('Checkpoint evidence does not match current source')
    historical_transcript = ROOT / 'benchmarks/system_verification.txt'
    historical_tests_passed = '\nOK\n' in historical_transcript.read_text(encoding='utf-8')
    gates = {'source_inventory_present': not missing,
             'historical_regression_transcript_passed': historical_tests_passed,
             'current_controlled_checkpoint_verified': bool(current_evidence and current_evidence.get('historical_counts_preserved')),
             'independent_model_checkpoint_restored': bool(current_evidence and current_evidence.get('model_roundtrip')),
             'memory_integrity_and_restore_measured': bool(current_evidence and current_evidence['visual_memory']['restored_observations'] == 128),
             'controlled_video_measured': bool(current_evidence and current_evidence['video']['mp4_frames'] == 6),
             'representative_recognition_validated': False,
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
    parser.add_argument('--checkpoint', type=Path, help='Fresh output from verify_final_checkpoint.py')
    parser.add_argument('--require-release', action='store_true'); args = parser.parse_args()
    result = audit(args.checkpoint); atomic_json(args.output, result); print(json.dumps(result, indent=2))
    raise SystemExit(1 if args.require_release and not result['release_ready'] else 0)
