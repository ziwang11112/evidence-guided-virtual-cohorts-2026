"""Weight-only post-acquisition parser audit; no DXA/component outcome access.

Reads XPT header metadata, then seeks directly to WTMEC2YR bytes. The independent
reader is pyreadstat with usecols=['WTMEC2YR']. Output contains aggregate checks
and parser provenance only, never participant rows, keys or weight values.
"""
from pathlib import Path
import hashlib
import inspect
import json
import math
import struct
import sys

import numpy as np
import pandas as pd
from pandas.io.sas.sas_xport import _parse_float_vec
import pyreadstat


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def ibm_double(raw):
    """SAS XPORT IBM float: sign * fraction * 16**(exponent-64)."""
    raw=raw.ljust(8,b'\0')
    if raw[1:]==b'\0'*7 and raw[0] in [0x2e,0x5f,*range(0x41,0x5b)]:
        return float('nan')
    sign=-1 if raw[0]&128 else 1
    mantissa=int.from_bytes(raw[1:],'big')
    return math.ldexp(sign*mantissa,4*((raw[0]&127)-64)-56)


def weight_bytes(path):
    with path.open('rb') as stream:
        headers=[stream.read(80) for _ in range(8)]
        assert headers[0].startswith(b'HEADER RECORD*******LIBRARY HEADER')
        assert headers[7].startswith(b'HEADER RECORD*******NAMESTR HEADER')
        descriptor_length=int(headers[3][-5:-2])
        number_fields=int(headers[7][54:58])
        metadata_length=((descriptor_length*number_fields+79)//80)*80
        metadata=stream.read(metadata_length)
        record_length=0; selected=None
        for k in range(number_fields):
            block=metadata[k*descriptor_length:(k+1)*descriptor_length].ljust(140,b'\0')
            fields=struct.unpack('>hhhh8s40s8shhh2s8shhl52s',block)
            ntype,width,name,position=fields[0],fields[2],fields[4].strip().decode('ascii'),fields[14]
            record_length=max(record_length,position+width)
            if name=='WTMEC2YR':selected=(ntype,width,position)
        assert stream.read(80).startswith(b'HEADER RECORD*******OBS')
        data_start=stream.tell()
        assert selected and selected[0]==1 and selected[1]==8
        assert record_length>80
        data_size=path.stat().st_size-data_start
        n=data_size//record_length
        assert 0<=data_size-n*record_length<80
        raw=[]
        for i in range(n):
            stream.seek(data_start+i*record_length+selected[2])
            raw.append(stream.read(selected[1]))
    return raw,dict(data_start=data_start,record_length=record_length,
                    weight_field_offset=selected[2],weight_field_width=selected[1])


def main():
    directory=Path(__file__).resolve().parent
    rawpath=directory.parent/'custodian/acquisition/private/raw/DEMO_J.xpt'
    raw,layout=weight_bytes(rawpath)
    manual=np.array([ibm_double(x) for x in raw])
    independent,_=pyreadstat.read_xport(rawpath,usecols=['WTMEC2YR'],output_format='dict')
    readstat=np.asarray(independent['WTMEC2YR'],float)
    pandas_values=_parse_float_vec(np.frombuffer(b''.join(raw),dtype='S8'))
    exact_zero=np.array([x==b'\0'*8 for x in raw])
    changed=pandas_values!=manual
    checks={
        'known_positive_one':ibm_double(bytes.fromhex('4110000000000000'))==1,
        'known_negative_one':ibm_double(bytes.fromhex('c110000000000000'))==-1,
        'known_positive_zero':ibm_double(b'\0'*8)==0,
        'known_negative_zero':ibm_double(bytes.fromhex('8000000000000000'))==0,
        'sas_missing_preserved':math.isnan(ibm_double(bytes.fromhex('2e00000000000000'))),
        'same_row_count':len(readstat)==len(raw),
        'manual_equals_readstat_every_weight':np.array_equal(manual,readstat,equal_nan=True),
        'all_manual_zeros_are_exact_all_zero_bytes':np.array_equal(manual==0,exact_zero),
        'pandas_disagreements_exactly_all_zero_bytes':np.array_equal(changed,exact_zero),
        'pandas_zero_error_equals_two_to_minus260':np.all(pandas_values[exact_zero]==2.0**-260),
        'all_nonzero_values_unchanged':np.array_equal(pandas_values[~exact_zero],manual[~exact_zero],equal_nan=True),
        'no_missing_weight':not np.isnan(manual).any(),
        'no_negative_weight':not (manual<0).any(),
    }
    checks={name:bool(value) for name,value in checks.items()}
    assert all(checks.values()),checks
    result=dict(status='confirmed_parser_defect',scope='DEMO_J.WTMEC2YR only; no DXA data or outcome analysis',
        input_sha256=digest(rawpath),layout=layout,
        parsers=dict(python=sys.version.split()[0],pandas=pd.__version__,pyreadstat=pyreadstat.__version__,
            pandas_function_source_sha256=hashlib.sha256(inspect.getsource(_parse_float_vec).encode()).hexdigest()),
        counts=dict(total_weights=len(raw),exact_zero_bytes=int(exact_zero.sum()),
            independently_decoded_zero=int((manual==0).sum()),independently_decoded_positive=int((manual>0).sum()),
            pandas_decoded_positive=int((pandas_values>0).sum()),disagreements=int(changed.sum())),
        exact_zero_pandas_value=float(2.0**-260),checks=checks,
        proposed_repair='Use the independently verified pyreadstat reader; preserve frozen filtering rules and original acquisition. No numerical threshold or outcome-dependent correction.')
    (directory/'weight_decode_review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
