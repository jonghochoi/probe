# probe soundness calibration harness — judge package.
#
# Ported and adapted from SoundnessBench (`rigorbench/`) — the sibling
# benchmark that measures whether LLM judges can pre-assess research
# soundness. probe's scout/analysis are themselves LLM rigor judges, so
# this harness measures how well probe's soundness prompt agrees with a
# human-labelled gold set (accuracy + Cohen's kappa), and A/B-tests the
# neutral vs. skeptical prompt to quantify the optimism-bias reduction.

__version__ = "0.1.0"
