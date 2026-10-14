#!/usr/bin/env python3
"""Cross-cohort VITALIS evaluation: train on Challenge 2019 set A, test on set B.

Input caches are local derived data. Only aggregate metrics are written to output.
"""
from __future__ import annotations
import argparse, json, time, warnings
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = ["HR","O2Sat","Temp","SBP","MAP","DBP","Resp","EtCO2","BaseExcess","HCO3","FiO2","pH","PaCO2","SaO2","AST","BUN","Alkalinephos","Calcium","Chloride","Creatinine","Bilirubin_direct","Glucose","Lactate","Magnesium","Phosphate","Potassium","Bilirubin_total","TroponinI","Hct","Hgb","PTT","WBC","Fibrinogen","Platelets","Age","Gender","Unit1","Unit2","HospAdmTime","ICULOS"]

def metrics(y, p):
    pred = p >= 0.5
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {"rows": int(len(y)), "positive_label_rows": int(y.sum()), "prevalence": float(np.mean(y)), "threshold": 0.5,
            "auroc": float(roc_auc_score(y,p)), "auprc": float(average_precision_score(y,p)),
            "brier_score": float(brier_score_loss(y,p)), "sensitivity": float(tp/(tp+fn)) if tp+fn else None,
            "specificity": float(tn/(tn+fp)) if tn+fp else None, "ppv": float(tp/(tp+fp)) if tp+fp else None,
            "npv": float(tn/(tn+fn)) if tn+fn else None,
            "confusion_matrix": {"tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp)}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--set-a-cache',type=Path,required=True)
    ap.add_argument('--set-b-cache',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[42,123,2026])
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--predict-chunk-rows',type=int,default=50000)
    args=ap.parse_args()
    ma=json.loads((args.set_a_cache/'meta.json').read_text()); mb=json.loads((args.set_b_cache/'meta.json').read_text())
    if ma['columns'] != mb['columns']: ap.error('Set A and set B feature schemas differ')
    Xa=np.load(args.set_a_cache/'X.npy',mmap_mode='r'); ya=np.load(args.set_a_cache/'y.npy',mmap_mode='r'); ga=np.load(args.set_a_cache/'g.npy',mmap_mode='r')
    Xb=np.load(args.set_b_cache/'X.npy',mmap_mode='r'); yb=np.load(args.set_b_cache/'y.npy',mmap_mode='r'); gb=np.load(args.set_b_cache/'g.npy',mmap_mode='r')
    for X,y,g,m,label in [(Xa,ya,ga,ma,'A'),(Xb,yb,gb,mb,'B')]:
        if X.shape[0]!=m['row_count'] or len(y)!=len(X) or len(g)!=len(X) or len(np.unique(g))!=m['patient_count']:
            ap.error(f'Set {label} cache integrity check failed')
    if ma['patient_count']!=20336 or mb['patient_count']!=20000: ap.error('Expected official Challenge 2019 set A (20,336 patients) and set B (20,000 patients)')
    if int(ya.sum())!=17136 or int(yb.sum())!=10780: ap.error('Challenge-label totals do not match the expected source cohorts')
    ci={c:i for i,c in enumerate(ma['columns'])}; sidx=np.array([ci[c] for c in BASE]); feature_sets=[('static',sidx),('temporal',np.arange(Xa.shape[1]))]
    runs=[]; started=time.time()
    for seed in args.seeds:
        tr,va=next(GroupShuffleSplit(n_splits=1,test_size=.4,random_state=seed).split(np.zeros(len(ya)),ya,ga))
        if set(ga[tr]) & set(ga[va]): raise RuntimeError('Set A patient leakage between train and holdout')
        sr={'seed':seed,'training_cohort':'training_setA','holdout_cohort':'training_setA (held out, not used for tuning)','test_cohort':'training_setB (entire independent cohort)',
            'patient_counts':{'set_a_train':int(len(np.unique(ga[tr]))),'set_a_holdout_unused':int(len(np.unique(ga[va]))),'set_b_test':int(mb['patient_count'])},
            'row_counts':{'set_a_train':int(len(tr)),'set_a_holdout_unused':int(len(va)),'set_b_test':int(len(yb))},
            'positive_label_rows':{'set_a_train':int(ya[tr].sum()),'set_a_holdout_unused':int(ya[va].sum()),'set_b_test':int(yb.sum())},'models':{}}
        for name,ix in feature_sets:
            model=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),LogisticRegression(max_iter=150,tol=1e-3,class_weight='balanced',solver='lbfgs',random_state=seed))
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('always'); t=time.time(); model.fit(Xa[np.ix_(tr,ix)],ya[tr]); fit_sec=time.time()-t
            probs=np.empty(len(yb),dtype=np.float64)
            for start in range(0,len(yb),args.predict_chunk_rows):
                end=min(start+args.predict_chunk_rows,len(yb))
                probs[start:end]=model.predict_proba(Xb[start:end,ix])[:,1]
            m=metrics(yb,probs)
            sr['models'][name]={'fit_seconds':round(fit_sec,3),'warnings':[str(w.message) for w in ws],'test_metrics':m}
            print(f"seed={seed} {name} setB AUROC={m['auroc']:.4f} AUPRC={m['auprc']:.4f} Brier={m['brier_score']:.4f}",flush=True)
            del model, probs
        runs.append(sr)
    aggregate={}
    for name in ('static','temporal'):
        aggregate[name]={}
        for metric in ('auroc','auprc','brier_score','sensitivity','specificity','ppv','npv'):
            vals=[r['models'][name]['test_metrics'][metric] for r in runs]
            aggregate[name][metric]={'mean':float(np.mean(vals)),'sample_sd_across_seeds':float(np.std(vals,ddof=1)) if len(vals)>1 else None,'by_seed':{str(r['seed']):r['models'][name]['test_metrics'][metric] for r in runs}}
    result={'project':'VITALIS','run_type':'cross_cohort_train_A_test_B','dataset':{'training_setA':{'patients':ma['patient_count'],'hourly_rows':ma['row_count'],'positive_hourly_labels':int(ya.sum())},'training_setB':{'patients':mb['patient_count'],'hourly_rows':mb['row_count'],'positive_hourly_labels':int(yb.sum())}},
        'protocol':{'seeds':args.seeds,'split_unit':'patient','set_a_train_fraction':0.6,'set_a_holdout_fraction':0.4,'set_b_test':'all patients in training_setB','feature_sets':['static baseline fields','temporal lag/delta/trailing-six-row features'],'model':'median imputation with missingness indicators, standard scaling, balanced logistic regression (max_iter=150, tol=1e-3)','threshold':0.5,'threshold_note':'fixed research comparison only; not clinically selected','sd_note':'Across A training subsamples, not a confidence interval','test_predictions_exported':False},
        'runs':runs,'aggregate_metrics':aggregate,'elapsed_seconds':round(time.time()-started,3),'limitations':['Retrospective evaluation on the official Challenge 2019 training cohorts; set B is a separate cohort but not external prospective clinical validation','Hourly challenge-label metrics are not patient-level event sensitivity, lead time, or real-world clinical false-alarm rates','A patient-level 60/40 training/unused-holdout split is used; no calibration or threshold tuning is performed','The fixed 0.5 threshold is not a clinically selected operating point','No patient-level predictions, IDs, or raw patient data are written to output']}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2)+'\n'); print('Wrote aggregate-only output',args.output,flush=True)
if __name__=='__main__': main()
