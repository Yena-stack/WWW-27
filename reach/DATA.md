# Data and interpretation

## Diagnostic explorer
- Source: verified local WVS/EVS and completed five-model response index.
- Human respondents: 45,036. LLM response sets: 1,400,000.
- Models: GPT-4o mini; GPT-5.6 Luna; Qwen3.5 9B; Ministral 3 8B; Mistral Small 4.
- 28 countries/regions, 15 items, 192 supported filter combinations per country.
- Human weights: WVS W_WEIGHT and EVS gwght; positive finite weights only.
- Item records are `[valid_n, effective_n, probability_1, ..., probability_K]`. No probability entries means the estimate does not meet the public reporting threshold. The absence of a PMF must never be interpreted as zero responses.
- Model records use equal weights. Human data supply weighted and unweighted PMFs. Invalid responses are excluded by item. Display thresholds apply to both response sources.
- Country files contain no individual records or identifiers. The aggregate release is not a formal privacy guarantee.

## Adjustment analyses
`catalog.js` also contains completed aggregate method comparisons and human sample-size results. `group_ot_anchored` identifies current REACH-adj in the matched comparison; older `reach_adj` and `reach_adj_plus_groups` variants from that source are excluded. In the sample-size source, `reach_adj` identifies the current procedure.

The matched GPT-OSS analysis uses 27,984 jointly valid Direct/VS/VOYAGER profiles and 36,636 held-out human respondents. Human-informed methods use 200 calibration respondents per country and a separate 100-person validation set. The response source adjusted is Direct.

The two-model analysis uses separate historical full-persona GPT-OSS and DeepSeek cohorts, each with 10,000 profiles per country, across 20/50/100/200 calibration respondents and 30 nested selections. Same-item answers from different respondents form the evaluation reference. Earlier parameter development and full-source persona marginals provide additional human information; the analysis is retrospective.

National targets coincide across REACH-adj, national OT, and human empirical, so their expected national errors tie. A direct cell-target control matches the evaluated marginal subgroup distributions. Neither equality should be presented as evidence of independent algorithmic superiority.

The site reports mean, SD, entropy, and W1 errors from existing analyses only. Unfinished experiments are not populated with example values.

## Checks
All 2,100 national country–item–model cells were checked against the paper's saved metrics. Maximum absolute difference after PMF rounding was below 3.2e-9. Browser checks cover filtered reference values, A/B contrast signs, weight selection, five-model and 15-item views, small-sample states, exports, URL restoration, mobile overflow, and GitHub project-subdirectory paths.

## References
Data and method links are in the site's Data & methods tab. WVS/EVS access conditions continue to apply to their source data. Rebuilding requires authorized access to the original local index; the website itself uses the released aggregates only.
