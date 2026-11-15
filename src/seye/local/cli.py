"""Local image, overlay, report, memory, annotation and configuration workflows."""
import argparse,json,sqlite3
from pathlib import Path
from seye import __version__
from seye.core.storage import read_json
from seye.local.workspace import ingest,open_workspace,inside


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',action='version',version=__version__)
    p.add_argument('--root',type=Path,help='Explicit allowed root for all workflow input/output paths')
    sub=p.add_subparsers(dest='command',required=True)
    cmd=sub.add_parser('ingest');cmd.add_argument('--images',nargs='+',required=True);cmd.add_argument('--output',required=True);cmd.add_argument('--source-kind',choices=('screenshot','photograph','synthetic'),default='screenshot')
    for name in ('overlays','report','annotate'):
        cmd=sub.add_parser(name);cmd.add_argument('--workspace',required=True);cmd.add_argument('--output',required=True)
        if name=='report':cmd.add_argument('--model')
        if name=='annotate':cmd.add_argument('--draft')
    cmd=sub.add_parser('validate-draft');cmd.add_argument('--workspace',required=True);cmd.add_argument('--draft',required=True)
    cmd=sub.add_parser('memory');cmd.add_argument('--memory',required=True);cmd.add_argument('--output',required=True);cmd.add_argument('--after',type=int,default=0);cmd.add_argument('--limit',type=int,default=20);cmd.add_argument('--expected-snapshot')
    cmd=sub.add_parser('compare');cmd.add_argument('--left',required=True);cmd.add_argument('--right',required=True);cmd.add_argument('--output',required=True);cmd.add_argument('--allow-partial',action='store_true')
    cmd=sub.add_parser('config-init');cmd.add_argument('--output',required=True);cmd.add_argument('--allow-write',action='store_true');cmd.add_argument('--allow-memory',action='store_true');cmd.add_argument('--timeout',type=float,default=30)
    cmd=sub.add_parser('config-inspect');cmd.add_argument('--path',required=True)
    cmd=sub.add_parser('config-migrate');cmd.add_argument('--source',required=True);cmd.add_argument('--output',required=True)
    cmd=sub.add_parser('doctor');cmd.add_argument('--self-test',action='store_true');cmd.add_argument('--require-installed',action='store_true')
    return p


def main(argv=None):
    p=parser();args=p.parse_args(argv)
    if args.command!='doctor' and args.root is None:p.error('--root is required for local file workflows')
    root=args.root
    try:
        if args.command=='doctor':
            from seye.local.doctor import doctor
            result=doctor(args.self_test)
            if args.require_installed and not (result['installed_distribution_matches_code'] and result['installed_cli_registered']):
                print(json.dumps(result,sort_keys=True));return 1
        elif args.command=='ingest':result=ingest(args.images,args.output,root,args.source_kind)
        elif args.command=='overlays':
            from seye.local.overlays import overlay_workspace
            result=overlay_workspace(args.workspace,args.output,root)
        elif args.command=='report':
            from seye.local.reports import build_report
            result=build_report(args.workspace,args.output,root,args.model)
        elif args.command=='memory':
            from seye.local.memory_browser import export_page
            result=export_page(args.memory,args.output,root,args.after,args.limit,args.expected_snapshot)
        elif args.command=='annotate':
            from seye.local.annotation_editor import build_editor
            draft=read_json(inside(args.draft,root),max_bytes=2*1024*1024) if args.draft else None
            result=build_editor(args.workspace,args.output,root,draft)
        elif args.command=='validate-draft':
            from seye.local.annotation_editor import validate_draft
            _,data,digest=open_workspace(args.workspace,root)
            result=validate_draft(read_json(inside(args.draft,root),max_bytes=2*1024*1024),data,digest)
        elif args.command=='compare':
            from seye.local.comparison import export_comparison
            result=export_comparison(args.left,args.right,args.output,root,args.allow_partial)
        elif args.command=='config-init':
            from seye.local.profiles import initialize
            result=initialize(root,args.output,root,args.allow_write,args.allow_memory,args.timeout)
        elif args.command=='config-inspect':
            from seye.local.profiles import inspect
            result=inspect(args.path,root)
        else:
            from seye.local.profiles import migrate
            result=migrate(args.source,args.output,root)
    except (ValueError,OSError,TypeError,KeyError,sqlite3.DatabaseError) as error:
        p.exit(2,'Workflow failed: '+str(error)+'\n')
    print(json.dumps(result,sort_keys=True,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
