"""Fixed statistical tool registry: no generated Python is evaluated."""
from __future__ import annotations
from typing import Any, Callable
import numpy as np
from scipy import stats

def _clean(values:list[Any],minimum:int=2)->np.ndarray:
    array=np.asarray([v for v in values if v is not None],dtype=float)
    if len(array)<minimum: raise ValueError(f"At least {minimum} non-missing observations required")
    return array

def proportion_confidence_interval(successes:int,n:int,confidence:float=.95)->dict[str,Any]:
    if n<=0 or not 0<=successes<=n: raise ValueError("successes must be within a positive n")
    p=successes/n; z=stats.norm.ppf(1-(1-confidence)/2); d=1+z*z/n; center=(p+z*z/(2*n))/d; half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return {"tool":"proportion_confidence_interval","estimate":p,"confidence_interval":[center-half,center+half],"n":n,"assumptions":["Binomial observations","Wilson interval"],"warnings":[]}
def chi_square(table:list[list[int]])->dict[str,Any]:
    a=np.asarray(table); 
    if a.ndim!=2 or np.any(a<0) or a.sum()<10: raise ValueError("A nonnegative 2D table with total n >= 10 is required")
    statistic,p,dof,expected=stats.chi2_contingency(a); warnings=["Some expected cells are below 5; consider Fisher exact."] if np.any(expected<5) else []
    return {"tool":"chi_square","statistic":statistic,"p_value":p,"degrees_of_freedom":dof,"effect_size":float(np.sqrt(statistic/(a.sum()*max(1,min(a.shape)-1)))),"n":int(a.sum()),"warnings":warnings}
def fisher_exact(table:list[list[int]])->dict[str,Any]:
    a=np.asarray(table); 
    if a.shape!=(2,2): raise ValueError("Fisher exact requires a 2x2 table")
    odds,p=stats.fisher_exact(a); return {"tool":"fisher_exact","odds_ratio":odds,"p_value":p,"n":int(a.sum()),"warnings":[]}
def independent_t_test(group_a:list[Any],group_b:list[Any])->dict[str,Any]:
    a,b=_clean(group_a),_clean(group_b); statistic,p=stats.ttest_ind(a,b,equal_var=False); pooled=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); effect=(a.mean()-b.mean())/pooled if pooled else 0
    return {"tool":"independent_t_test","statistic":statistic,"p_value":p,"effect_size":effect,"n":len(a)+len(b),"warnings":["Welch test assumes independent observations and approximately normal group means."]}
def mann_whitney(group_a:list[Any],group_b:list[Any])->dict[str,Any]:
    a,b=_clean(group_a),_clean(group_b); statistic,p=stats.mannwhitneyu(a,b,alternative="two-sided"); return {"tool":"mann_whitney_u","statistic":statistic,"p_value":p,"n":len(a)+len(b),"warnings":["Tests distributional shift, not strictly medians."]}
def one_way_anova(groups:list[list[Any]])->dict[str,Any]:
    clean=[_clean(g) for g in groups]; statistic,p=stats.f_oneway(*clean); return {"tool":"one_way_anova","statistic":statistic,"p_value":p,"n":sum(map(len,clean)),"warnings":["Assumes independent, approximately normal, homoscedastic residuals."]}
def correlation(x:list[Any],y:list[Any],method:str="pearson")->dict[str,Any]:
    a,b=_clean(x,3),_clean(y,3)
    if len(a)!=len(b): raise ValueError("Paired vectors must have equal length")
    result=stats.spearmanr(a,b) if method=="spearman" else stats.pearsonr(a,b)
    return {"tool":f"{method}_correlation","statistic":float(result.statistic),"p_value":float(result.pvalue),"n":len(a),"warnings":[]}
TOOLS:dict[str,Callable[...,dict[str,Any]]]={"proportion_confidence_interval":proportion_confidence_interval,"chi_square":chi_square,"fisher_exact":fisher_exact,"independent_t_test":independent_t_test,"mann_whitney_u":mann_whitney,"one_way_anova":one_way_anova,"pearson_correlation":lambda x,y:correlation(x,y,"pearson"),"spearman_correlation":lambda x,y:correlation(x,y,"spearman")}
def run_statistical_tool(name:str,**kwargs:Any)->dict[str,Any]:
    if name not in TOOLS: raise ValueError(f"Unapproved statistical tool: {name}")
    return TOOLS[name](**kwargs)
