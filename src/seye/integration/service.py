"""Versioned offline S-Memory/S-Tools adapter with explicit filesystem grants.

No network, shell execution or camera action is exposed. This is an independently
exercisable integration contract, not a deployed change to the main S repository.
"""
from dataclasses import dataclass
from pathlib import Path
from seye.core.storage import checksum
from seye.detection.analysis import analyze
from seye.image.ingestion import load_image
from seye.learning.prototypes import load_model, predict, save_model
from seye.learning.dataset import train
from seye.memory.store import Memory
from seye.recognition.features import extract, FEATURE_VERSION
from seye.scenes.relations import inventory
from seye.video.ingestion import analyze_video


@dataclass(frozen=True)
class Permissions:
    read_roots: tuple = ()
    write_roots: tuple = ()
    memory: bool = False
    training: bool = False
    video: bool = False

    def require(self, path, write=False):
        target = Path(path).expanduser().resolve()
        roots = self.write_roots if write else self.read_roots
        if not any(target.is_relative_to(Path(root).expanduser().resolve()) for root in roots):
            raise PermissionError('Requested path is outside explicit filesystem grants')
        return target


def execute(request, permissions):
    if not isinstance(request, dict) or type(request.get('schema_version')) is not int or request['schema_version'] != 1:
        raise ValueError('Integration schema_version=1 required')
    identifier = request.get('request_id')
    if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
        raise ValueError('Request ID required')
    action = request.get('action')
    if action in ('analyze', 'recognize', 'visual_question', 'remember', 'retrieve'):
        image = permissions.require(request['image'])
        if action in ('analyze', 'visual_question', 'remember'):
            report, artifacts = analyze(image, mode=request.get('mode', 'baseline'))
        if action == 'analyze':
            result = report
        elif action == 'visual_question':
            question = request.get('question')
            if question == 'count_geometric_regions':
                result = {'answer': len(report['objects']), 'scope': 'unverified geometric proposals, not semantic object count'}
            elif question == 'list_geometric_classes':
                result = {'answer': [r['class'] for r in report['objects']], 'scope': 'geometric hypotheses'}
            elif question == 'spatial_relations':
                result = inventory(report['objects'])
            else:
                result = {'answer': None, 'unsupported': True, 'reason': 'No supported evidence-grounded query for that question'}
            result['source_sha256'] = report['source']['sha256']
        elif action == 'recognize':
            model = load_model(permissions.require(request['model']))
            decoded, source = load_image(image)
            result = dict(predict(model, extract(decoded)), source_sha256=source['sha256'], model_sha256=checksum(model))
        else:
            if not permissions.memory:
                raise PermissionError('Explicit memory permission required')
            memory_path = permissions.require(request['memory'], write=action == 'remember')
            memory = Memory(memory_path, read_only=action == 'retrieve')
            try:
                if action == 'remember':
                    record = {'schema_version': 1, 'features': extract(artifacts['source']),
                              'feature_version': FEATURE_VERSION, 'analysis': report,
                              'provenance': {'source_sha256': report['source']['sha256'], 'request_id': identifier,
                                             'kind': 'independent_geometry_observation'}}
                    result = {'observation_id': memory.put(record), 'integrity': memory.verify()}
                else:
                    decoded, _ = load_image(image)
                    result = {'matches': memory.search(extract(decoded), request.get('limit', 5))}
            finally:
                memory.close()
    elif action == 'observe_interface':
        from seye.interface.observer import observe
        image = permissions.require(request['image'])
        previous = permissions.require(request['previous']) if request.get('previous') is not None else None
        templates = request.get('templates', [])
        if not isinstance(templates, list) or len(templates) > 8:
            raise ValueError('At most eight explicit templates allowed')
        validated = []
        for entry in templates:
            if not isinstance(entry, dict):
                raise ValueError('Template entry must be an object')
            validated.append({'name': entry['name'], 'path': permissions.require(entry['path'])})
        memory_path = None
        if request.get('memory') is not None:
            if not permissions.memory:
                raise PermissionError('Explicit memory permission required')
            memory_path = permissions.require(request['memory'], write=True)
        result = observe(image, previous, validated, request.get('stride', 4), request.get('min_similarity', .99 if request.get('matcher')=='contrast' else .97), request.get('matcher', 'pixel'), request.get('scales'), request.get('region_proposals', False), request.get('region_mode', 'baseline'))
        if memory_path is not None:
            memory = Memory(memory_path)
            try:
                record = {'schema_version': 1, 'features': None, 'analysis': result,
                          'provenance': {'source_sha256': result['source']['sha256'],
                                         'request_id': identifier, 'kind': 'interface_observation'}}
                result['observation_id'] = memory.put(record)
            finally:
                memory.close()
    elif action == 'extract_features':
        from seye.recognition.pipeline import FeaturePipeline
        decoded,source=load_image(permissions.require(request['image']),max_pixels=4_000_000)
        normalization=None
        if request.get('perspective_quad') is not None:
            from seye.interface.perspective import rectify
            decoded,normalization=rectify(decoded,request['perspective_quad'],request.get('canonical_size',[64,64]))
        elif 'canonical_size' in request:
            raise ValueError('canonical_size requires perspective_quad')
        result=FeaturePipeline().extract(decoded,request.get('components',['interface']))
        result['source']=source
        if normalization is not None:result['normalization']=normalization
    elif action == 'recognize_batch':
        from seye.recognition.cache import FeatureCache
        paths = request.get('images')
        if not isinstance(paths, list) or not 1 <= len(paths) <= 100:
            raise ValueError('Batch requires 1..100 explicit image paths')
        sources = [permissions.require(path) for path in paths]
        model = load_model(permissions.require(request['model']))
        cache = FeatureCache()
        outputs = []
        for path in sources:
            vector, provenance = cache.from_file(path)
            outputs.append(dict(predict(model, vector), source_sha256=provenance['sha256']))
        result = {'predictions': outputs, 'cache': cache.statistics(), 'model_sha256': checksum(model)}
    elif action == 'memory_list':
        if not permissions.memory:
            raise PermissionError('Explicit memory permission required')
        memory = Memory(permissions.require(request['memory']), read_only=True)
        try:
            result = {'observations': memory.recent(request.get('limit', 20))}
        finally:
            memory.close()
    elif action == 'train':
        if not permissions.training:
            raise PermissionError('Explicit independent-training permission required')
        manifest = permissions.require(request['manifest'])
        output = permissions.require(request['output'], write=True)
        if request.get('method', 'prototype') == 'linear':
            from seye.learning.dataset import train_linear
            model, evaluation = train_linear(manifest)
        elif request.get('method', 'prototype') == 'prototype':
            model, evaluation = train(manifest)
        else:
            raise ValueError('Training method must be prototype or linear')
        save_model(output, model)
        result = {'checkpoint': str(output), 'model_sha256': checksum(model), 'evaluation': evaluation}
    elif action == 'video':
        if not permissions.video:
            raise PermissionError('Explicit prerecorded-video permission required')
        path = permissions.require(request['video'])
        result = analyze_video(path, path.parent, request.get('fps', 2), request.get('max_seconds', 30), request.get('mode', 'baseline'))
    else:
        raise ValueError('Unsupported action; no shell, network or camera tools are available')
    return {'schema_version': 1, 'request_id': identifier, 'success': True, 'result': result}


