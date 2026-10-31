"""Invented arithmetic only. Expected values use stdlib/Fraction, not checker helpers/tests."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import csv
import hashlib
import json
import math
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cohort_harness.self_consistency import run_self_consistency


def exact_summary(values):
    if not values:
        return None
    xs = list(map(F, values))
    n = len(xs)
    mean = sum(xs) / n
    ordered = sorted(xs)
    quantiles = {}
    for q in [F(0), F(1,100), F(5,100), F(1,2), F(95,100), F(99,100), F(1)]:
        location = (n - 1) * q
        lo = location.numerator // location.denominator
        hi = min(lo + 1, n - 1)
        quantiles[str(float(q))] = float(ordered[lo] + (location - lo) * (ordered[hi] - ordered[lo]))
    return {"n": n, "mean": float(mean),
            "sample_sd": math.sqrt(float(sum((x-mean)**2 for x in xs)/(n-1))) if n>1 else None,
            "rmse_from_zero": math.sqrt(float(sum(x*x for x in xs)/n)), "quantiles": quantiles}


def average_ranks(values):
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    result = [None] * len(values)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[ordered[end]] == values[ordered[start]]:
            end += 1
        for position in range(start, end):
            result[ordered[position]] = F(start + 1 + end, 2)
        start = end
    return result


def correlation(a, b):
    a, b = list(map(F, a)), list(map(F, b))
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    numerator = sum((x-ma)*(y-mb) for x,y in zip(a,b))
    denominator = math.sqrt(float(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b)))
    return float(numerator)/denominator if denominator else None


def rational_rank(matrix):
    a = [list(map(F, row)) for row in matrix]
    pivot_row = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(pivot_row,len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[pivot_row],a[pivot] = a[pivot],a[pivot_row]
        value = a[pivot_row][column]
        a[pivot_row] = [x/value for x in a[pivot_row]]
        for i in range(len(a)):
            if i != pivot_row:
                value = a[i][column]
                a[i] = [x-value*y for x,y in zip(a[i],a[pivot_row])]
        pivot_row += 1
    return pivot_row


def main():
    def col(name, kind, role, **extra):
        return {"name":name,"kind":kind,"role":role,"unit":"invented","nullable":False,**extra}
    task={"schema_version":1,"task_id":"independent-arithmetic-only","mode":"enrichment",
          "population":"Invented software fixture; no scientific or target rows","row_id":"key","n_rows":6,
          "columns":[col("key","string","identifier"),col("x","number","observed"),
                     col("w","number","observed"),col("constant","number","observed"),
                     col("g","category","observed",categories=["A","B","C"]),
                     col("h","category","observed",categories=["U","V"]),col("y","number","generated")],
          "information_policy":{"mode":"prior_only","excluded_cohorts":[],"allowed_tools":[]},
          "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    def lookup(name,pairs):
        return {"lookup":{"column":name,"values":[{"key":k,"value":v} for k,v in pairs]}}
    def add(a,b):return {"op":"add","args":[a,b]}
    spec={"schema_version":1,"interpretation":"working_guides","outcome":"y",
          "numeric_predictors":["x","w","constant"],"group_by":["g","h"],
          "conditional_mean":add(add({"const":5},{"op":"mul","args":[{"const":2},{"column":"x"}]}),
             add(lookup("g",[("A",-1),("B",2),("C",0)]),lookup("h",[("U",0),("V",1)]))),
          "conditional_sd":lookup("h",[("U",2),("V",1)])}
    x=[0,1,1,2,3,3]; w=[1,3,3,5,7,7]; g=["A","A","B","B","A","B"]; h=["U","V","U","V","U","V"]
    # Independently fixed vectors, not obtained from the expression evaluator.
    locations=[4,7,9,12,10,14]; y=[2,7,11,10,10,17]
    residual=[F(a-b) for a,b in zip(y,locations)]
    scales=[2,1,2,1,2,1]; z=[a/F(b) for a,b in zip(residual,scales)]
    checks=[]
    def close(actual,expected,label):
        assert actual is None if expected is None else math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12), label
        checks.append(label)
    def compare_summary(actual,values,label):
        expected=exact_summary(values)
        assert actual['n']==len(values),label
        if expected is None:
            assert actual['status']=='empty_group' and actual['mean'] is None,label
            checks.append(label+'.empty');return
        for key in ['mean','sample_sd','rmse_from_zero']:
            close(actual[key],expected[key],label+'.'+key)
        for key,value in expected['quantiles'].items():close(actual['quantiles'][key],value,label+'.q'+key)
    with tempfile.TemporaryDirectory(prefix='m16-invented-independent-') as temp:
        folder=Path(temp)
        for name,obj in [('task',task),('spec',spec)]:
            (folder/(name+'.json')).write_text(json.dumps(obj),encoding='utf-8')
        rows=[[f'invented{i}',f'{x[i]:.2f}',str(w[i]),'7',g[i],h[i]] for i in range(6)]
        for name,header,values in [('observed',['key','x','w','constant','g','h'],rows),
                                  ('generated',['key','x','w','constant','g','h','y'],[row+[str(y[i])] for i,row in enumerate(rows)])]:
            with (folder/(name+'.csv')).open('w',encoding='utf-8',newline='') as stream:
                writer=csv.writer(stream);writer.writerow(header);writer.writerows(values)
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
        result=run_self_consistency(*(folder/name for name in ['task.json','observed.csv','generated.csv','spec.json','result.json']))
        d=result['diagnostics']
        vectors={'outcome':y,'conditional_mean_or_location_guide':locations,'residual':residual,
                 'conditional_sd_or_scale_guide':scales,'standardized_residual':z}
        for name,values in vectors.items():compare_summary(d['overall'][name],values,'overall.'+name)
        for name,group_values in [('g',g),('h',h)]:
            for entry in d['groups'][name]:
                indices=[i for i,v in enumerate(group_values) if v==entry['category']]
                for vector,values in vectors.items():compare_summary(entry['summaries'][vector],[values[i] for i in indices],name+entry['category']+'.'+vector)
        joint=d['joint_groups'];assert (joint['declared_group_count'],joint['observed_group_count'],joint['empty_group_count'])==(6,4,2)
        assert [entry['categories'] for entry in joint['groups']]==[{'g':a,'h':b} for a,b in product(['A','B','C'],['U','V'])]
        for entry in joint['groups']:
            indices=[i for i in range(6) if g[i]==entry['categories']['g'] and h[i]==entry['categories']['h']]
            for vector,values in vectors.items():compare_summary(entry['summaries'][vector],[values[i] for i in indices],str(entry['categories'])+'.'+vector)
        for residual_name,values in [('residual_predictor_associations',residual),('standardized_residual_predictor_associations',z)]:
            for predictor,pvalues in [('x',x),('w',w),('constant',[7]*6)]:
                actual=d[residual_name][predictor]
                close(actual['pearson']['value'],correlation(values,pvalues),residual_name+predictor+'.Pearson')
                close(actual['spearman_average_ranks']['value'],correlation(average_ranks(values),average_ranks(pvalues)),residual_name+predictor+'.Spearman')
        expected_rank=rational_rank([[1,x[i],w[i],7] for i in range(6)])
        assert d['predictor_design']['rank']==expected_rank==2
        assert d['predictor_design']['status']=='rank_deficient' and d['predictor_design']['constant_predictors']==['constant']
        assert d['absolute_standardized_tail_counts']=={str(k):sum(abs(v)>k for v in z) for k in (1,2,3)}
        assert d['duplicate_outcome_values']=={'unique_count':5,'repeated_value_count':1,'extra_occurrence_count':1,'largest_multiplicity':2}
        assert result['status']=='computed' and result['scientific_validity']=='not_assessed' and d['overall']['residual']['mean']!=0
        assert all(hashlib.sha256((folder/name).read_bytes()).hexdigest()==value for name,value in before.items())
        report={'status':'PASS','arithmetic_comparisons':len(checks),'scope':'Invented independent fixture only; no biomedical target or source rows',
                'expected_values_method':'stdlib Fraction, direct formulas, independent average tied ranks, exact Gaussian elimination; no imported test fixtures or checker helpers',
                'engine_sha256':hashlib.sha256((ROOT/'cohort_harness/self_consistency.py').read_bytes()).hexdigest(),
                'test_file_sha256':hashlib.sha256((ROOT/'tests/test_self_consistency.py').read_bytes()).hexdigest(),
                'docs_sha256':hashlib.sha256((ROOT/'docs/SELF_CONSISTENCY.md').read_bytes()).hexdigest(),
                'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'residual_mean':float(sum(residual)/6),'residual_sample_sd':exact_summary(residual)['sample_sd'],
                'rank':expected_rank,'joint_counts':{'declared':6,'observed':4,'empty':2},
                'input_hashes_preserved':True,'no_scientific_equality_threshold':True,'checks':checks}
        with Path(__file__).with_name('INDEPENDENT_SELF_CHECK.json').open('x',encoding='utf-8') as stream:
            json.dump(report,stream,indent=2);stream.write('\n')
        print(json.dumps({k:v for k,v in report.items() if k!='checks'}))


if __name__=='__main__':main()
