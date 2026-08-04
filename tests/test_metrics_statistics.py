import pytest
from src.metrics.registry import METRICS
from src.statistics.tools import run_statistical_tool

@pytest.mark.parametrize("name",["30-day readmission rate","mortality rate","complication rate","average length of stay","median length of stay","emergency admission conversion rate","average encounter cost","total encounter cost","encounter volume","diagnosis prevalence"])
def test_metric_registered(name): assert name in METRICS and METRICS[name].minimum_sample_size>=10
def test_proportion_ci():
    r=run_statistical_tool("proportion_confidence_interval",successes=20,n=100); assert r["confidence_interval"][0]<.2<r["confidence_interval"][1]
def test_chi_square(): assert 0<=run_statistical_tool("chi_square",table=[[10,20],[20,10]])["p_value"]<=1
def test_fisher(): assert "odds_ratio" in run_statistical_tool("fisher_exact",table=[[1,9],[8,2]])
def test_ttest(): assert "effect_size" in run_statistical_tool("independent_t_test",group_a=[1,2,3],group_b=[4,5,6])
def test_mann_whitney(): assert "p_value" in run_statistical_tool("mann_whitney_u",group_a=[1,2],group_b=[3,4])
def test_anova(): assert "p_value" in run_statistical_tool("one_way_anova",groups=[[1,2],[3,4]])
def test_pearson(): assert run_statistical_tool("pearson_correlation",x=[1,2,3],y=[2,4,6])["statistic"]>.99
def test_spearman(): assert run_statistical_tool("spearman_correlation",x=[1,2,3],y=[3,2,1])["statistic"]<-.99
def test_arbitrary_tool_denied():
    with pytest.raises(ValueError): run_statistical_tool("exec_python",code="print(1)")
def test_invalid_proportion():
    with pytest.raises(ValueError): run_statistical_tool("proportion_confidence_interval",successes=11,n=10)