def handle(request, permissions):
    try:
        return execute(request, permissions)
    except (ValueError, OSError, KeyError, TypeError, __import__("sqlite3").DatabaseError, __import__("subprocess").SubprocessError) as error:
        return {'schema_version': 1, 'request_id': request.get('request_id') if isinstance(request, dict) else None,
                'success': False, 'error': {'type': type(error).__name__, 'message': str(error)}}


def _worker(request, permissions, queue):
    queue.put(handle(request, permissions))


def bounded_handle(request, permissions, timeout=30):
    """Run the adapter in a killable child. Committed side effects remain committed."""
    import math
    import multiprocessing
    from queue import Empty
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 120:
        raise ValueError('Request timeout must be in (0,120] seconds')
    from seye.core.storage import canonical
    if len(canonical(request)) > 1024 * 1024:
        raise ValueError('Integration request exceeds 1 MiB')
    context = multiprocessing.get_context('spawn')
    queue = context.Queue(maxsize=1)
    process = context.Process(target=_worker, args=(request, permissions, queue))
    process.start()
    try:
        result = queue.get(timeout=timeout)
    except Empty:
        result = {'schema_version': 1, 'request_id': request.get('request_id') if isinstance(request, dict) else None,
                  'success': False, 'error': {'type': 'Timeout', 'message': 'Request deadline exceeded; committed memory writes are not undone'}}
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill(); process.join(timeout=2)
        queue.close(); queue.cancel_join_thread()
    return result
