#!/usr/bin/env python3
"""Exercise the installed package from outside the source checkout."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

with tempfile.TemporaryDirectory(prefix='seye_installed_') as directory:
    root = Path(directory)
    image = Image.new('RGB', (300, 300), 'white')
    ImageDraw.Draw(image).polygon([(150, 60), (70, 225), (230, 225)], outline='black', width=5)
    source = root / 'triangle.png'
    image.save(source)
    result = subprocess.run([sys.executable, '-c',
                             'from seye.api.cli import main; raise SystemExit(main())',
                             '--image', str(source), '--output-dir', str(root / 'output'),
                             '--allowed-root', str(root)], cwd=root, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise SystemExit(result.stderr)
    report = json.loads((root / 'output/analysis.json').read_text())
    assert [row['class'] for row in report['objects']] == ['triangle'], report
    assert (root / 'output/overlay.png').is_file()
    request = root / 'request.json'
    request.write_text(json.dumps({'schema_version': 1, 'request_id': 'installed-smoke', 'action': 'analyze', 'image': str(source)}))
    workflow = subprocess.run([sys.executable, '-m', 'seye.api.workflow', '--request', str(request),
                               '--output', str(root / 'workflow.json'), '--read-root', str(root), '--write-root', str(root)],
                              cwd=root, capture_output=True, text=True, timeout=120)
    assert workflow.returncode == 0, workflow.stderr
    assert json.loads((root / 'workflow.json').read_text())['success']
    module = subprocess.check_output([sys.executable, '-c', 'import seye; print(seye.__file__)'], cwd=root, text=True).strip()
    print(json.dumps({'installed_module': module, 'class': 'triangle', 'overlay_created': True,
                      'source_sha256': report['source']['sha256'], 'executed_outside_checkout': True, 'versioned_workflow_passed': True}, indent=2))
