"""Predeclared causal patient-relative physiology ablation with aggregate-only probability-quality analysis."""
from __future__ import annotations
import argparse, hashlib, json, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from vitalis.features import add_patient_baseline_features
from vitalis.horizon import build_future_challenge_targets, evaluate_horizon_alerts, patient_cluster_bootstrap_horizon_alerts
from vitalis.validation import assert_disjoint_patient_splits

VITALS = ("HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp")
BASE = ("HR","O2Sat","Temp","SBP","MAP","DBP","Resp","EtCO2","BaseExcess","HCO3","FiO2","pH","PaCO2","SaO2","AST","BUN","Alkalinephos","Calcium","Chloride","Creatinine","Bilirubin_direct","Glucose","Lactate","Magnesium","Phosphate","Potassium","Bilirubin_total","TroponinI","Hct","Hgb","PTT","WBC","Fibrinogen","Platelets","Age","Gender","Unit1","Unit2","HospAdmTime","ICULOS")
EXPECTED = {"A": (20336,790215,17136), "B": (20000,761995,10780)}

def load_cache(path, cohort):
    meta=json.loads((path/"meta.json").read_text())
    X=np.load(path/"X.npy",mmap_mode="r"); y=np.load(path/"y.npy",mmap_mode="r"); g=np.load(path/"g.npy",mmap_mode="r")
    actual=(len(np.unique(g)),len(y),int(np.asarray(y).sum()))
    if actual != EXPECTED[cohort]: raise ValueError(f"Set {cohort} audit failed: {actual}")
    if X.shape[0]!=len(y) or len(g)!=len(y) or X.shape[1]!=len(meta["columns"]): raise ValueError("Cache shape/schema mismatch")
    return meta,X,y,g

def personal_z(X,g,columns):
    missing=set(VITALS)-set(columns)
    if missing: raise ValueError(f"Missing vital channels: {sorted(missing)}")
    ix=[columns.index(n) for n in VITALS]
    frame=pd.DataFrame(np.asarray(X[:,ix]),columns=VITALS)
    frame.insert(0,"patient_code",np.asarray(g))
    enriched=add_patient_baseline_features(frame,patient_col="patient_code",value_cols=list(VITALS),min_history=5,min_scale=1e-3)
    out=enriched[[f"{n}_personal_z" for n in VITALS]].to_numpy(dtype=np.float32,copy=True)
    del enriched,frame
    return out

