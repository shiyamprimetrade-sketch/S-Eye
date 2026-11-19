"""Installation metadata and opt-in generated self-test; no downloads or upgrades."""
import importlib.metadata,platform,shutil,sys,tempfile
from pathlib import Path
from seye import __version__


def doctor(self_test=False):
    if type(self_test) is not bool:raise ValueError('Boolean self-test flag required')
    try:installed=importlib.metadata.version('seye-independent')
    except importlib.metadata.PackageNotFoundError:installed=None
    pillow=importlib.metadata.version('Pillow')
    registered=any(e.name=='seye-local' for e in importlib.metadata.entry_points(group='console_scripts'))
    result={'format':'seye-local-doctor-v1','code_version':__version__,'installed_version':installed,
            'installed_distribution_matches_code':installed==__version__,'installed_cli_registered':registered,
            'python_version':platform.python_version(),'system':platform.system(),'machine':platform.machine(),
            'python_compatible':sys.version_info>=(3,12),'pillow_version':pillow,
            'ffmpeg_available':shutil.which('ffmpeg') is not None and shutil.which('ffprobe') is not None,
            'local_workflow_requirements_present':sys.version_info>=(3,12) and pillow=='13.0.0',
            'self_test':None,'hardware_validation':False,'v1_release':False}
    if self_test:
        from PIL import Image,ImageDraw
        from seye.local.workspace import ingest,open_workspace
        from seye.local.reports import build_report
        with tempfile.TemporaryDirectory(prefix='seye_local_doctor_') as d:
            root=Path(d);path=root/'fixture.png';image=Image.new('RGB',(100,80),'white');ImageDraw.Draw(image).rectangle((10,10,30,30),fill='black');image.save(path)
            ingest([path],root/'workspace',root,source_kind='synthetic');_,data,_=open_workspace(root/'workspace',root);build_report(root/'workspace',root/'report',root)
            result['self_test']={'generated_images':len(data['items']),'workspace_verified':True,'offline_report_created':(root/'report'/'report.html').is_file()}
    return result
