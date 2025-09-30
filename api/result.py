# api/result.py - defensive handler (safe import, loads data at runtime)
import os, json, traceback
from urllib.parse import parse_qs

def _make_response(obj, status=200):
    return (json.dumps(obj, ensure_ascii=False), status, {'Content-Type':'application/json'})

def handler(request):
    try:
        if hasattr(request, 'args'):
            params = {k: v for k, v in request.args.items()}
        else:
            qs = request.environ.get('QUERY_STRING','')
            params = {k: v[0] for k, v in parse_qs(qs).items()}

        reg = params.get('reg','').strip()
        branch = params.get('branch','').strip()
        if not reg:
            return _make_response({'error':'reg is required'}, 400)
        if not branch:
            return _make_response({'error':'branch is required'}, 400)

        data_file = os.path.join(os.getcwd(), 'data', f"{branch}.json")
        if not os.path.exists(data_file):
            return _make_response({'error':'Incorrect entries or branch selection. Please try again.'}, 400)

        with open(data_file, 'r', encoding='utf-8') as fh:
            rows = json.load(fh)

        reg_norm = reg.lower()
        normalized = []
        for r in rows:
            r = {str(k): (v if v is not None else '') for k,v in r.items()}
            matched = False
            # prefer Reg-like keys
            for k in r.keys():
                if k.lower() in ('reg','reg. no','registration','regno','registration no'):
                    if isinstance(r[k], str) and r[k].strip().lower() == reg_norm:
                        matched = True
                        break
            if not matched:
                for v in r.values():
                    if isinstance(v, str) and v.strip().lower() == reg_norm:
                        matched = True; break
                if not matched:
                    for v in r.values():
                        if isinstance(v, str) and reg_norm in v.strip().lower():
                            matched = True; break
            if not matched:
                continue

            out = {}
            def find_key(substrs):
                for c in r.keys():
                    lc = c.lower()
                    for s in substrs:
                        if s in lc:
                            return c
                return None

            out['Reg'] = r.get(find_key(['reg','registration']) or next(iter(r.keys())), '')
            out['Name'] = r.get(find_key(['name']) or '', '')
            out['Uni-Roll No'] = r.get(find_key(['uni-roll','uni roll','university roll']) or '', '')
            out['Col Roll No'] = r.get(find_key(['col roll','college roll','section']) or '', '')

            # subject detection
            for k in r.keys():
                lk = k.lower()
                if k in (out.get('Reg'), out.get('Name')): continue
                if any(x in lk for x in ['total','back','result','sgpa','gpa','roll','name']): continue
                if (any(ch.isdigit() for ch in k) and any(ch.isalpha() for ch in k)) or any(x in lk for x in ['fec','4cs','cs','ee','ma']):
                    out[k] = r.get(k, '')

            out['Total Back'] = r.get(find_key(['total back','back','totalback']) or 'Total Back','')
            if not out['Total Back']:
                bc = 0
                for v in out.values():
                    if isinstance(v,str) and (v.strip().upper() == 'F' or 'FAIL' in v.upper()):
                        bc += 1
                out['Total Back'] = str(bc)
            out['Result'] = r.get(find_key(['result','status']) or 'Result','')
            out['SGPA'] = r.get(find_key(['sgpa','gpa','cgpa']) or 'SGPA','')
            normalized.append(out)

        return _make_response({'result': normalized}, 200)
    except Exception as e:
        tb = traceback.format_exc()
        print('ERROR in api/result:', str(e))
        print(tb)
        return _make_response({'error':'Internal server error','detail':str(e)}, 500)