def metric(y,p,threshold):
    pred=p>=threshold; tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {"rows":int(len(y)),"positive_future_label_rows":int(np.sum(y)),"prevalence":float(np.mean(y)),"threshold":threshold,
      "auroc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,"auprc":float(average_precision_score(y,p)),
      "brier_score":float(brier_score_loss(y,p)),"sensitivity":float(tp/(tp+fn)) if tp+fn else None,
      "specificity":float(tn/(tn+fp)) if tn+fp else None,"ppv":float(tp/(tp+fp)) if tp+fp else None,
      "npv":float(tn/(tn+fn)) if tn+fn else None,"confusion_matrix":{"tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp)}}

def paired_brier_cluster_bootstrap(y, p_base, p_candidate, groups, n_bootstrap, seed):
    """Paired Set B Brier difference (candidate - baseline), resampling whole patients."""
    y=np.asarray(y,dtype=np.int8); p_base=np.asarray(p_base,dtype=float)
    p_candidate=np.asarray(p_candidate,dtype=float); groups=np.asarray(groups)
    unique, inverse=np.unique(groups,return_inverse=True)
    sums=np.zeros((len(unique),3),dtype=float)
    np.add.at(sums[:,0],inverse,(p_base-y)**2)
    np.add.at(sums[:,1],inverse,(p_candidate-y)**2)
    np.add.at(sums[:,2],inverse,1.0)
    point=float((sums[:,1].sum()-sums[:,0].sum())/sums[:,2].sum())
    rng=np.random.default_rng(seed)
    draws=rng.integers(0,len(unique),size=(n_bootstrap,len(unique)))
    sampled=sums[draws].sum(axis=1)
    deltas=(sampled[:,1]-sampled[:,0])/sampled[:,2]
    return {"estimand":"Brier(candidate) - Brier(temporal baseline); negative favors candidate",
      "point_estimate":point,"ci_95_percentile":{"lower":float(np.quantile(deltas,.025)),"upper":float(np.quantile(deltas,.975))},
      "bootstrap_replicates":int(n_bootstrap),"bootstrap_unit":"Set B patient cluster","unique_patients":int(len(unique))}

def calibration_summary(y,p):
    """Descriptive calibration only; no recalibration is fitted or applied."""
    from scipy.optimize import minimize
    y=np.asarray(y,dtype=np.int8); p=np.clip(np.asarray(p,dtype=float),1e-7,1-1e-7)
    logit=np.log(p/(1-p))
    lo,hi=-30.0,30.0
    for _ in range(80):
        mid=(lo+hi)/2
        pred=1/(1+np.exp(-np.clip(logit+mid,-40,40)))
        if pred.mean()>y.mean(): hi=mid
        else: lo=mid
    intercept=(lo+hi)/2
    def objective(theta):
        z=np.clip(theta[0]+theta[1]*logit,-40,40)
        return float(np.sum(np.logaddexp(0,z)-y*z))
    fit=minimize(objective,np.array([0.0,1.0]),method="L-BFGS-B",bounds=[(-30,30),(-20,20)])
    return {"calibration_intercept_slope_fixed_1":float(intercept),
      "calibration_intercept_free_slope":float(fit.x[0]),"calibration_slope":float(fit.x[1]),
      "calibration_fit_converged":bool(fit.success),
      "interpretation":"Descriptive Set B diagnostics only; no calibration transformation applied."}

def digest(a):
    a=np.ascontiguousarray(np.asarray(a))
    return hashlib.sha256(a.dtype.str.encode()+str(a.shape).encode()+a.tobytes()).hexdigest()

def run_one(ma,Xa,ya,ga,mb,Xb,yb,gb,horizon,seed,threshold,refractory,boot):
    if ma["columns"]!=mb["columns"]: raise ValueError("Cohort feature schemas differ")
    ta=build_future_challenge_targets(ya,ga,horizon); tb=build_future_challenge_targets(yb,gb,horizon)
    split=GroupShuffleSplit(n_splits=1,test_size=.4,random_state=seed)
    train_pos,unused_pos=next(split.split(np.zeros(len(ta.targets)),ta.targets,ta.patient_ids))
    train_groups=set(ta.patient_ids[train_pos].tolist()); unused_groups=set(ta.patient_ids[unused_pos].tolist())
    assert_disjoint_patient_splits(train_groups,unused_groups,set())
    train_rows=ta.row_indices[train_pos]; train_y=ta.targets[train_pos]; test_rows=tb.row_indices
    if len(np.unique(train_y))<2: raise ValueError(f"One training class at {horizon}h seed {seed}")
    za=personal_z(Xa,ga,ma["columns"]); zb=personal_z(Xb,gb,mb["columns"])
    ix={n:i for i,n in enumerate(ma["columns"])}
    static_ix=np.array([ix[n] for n in BASE if n in ix],dtype=np.int64)
    temporal_ix=np.arange(len(ma["columns"]),dtype=np.int64)
    configs=(("static_baseline",static_ix,False),("temporal_baseline",temporal_ix,False),("temporal_plus_personal_physiology",temporal_ix,True))
    result={"horizon_hours":horizon,"seed":seed,"threshold":threshold,"refractory_hours":refractory,
      "set_a_training_patients":len(train_groups),"set_a_heldout_unused_patients":len(unused_groups),
      "set_b_evaluation_patients":int(len(np.unique(tb.patient_ids))),"set_a_training_rows":int(len(train_rows)),
      "set_b_evaluation_rows":int(len(tb.targets)),"set_b_positive_target_rows":int(tb.targets.sum()),"models":{}}
    predictions={}
    for name,indices,add_z in configs:
        def select(X,rows,z):
            raw=np.asarray(X[np.ix_(rows,indices)],dtype=np.float32)
            return np.concatenate((raw,z[rows]),axis=1) if add_z else raw
        train_X=select(Xa,train_rows,za); test_X=select(Xb,test_rows,zb)
        model=make_pipeline(SimpleImputer(strategy="median",add_indicator=True,keep_empty_features=True),StandardScaler(),
            LogisticRegression(max_iter=300,class_weight="balanced",solver="lbfgs",random_state=seed))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always"); start=time.time()
            with threadpool_limits(limits=1): model.fit(train_X,train_y)
            fit_seconds=time.time()-start
        with threadpool_limits(limits=1): p=model.predict_proba(test_X)[:,1]
        row_metrics=metric(tb.targets,p,threshold)
        predictions[name]=np.asarray(p,dtype=np.float64).copy()
        row_metrics['calibration_diagnostics']=calibration_summary(tb.targets,p)
        alert=evaluate_horizon_alerts(tb.targets,p,tb.patient_ids,tb.patient_time_indices,threshold=threshold,refractory_hours=refractory)
        ci=patient_cluster_bootstrap_horizon_alerts(tb.targets,p,tb.patient_ids,tb.patient_time_indices,threshold=threshold,refractory_hours=refractory,n_bootstrap=boot,seed=seed)
        clf=model[-1]
        result["models"][name]={"feature_count_before_imputation":int(train_X.shape[1]),"fit_seconds":round(fit_seconds,3),
          "fit_warnings":[str(w.message) for w in caught],"set_b_row_metrics":row_metrics,"set_b_patient_alert_metrics":alert,
          "set_b_patient_alert_metrics_cluster_bootstrap_95ci":ci,
          "diagnostics":{"train_row_indices_sha256":digest(train_rows),"train_targets_sha256":digest(train_y),
            "coefficient_sha256":digest(clf.coef_),"intercept_sha256":digest(clf.intercept_),"prediction_sha256":digest(p),
            "converged_within_max_iter":bool(np.all(np.asarray(clf.n_iter_)<clf.max_iter))}}
        print(f"horizon={horizon} seed={seed} model={name} AUROC={row_metrics['auroc']}",flush=True)
        del model,train_X,test_X,p
    result["paired_probability_quality"]={
      "temporal_baseline_vs_candidate_brier":paired_brier_cluster_bootstrap(
        tb.targets,predictions["temporal_baseline"],predictions["temporal_plus_personal_physiology"],
        tb.patient_ids,boot,seed+100000+horizon),
      "note":"Paired patient-cluster uncertainty; Set B is evaluation-only. No calibration or threshold selection on Set B."
    }
    del predictions
    result["candidate_features"]={"channels":list(VITALS),"min_history":5,"scale_floor":1e-3,"uses_prior_rows_only":True}
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--set-a-cache",type=Path,required=True); p.add_argument("--set-b-cache",type=Path,required=True)
    p.add_argument("--horizons",type=int,nargs="+",default=[1,3,6]); p.add_argument("--seeds",type=int,nargs="+",default=[42,123,2026])
    p.add_argument("--threshold",type=float,default=.5); p.add_argument("--refractory-hours",type=int,default=6); p.add_argument("--bootstrap-replicates",type=int,default=200); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); ma,Xa,ya,ga=load_cache(a.set_a_cache,"A"); mb,Xb,yb,gb=load_cache(a.set_b_cache,"B")
    start=time.time(); runs=[]
    for h in a.horizons:
        for seed in a.seeds: runs.append(run_one(ma,Xa,ya,ga,mb,Xb,yb,gb,h,seed,a.threshold,a.refractory_hours,a.bootstrap_replicates))
    out={"project":"VITALIS","experiment":"predeclared causal patient-relative physiology feature ablation","source_label_note":"Challenge SepsisLabel-positive-window entry, not independently observed biological onset.",
      "runtime_seconds":round(time.time()-start,3),"protocol":{"horizons_hours":a.horizons,"seeds":a.seeds,
      "models":["static_baseline","temporal_baseline","temporal_plus_personal_physiology"],"threshold":a.threshold,"refractory_hours":a.refractory_hours,
      "bootstrap_replicates":a.bootstrap_replicates,"Set_B_role":"evaluation only","no_Set_B_fit_or_selection":True},
      "cohorts":{"A":{"patients":len(np.unique(ga)),"rows":len(ya),"positive_labels":int(np.asarray(ya).sum())},
      "B":{"patients":len(np.unique(gb)),"rows":len(yb),"positive_labels":int(np.asarray(yb).sum())}},"runs":runs,
      "limitations":["Exploratory retrospective ablation, not clinical validation.","Set B is another Challenge training cohort, not independent prospective validation.",
      "Candidate is a prior-only personal-deviation feature ablation, not the full streaming adaptive twin.","Calibration intercept/slope are descriptive diagnostics; no Set B calibration is fitted or applied.","Paired Brier intervals quantify uncertainty for candidate-minus-baseline difference, not clinical benefit.","Do not use Set B results to tune/select the model or claim clinical benefit."]}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"runs":len(runs),"runtime_seconds":out["runtime_seconds"],"output":str(a.output)}))
if __name__=="__main__": main()
