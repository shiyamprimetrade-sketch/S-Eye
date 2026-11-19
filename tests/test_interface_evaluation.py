import importlib.util
from pathlib import Path
import unittest
from seye.interface.evaluation import summarize
from seye.core.storage import checksum

spec=importlib.util.spec_from_file_location('stage89',Path(__file__).parents[1]/'scripts/benchmark_stage89.py')
benchmark=importlib.util.module_from_spec(spec);spec.loader.exec_module(benchmark)


def case(identifier='one', expected='visual_candidate', actual='visual_candidate'):
    return {'id':identifier,'family':'run','theme':'dark','scale':1,'state':'single',
            'expected_status':expected,'observed_status':actual,
            'expected_boxes':[[10,10,30,30]] if expected=='visual_candidate' else [[10,10,30,30],[50,10,70,30]] if expected=='ambiguous' else [],
            'candidate':{'box':[10,10,30,30]} if actual=='visual_candidate' else None,
            'expected_change':{'signal':'pixels_unchanged','changed_pixels':0},
            'change':{'signal':'pixels_unchanged','changed_pixels':0}}


class InterfaceEvaluationTests(unittest.TestCase):
    def test_wrong_location_is_false_positive_and_false_negative_even_if_status_matches(self):
        row=case();row['candidate']['box']=[70,70,90,90]
        report=summarize([row])
        self.assertEqual(report['status_matches'],1)
        self.assertEqual(report['localization']['true_positives'],0)
        self.assertEqual(report['localization']['false_positives'],1)
        self.assertEqual(report['localization']['false_negatives'],1)
        self.assertEqual(len(report['error_examples']),1)

    def test_negative_and_duplicate_unsafe_choices_are_counted(self):
        report=summarize([case('absent','not_found'),case('duplicate','ambiguous')])
        self.assertEqual(report['negative_rejection']['false_accepts'],1)
        self.assertEqual(report['ambiguity_safety']['unsafe_single_choices'],1)
        self.assertEqual(report['localization']['false_positives'],2)
        self.assertEqual(report['by_condition']['family']['run']['cases'],2)

    def test_execution_failure_is_not_silently_excluded(self):
        row=case(actual='execution_error');row['error']='controlled failure'
        report=summarize([row])
        self.assertEqual(report['requested_cases'],1)
        self.assertEqual(report['completed_cases'],0)
        self.assertEqual(report['status_confusion_matrix']['visual_candidate']['execution_error'],1)
        self.assertEqual(report['localization']['false_negatives'],1)
        self.assertEqual(report['change_oracle']['eligible_completed_cases'],0)
        self.assertIsNone(report['representative_application_accuracy'])

    def test_invalid_oracles_and_actionable_abstentions_are_rejected(self):
        for mutation in ({'expected_status':'invented'}, {'expected_boxes':[]},
                         {'observed_status':'not_found'}, {'expected_boxes':[[10,10,10,30]]}, {'expected_change':{}}, {'change':{}}):
            row=case();row.update(mutation)
            with self.assertRaises(ValueError):summarize([row])
        with self.assertRaises(ValueError):summarize([case(),case()])
        with self.assertRaises(ValueError):summarize([case()],iou_threshold=float('nan'))
        with self.assertRaises(ValueError):summarize([])

    def test_renderer_oracle_is_deterministic_and_analytic_counts_match_pixels(self):
        identities=[]
        for iteration in range(2):
            rows=[]
            for metadata,before,after,template in benchmark.fixtures():
                if before.size==after.size:
                    # Verify analytic construction metadata independently from observer output.
                    count=sum(any(abs(a-b)>=20 for a,b in zip(first,second))
                              for first,second in zip(before.get_flattened_data(),after.get_flattened_data()))
                    self.assertEqual(count,metadata['expected_change']['changed_pixels'])
                rows.append([metadata,checksum(list(before.get_flattened_data())),checksum(list(after.get_flattened_data()))])
            identities.append(checksum(rows))
            self.assertEqual(len(rows),75)
        self.assertEqual(identities[0],identities[1])

    def test_reproducible_full_experiment_retains_negative_generalization_results(self):
        report=benchmark.run();summary=report['summary']
        self.assertEqual(summary['completed_cases'],75)
        self.assertEqual(summary['execution_errors'],0)
        self.assertEqual(summary['change_oracle']['exact_matches'],75)
        self.assertEqual(summary['localization']['true_positives'],3)
        self.assertEqual(summary['localization']['false_negatives'],15)
        self.assertEqual(summary['localization']['false_positives'],0)
        self.assertEqual(summary['ambiguity_safety']['unsafe_single_choices'],0)
        self.assertEqual(summary['by_condition']['theme']['light']['localized_unique_targets'],0)
        self.assertEqual(summary['by_condition']['scale']['1.5']['localized_unique_targets'],0)
        self.assertIsNone(summary['representative_application_accuracy'])
        cursor=next(c for c in report['cases'] if c['id']=='tiny_cursor')
        self.assertEqual(cursor['change']['regions'],[])
        self.assertEqual(cursor['change']['changed_pixels'],4)
