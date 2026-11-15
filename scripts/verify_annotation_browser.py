#!/usr/bin/env python3
"""Optional development-only real Chromium annotation/resize/download check."""
import argparse,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from PIL import Image,ImageDraw
from seye.local.workspace import ingest,open_workspace
from seye.local.annotation_editor import build_editor,validate_draft


def run(screenshots=None):
    from playwright.sync_api import sync_playwright
    rows=[]
    with tempfile.TemporaryDirectory(prefix='seye_editor_browser_') as directory:
        root=Path(directory);source=root/'image.png';image=Image.new('RGB',(500,300),'white');ImageDraw.Draw(image).rectangle((70,50,330,220),outline='black',width=4);image.save(source)
        ingest([source],root/'workspace',root,source_kind='synthetic');_,data,digest=open_workspace(root/'workspace',root)
        build_editor(root/'workspace',root/'editor',root)
        with sync_playwright() as p:
            executable=shutil.which('chromium') or shutil.which('google-chrome')
            browser=p.chromium.launch(headless=True,**({'executable_path':executable} if executable else {}))
            try:
                for width,height in ((1100,900),(390,844)):
                    context=browser.new_context(viewport={'width':width,'height':height},accept_downloads=True)
                    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                    page.goto((root/'editor'/'annotate.html').as_uri());page.wait_for_function("document.getElementById('status').textContent.includes('0 draft boxes')")
                    page.select_option('#class','quadrilateral');canvas=page.locator('#canvas');canvas.scroll_into_view_if_needed();box=canvas.bounding_box()
                    x1=box['x']+1+.1*(box['width']-2);y1=box['y']+1+.2*(box['height']-2)
                    x2=box['x']+1+.6*(box['width']-2);y2=box['y']+1+.7*(box['height']-2)
                    page.mouse.move(x1,y1);page.mouse.down();page.mouse.move(x2,y2,steps=5);page.mouse.up()
                    with page.expect_download() as downloaded:page.click('#download')
                    draft=json.loads(Path(downloaded.value.path()).read_text());checked=validate_draft(draft,data,digest)
                    assert checked['instances']==1,draft
                    actual=draft['images'][0]['instances'][0]['box'];expected=[50,60,300,210];error=max(abs(a-b) for a,b in zip(actual,expected))
                    assert error<=2,(actual,box);assert draft['images'][0]['instances'][0]['class']=='quadrilateral'
                    overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
                    assert not overflow,(width,'horizontal overflow')
                    if screenshots:
                        folder=Path(screenshots);folder.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(folder/f'editor-{width}.png'),full_page=True)
                    page.click('#undo')
                    with page.expect_download() as undo_download:page.click('#download')
                    undo=json.loads(Path(undo_download.value.path()).read_text());assert validate_draft(undo,data,digest)['instances']==0
                    assert not errors,errors
                    rows.append({'viewport':[width,height],'source_box':actual,'maximum_coordinate_error_pixels':error,
                                 'downloaded_boxes':checked['instances'],'undo_boxes':0,'unscored':checked['unscored'],'horizontal_overflow':overflow,'page_errors':errors})
                    context.close()
                version=browser.version
            finally:browser.close()
    return {'format':'seye-annotation-browser-verification-v1','browser_version':version,'generated_source_size':[500,300],
            'cases':rows,'independent_human_usability_validated':False,'passed':len(rows)==2}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--screenshots');args=parser.parse_args()
    result=run(args.screenshots);Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
