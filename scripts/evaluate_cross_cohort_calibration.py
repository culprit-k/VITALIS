#!/usr/bin/env python3
"""Descriptive calibration audit: train on Challenge 2019 set A, evaluate on set B.

No recalibration or threshold tuning is performed on set B. Calibration statistics
are descriptive only. Inputs are local caches; output contains aggregate metrics only.
"""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = ["HR","O2Sat","Temp","SBP","MAP","DBP","Resp","EtCO2","BaseExcess","HCO3","FiO2","pH","PaCO2","SaO2","AST","BUN","Alkalinephos","Calcium","Chloride","Creatinine","Bilirubin_direct","Glucose","Lactate","Magnesium","Phosphate","Potassium","Bilirubin_total","TroponinI","Hct","Hgb","PTT","WBC","Fibrinogen","Platelets","Age","Gender","Unit1","Unit2","HospAdmTime","ICULOS"]

def calibration(y, p, bins=10):
    y=np.asarray(y,dtype=np.int8); p=np.asarray(p,dtype=np.float64)
    pc=np.clip(p,1e-6,1-1e-6); z=np.log(pc/(1-pc))
    fit=LogisticRegression(C=1e6,solver="lbfgs",max_iter=1000).fit(z.reshape(-1,1),y)
    order=np.argsort(p,kind="mergesort")
    chunks=np.array_split(order,min(bins,len(order)))
    rel=[{"rows":int(len(ix)),"mean_predicted":float(np.mean(p[ix])),"observed_prevalence":float(np.mean(y[ix]))} for ix in chunks if len(ix)]
    return {"rows":int(len(y)),"positive_label_rows":int(y.sum()),"prevalence":float(y.mean()),
      "mean_predicted_probability":float(p.mean()),"brier_score":float(brier_score_loss(y,p)),
      "log_loss":float(log_loss(y,pc,labels=[0,1])),
      "calibration_intercept_descriptive":float(fit.intercept_[0]),
      "calibration_slope_descriptive":float(fit.coef_[0,0]),
      "reliability_bins_equal_frequency":rel}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--set-a-cache",type=Path,required=True); ap.add_argument("--set-b-cache",type=Path,required=True)
    ap.add_argument("--seeds",type=int,nargs="+",default=[42,123,2026]); ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--predict-chunk-rows",type=int,default=50000); a=ap.parse_args()
    ma=json.loads((a.set_a_cache/"meta.json").read_text()); mb=json.loads((a.set_b_cache/"meta.json").read_text())
    if ma["columns"]!=mb["columns"]: ap.error("Feature schemas differ")
    Xa=np.load(a.set_a_cache/"X.npy",mmap_mode="r"); ya=np.load(a.set_a_cache/"y.npy",mmap_mode="r"); ga=np.load(a.set_a_cache/"g.npy",mmap_mode="r")
    Xb=np.load(a.set_b_cache/"X.npy",mmap_mode="r"); yb=np.load(a.set_b_cache/"y.npy",mmap_mode="r"); gb=np.load(a.set_b_cache/"g.npy",mmap_mode="r")
    for X,y,g,m,n in ((Xa,ya,ga,ma,"A"),(Xb,yb,gb,mb,"B")):
        if X.shape[0]!=m["row_count"] or len(y)!=len(X) or len(g)!=len(X) or len(np.unique(g))!=m["patient_count"]: ap.error(f"Set {n} cache integrity check failed")
    if (ma["patient_count"],mb["patient_count"],int(ya.sum()),int(yb.sum()))!=(20336,20000,17136,10780): ap.error("Unexpected Challenge cohort totals")
    col={v:i for i,v in enumerate(ma["columns"])}; features=[("static",np.array([col[x] for x in BASE])),("temporal",np.arange(Xa.shape[1]))]
    runs=[]
    for seed in a.seeds:
        tr,unused=next(GroupShuffleSplit(n_splits=1,test_size=.4,random_state=seed).split(np.zeros(len(ya)),ya,ga))
        if set(ga[tr]) & set(ga[unused]): raise RuntimeError("Patient overlap in set A split")
        run={"seed":seed,"train_patients":int(len(np.unique(ga[tr]))),"unused_set_a_patients":int(len(np.unique(ga[unused]))),"test_patients_set_b":int(mb["patient_count"]),"models":{}}
        for name,ix in features:
            model=make_pipeline(SimpleImputer(strategy="median",add_indicator=True),StandardScaler(),LogisticRegression(max_iter=150,tol=1e-3,class_weight="balanced",solver="lbfgs",random_state=seed))
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter("always"); model.fit(Xa[np.ix_(tr,ix)],ya[tr])
            p=np.empty(len(yb),dtype=np.float64)
            for start in range(0,len(yb),a.predict_chunk_rows):
                end=min(start+a.predict_chunk_rows,len(yb)); p[start:end]=model.predict_proba(Xb[start:end,ix])[:,1]
            run["models"][name]={"warnings":[str(w.message) for w in ws],
              "discrimination":{"auroc":float(roc_auc_score(yb,p)),"auprc":float(average_precision_score(yb,p))},
              "calibration":calibration(yb,p)}
            print(f"seed={seed} model={name} Brier={run['models'][name]['calibration']['brier_score']:.5f}",flush=True)
        runs.append(run)
    metric_names=["auroc","auprc","brier_score","log_loss","calibration_intercept_descriptive","calibration_slope_descriptive","mean_predicted_probability","prevalence"]
    aggregate={}
    for name in ("static","temporal"):
        aggregate[name]={}
        for metric in metric_names:
            vals=[r["models"][name]["discrimination"][metric] if metric in ("auroc","auprc") else r["models"][name]["calibration"][metric] for r in runs]
            aggregate[name][metric]={"mean":float(np.mean(vals)),"sample_sd_across_seeds":float(np.std(vals,ddof=1)) if len(vals)>1 else None,"by_seed":{str(r["seed"]):v for r,v in zip(runs,vals)}}
    prevalence=float(np.mean(yb))
    result={"project":"VITALIS","run_type":"descriptive_cross_cohort_calibration_train_A_test_B",
      "dataset":{"training_setA":{"patients":ma["patient_count"],"rows":ma["row_count"],"positive_hourly_labels":int(ya.sum())},"training_setB":{"patients":mb["patient_count"],"rows":mb["row_count"],"positive_hourly_labels":int(yb.sum())}},
      "protocol":{"seeds":a.seeds,"split_unit":"patient","set_a_train_fraction":.6,"set_b_test":"all patients","calibration_on_set_b":"descriptive only; no recalibration or threshold selection","reliability_bins":"equal-frequency","patient_level_predictions_exported":False},
      "runs":runs,"aggregate_metrics":aggregate,
      "descriptive_constant_prevalence_reference":{"prevalence":prevalence,"brier_score":prevalence*(1-prevalence),"log_loss":float(log_loss(yb,np.full(len(yb),prevalence),labels=[0,1])),"note":"Uses test prevalence only as a scale reference; not a deployable model."},
      "limitations":["Set B calibration results are descriptive; do not tune calibration or thresholds on this test cohort.","Both cohorts are from the same benchmark, not prospective clinical validation.","Hourly challenge-label metrics are not patient-level event sensitivity, lead time, or clinical false-alarm rates.","No row-level predictions, identifiers, or raw records are written."]}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+"\n"); print("Wrote aggregate-only output",a.output)
if __name__=="__main__": main()
