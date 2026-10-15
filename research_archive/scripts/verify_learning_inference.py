"""Independent regression algebra check and one motivated composition sensitivity.
Uses the audited reconstruction; does not independently reconstruct raw tests.
The sensitivity is fixed to treatment interactions with the three original child
baseline controls, to assess whether teacher-score moderation may reflect pupils.
"""
from pathlib import Path
import importlib.util
import hashlib
import json
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/audit_learning_extension.py'
spec=importlib.util.spec_from_file_location('audit_learn',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
_,mid=m.prepare_midline();_,post=m.prepare_postline()
post,_=m.add_teacher_score(post);scores=m.score_reference(mid,post)
post['teacher_score_z']=(post.teacher_score-scores.teacher_score.mean())/scores.teacher_score.std(ddof=1)
post['treat_score_z']=post.treat*post.teacher_score_z
controls=['pre_total_v','pre_total_w','pre_writ']
base=['treat','teacher_score_z','treat_score_z']+controls
for c in controls: post['treat_'+c]=post.treat*post[c]
rows=[]
for model,cols in [('independent_main',base),('pupil_composition_sensitivity',base+['treat_'+c for c in controls])]:
 d=post.dropna(subset=cols+['z_add_post_total','schid']).copy()
 y=d.z_add_post_total.to_numpy(float);x=np.column_stack([np.ones(len(d)),d[cols].to_numpy(float)])
 b=np.linalg.lstsq(x,y,rcond=None)[0];u=y-x@b;g=pd.Categorical(d.schid).codes;G=len(np.unique(g));N,K=x.shape
 cluster_scores=np.zeros((G,K));np.add.at(cluster_scores,g,x*u[:,None])
 bread=np.linalg.pinv(x.T@x)
 cov=bread@(cluster_scores.T@cluster_scores)@bread*G/(G-1)*(N-1)/(N-K)
 j=3;se=np.sqrt(cov[j,j]);crit=stats.t.ppf(.975,G-1)
 rows.append(dict(model=model,n=N,schools=G,interaction=float(b[j]),se=float(se),p=float(2*stats.t.sf(abs(b[j]/se),G-1)),ci_low=float(b[j]-crit*se),ci_high=float(b[j]+crit*se)))
result=pd.DataFrame(rows)
expected=pd.read_csv(ROOT/'outputs/research_direction_audit/learning_model_results.csv')
r=expected[(expected.stage=='post')&(expected.model=='moderator_table9A_controls')&(expected.term=='treat_score_z')].iloc[0]
assert abs(rows[0]['interaction']-r.coefficient)<1e-8
assert abs(rows[0]['se']-r.se_clustered)<1e-8
out=ROOT/'outputs/research_direction_audit'
result.to_csv(out/'learning_independent_check_and_sensitivity.csv',index=False)
(out/'learning_independent_inference_check.json').write_text(json.dumps({'scope':'Independent NumPy least-squares and grouped-score covariance on audited reconstructed data; not independent raw-data reconstruction','input_script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'matched_main_coefficient_and_se':True,'sensitivity':'Treatment interacted with each original child baseline control; same sample','results':rows},indent=2))
print(result.to_string(index=False))
