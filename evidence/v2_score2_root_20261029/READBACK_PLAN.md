# Independent economic readback, specified before actual wave-2 scores

29 October 2026, Europe/Paris. This is an observational reconstruction of complete
saved scorer workflows, not a new policy or a postimplementation unit test.
Root owns the readback. The owners' prospective E2E harnesses already cover the
policy implementations. No actual wave-2 candidate has been scored at this point.

Inputs: immutable original returns.csv and costs.csv; each admitted actual run's
atomic targets.npy (decisions 252..3778), rows.npy (earning rows 253..3778), and
source/input/output manifests. The previous joint CSV is the fixed economic
control. Preserve all SHA256 identities, shapes, indices and original counts.

For each saved target sequence, start from zero. At close t compute the dot
product of the previous target and original stock returns, drift that target by
(1+individual return)/(1+portfolio gross return), calculate full one-way fees on
the absolute difference to the new target, with the opening exception only,
and calculate closing gross and equal-weight market return. Drop the empty first
row exactly as the original scorer does. Include the final charged rebalance;
do not force liquidation or add a return earned on the last target.

Compare all four economic columns to saved scorer rows at absolute tolerance
1e-12; report actual maximum discrepancies. Confirm finite/solvent paths,
gross<=5+1e-12 and the policy-specific maximum-weight bounds. Scalar optimality,
inner state and solver certificates remain separately checked by the owners'
source-bound E2E records; a source certificate does not certify a different final
postprocessed optimization problem.

Compute original full and stage scores with population standard deviation,
net beta, annual mean/volatility/fees, maximum/mean gross, maximum stock weight,
worst gross return and measured runtime. Stage earning-index masks are
[253,2015), [2016,3023), [3024,3779); the full mask is [253,3779).

Independently compute paired net-Sharpe intervals against the fixed leader using
block lengths21/63/126,2000draws,seed20261027,including the last legal block start.
For a conditional joint, also compare to the best admitted standalone. Intervals
describe fixed policies on exposed history and do not adjust the entire search.
They are reported, not used as a new significance veto.

Rank operationally admitted complete candidates by the exact primary score and
apply the committed four-plus-one composition rule. Preserve every outcome and
any failed, blocked or incomplete evidence. Do not optimize a mixture, window,
penalty or market-sleeve weight in this readback. No hidden future is accessed.
