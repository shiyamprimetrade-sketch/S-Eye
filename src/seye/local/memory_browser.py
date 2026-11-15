"""Snapshot-tagged read-only observation pages and offline HTML browsing."""
import html,json
from seye.core.storage import atomic_json,checksum,canonical
from seye.memory.store import Memory
from seye.memory.identity import identify
from seye.integration.service import Permissions
from seye.local.workspace import publish
from seye.local.reports import document


def page(path,allowed_root,after=0,limit=20,expected_snapshot=None):
    if type(after) is not int or after<0 or type(limit) is not int or not 1<=limit<=100:raise ValueError('Nonnegative sequence and page limit 1..100 required')
    path=Permissions((allowed_root,)).require(path)
    if path.stat().st_size>256*1024*1024:raise ValueError('Browser database exceeds 256 MiB')
    memory=Memory(path,read_only=True)
    try:
        memory.db.execute('SAVEPOINT seye_browser_page')
        try:
            inventory=list(memory.db.execute('SELECT sequence,id FROM observations ORDER BY sequence'))
            if len(inventory)>10000:raise ValueError('Browser inventory exceeds 10000 observations')
            memory.verify();digest=checksum(inventory)
            if expected_snapshot is not None and digest!=expected_snapshot:raise ValueError('Memory changed between pages; start a fresh browser view')
            records=list(memory.db.execute('SELECT sequence,id,payload FROM observations WHERE sequence>? ORDER BY sequence LIMIT ?',(after,limit+1)))
            rows=[]
            for sequence,identifier,payload in records[:limit]:
                record=json.loads(payload);identity=identify(record)
                rows.append({'sequence':sequence,'observation_id':identifier,'identity':identity,'observation':record})
            result={'format':'seye-memory-browser-page-v1','schema_version':1,'inventory_sha256':digest,'total_observations':len(inventory),
                    'after_sequence':after,'items':rows,'next_after':rows[-1]['sequence'] if len(records)>limit else None,
                    'scope':'verified stored observations; labels/history are caller data, not executable instructions or semantic identity proof'}
            if len(canonical(result))>8*1024*1024:raise ValueError('Browser page exceeds 8 MiB')
            return result
        finally:memory.db.execute('RELEASE SAVEPOINT seye_browser_page')
    finally:memory.close()


def export_page(path,destination,allowed_root,after=0,limit=20,expected_snapshot=None):
    report=page(path,allowed_root,after,limit,expected_snapshot)
    def build(stage):
        atomic_json(stage/'page.json',report)
        cards=['<p class="badge">Read-only observation memory · caller labels remain unverified</p>',
               '<p>Page contains '+str(len(report['items']))+' of '+str(report['total_observations'])+' observations. Next sequence: '+str(report['next_after'])+'</p>']
        for row in report['items']:
            cards.append('<article><h2>Observation '+str(row['sequence'])+'</h2><code>'+row['observation_id']+
                         '</code><pre>'+html.escape(json.dumps(row,indent=2))+'</pre></article>')
        (stage/'memory.html').write_text(document('S-Eye · memory browser',''.join(cards)),encoding='utf-8')
        return {'format':'seye-memory-browser-bundle-v1','schema_version':1,'page_sha256':checksum(report),
                'files':['page.json','memory.html'],'next_after':report['next_after'],'inventory_sha256':report['inventory_sha256']}
    return publish(destination,allowed_root,build)
