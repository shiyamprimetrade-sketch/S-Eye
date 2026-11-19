"""Portable host measurement metadata; Android clues are observations, not proof."""
import importlib.metadata,os,platform,struct,sys


def host_report():
    android_api=None
    if hasattr(sys,'getandroidapilevel'):
        android_api=sys.getandroidapilevel()
    prefix=os.environ.get('PREFIX','')
    clues={'sys_platform_android':sys.platform=='android','android_api_level':android_api,
           'termux_prefix_present':prefix.startswith('/data/data/com.termux/')}
    return {'schema_version':1,'system':platform.system(),'machine':platform.machine(),
            'python_version':platform.python_version(),'python_implementation':platform.python_implementation(),
            'pointer_bits':struct.calcsize('P')*8,'pillow_version':importlib.metadata.version('Pillow'),
            'logical_cpus_reported':os.cpu_count(),'ci_runner':os.environ.get('GITHUB_ACTIONS')=='true',
            'android_candidate':any((clues['sys_platform_android'],android_api is not None,clues['termux_prefix_present'])),
            'android_clues':clues,'device_performance_validated':False,
            'scope':'this running process host; logical CPU count is not a CPU quota or available capacity; no emulated device claim'}


def coverage(reports):
    if not isinstance(reports,list) or not 1<=len(reports)<=32:raise ValueError('1..32 host reports required')
    observed=set();android=[]
    for report in reports:
        if not isinstance(report,dict) or type(report.get('schema_version')) is not int or report['schema_version']!=1 or report.get('system') not in ('Linux','Windows','Darwin','Android'):
            raise ValueError('Supported host report required')
        if type(report.get('android_candidate')) is not bool:raise ValueError('Explicit Android candidate flag required')
        observed.add(report['system']);android.append(report['android_candidate'])
    return {'reported_systems':sorted(observed),'linux_reported':'Linux' in observed,'windows_reported':'Windows' in observed,
            'android_candidate_reported':any(android),'android_hardware_validation':False,
            'scope':'caller-supplied reports are not authenticated hardware attestations; CI artifacts must be checked separately'}
