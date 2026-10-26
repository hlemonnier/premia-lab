# A simulated market

Welcome. This folder holds fifteen years of daily data from a stock market that does not
exist: 1000 stocks, 3780 trading days. We built it, and we are not going to tell you how.
Everything you know about this market, you will learn from these files.

## What you get

```
returns.csv              one row per day, one column per stock: that day's simple return
characteristics.csv      one row per day and stock, 13 columns: the stock's characteristics on that day
costs.csv                one row per stock: its one-way trading cost, as a fraction of the notional traded
strategy.py              where your code goes
example_equal_weight.py  the simplest possible strategy, so you can see the shape of the thing
example_naive_mv.py      a first attempt at something real, with its flaws left in
score.py                 runs a strategy over these fifteen years and prints its Sharpe ratio
figures/                 four pictures of the data
```

The characteristics are called
Woe, Malice, Dread, Frolic, Up, Down, Charm, Strange, Top, Bottom, Snap, Crackle, Pop.
The names probably mean nothing. A cost of 0.0005 is 5 basis points: trading 100 dollars
of that stock costs 5 cents, whether you buy or sell. Costs do not change over time.

## The job

Build a strategy for trading these stocks. We will run it on this market for a long time
after these fifteen years end. How long, we will not say, but think in decades. Your score is
the Sharpe ratio it earns over that stretch, after trading costs. Maximize out-of-sample
Sharpe. That is the whole objective, and we mean it: there is no hidden second criterion
about turnover or leverage or looking sensible.

One thing we do ask: keep the book's beta to the equal-weight market under 0.2 out of
sample. We measure it as the slope of your daily net return on the equal-weight market's
daily return over the whole stretch we run, and `score.py` prints the in-sample number.
Hedge the market out or build the book so it is not there. A strategy that is mostly long
the market is not what we are looking for.

There are no other constraints on the portfolio. Long, short, levered, concentrated: your
call, costs and all. A Sharpe ratio does not care how big the book is, but the daily
arithmetic does: positions drift with returns by dividing through one plus the day's
portfolio return, and a book that loses everything in a day is finished. Size yours so that
cannot happen; beyond that, what matters is the mix and how it moves.

## The shape of a strategy

`strategy.py` must define `rebalance`. It may also define `forecast`. The rest is up to you.

`rebalance` is called once per trading day, after the close, and returns the positions to
hold through the next day: one weight per stock, as a fraction of capital. It can ask for
any of these, by name, in any order; we pass whatever your function declares:

- `held_positions`: `(1000,)` what you hold right now, after today's returns have moved it
- `expected_returns`: tomorrow's row of whatever your `forecast` returned, or `None` if you have no `forecast`
- `returns_history`: `(days, 1000)` every daily return through today, oldest first
- `characteristics_history`: `(days, 1000, 13)` every day's characteristics through today
- `trading_costs`: `(1000,)` the one-way cost per stock

It depends on yesterday's answer, so it runs serially, and it has to average under 100
milliseconds per call on one core. It may keep state between calls: a class instance, a
closure, module globals, whatever you like.

`forecast` is the optional slow part, for anything you would rather compute once over the
whole history, vectorized, than redo every day. If it exists we call it once, before the
clock starts, with the entire scoring history, again by name: `returns_history`
`(days, 1000)`, `characteristics_history` `(days, 1000, 13)` and `trading_costs`. It may take
about an hour per century of days. It returns an array whose first axis is days: row `t` is
what `rebalance` receives as `expected_returns` when it positions for day `t`. Usually that
is a `(days, 1000)` array of expected returns, but it can be `(days, 1000, k)` if you carry
several signals, or anything else with days first.

Beyond that, the shape is yours. Fold everything into `rebalance` and skip `forecast`, or do
all the research in `forecast` and keep `rebalance` a thin optimizer; add helper files; keep
whatever state you need. The one fixed point: the positions for a day come out of
`rebalance`, and they may depend only on information from before that day.

## Information and lookahead

Each day's returns and characteristics are published together, after that day's close. When
`rebalance` positions you for a day, it has returns and characteristics through the day
before and nothing later, so there it cannot look ahead by construction.

`forecast` sees the whole history at once, so there the rule is on you: row `t` must be a
function of days before `t` only, returns and characteristics alike. Using day `t`'s return
or characteristics, or anything later, to build row `t` is lookahead, and lookahead fails
the submission no matter how good the number looks.

Tuning on the fifteen years you have is not lookahead. Choose your parameters, half-lives,
shrinkages and risk aversions on the full sample; everyone does, and we expect it. The rule
is about the market after these fifteen years, which you have not seen: nothing your code
does on a day may depend on that day's data or on days after it. We check by reading the
code and by rerunning your `forecast` on altered futures, where the rows before the
alteration must come out the same to floating-point precision. A start-up step that sizes
itself on the first weeks of the data is lookahead for those weeks. If you are unsure
whether something is lookahead, it is.

## How a day goes

Each trading day, after the close:

1. The day's returns come in and move your positions. If you held 2 percent in a stock that
   rose 10 percent on a day the portfolio as a whole made 1 percent, you now hold
   2% x 1.10 / 1.01 = 2.18 percent of it.
2. The day's characteristics are published. We call `rebalance` with the positions you now
   hold, tomorrow's row of your forecast, and returns and characteristics through today.
3. You return the positions to hold through tomorrow. We trade you there and charge each
   stock's cost on the absolute change in its weight. Moving a stock from 2.18 to 1.00
   percent costs 0.0118 times its cost; flipping one from +3 to -3 percent costs 0.06 times
   its cost. Not trading costs nothing.
4. Tomorrow's returns are earned on the positions you returned.

You start with nothing in the book, and your first trade is on us. Our long run starts the
way `score.py` does, at day 252 with an empty book, so the fifteen years you have are the
warm-up and the score is taken over the days after them.

## The score

For each scoring day we record

    x = the portfolio's return that day - that day's trading cost

both as fractions of your capital, and the score is the annualized Sharpe ratio of `x`,
`mean(x) / std(x) * sqrt(252)`. Higher is better.

For example, a strategy that nets 0.04 percent a day on average with a daily standard
deviation of 0.6 percent scores 0.0004 / 0.006 x 15.9 = 1.06. Halve the standard deviation
at the same mean and it scores 2.1. Costs come straight out of the mean, so a strategy that
turns over its whole book every day at 5 basis points gives up 0.05 percent a day before it
has earned anything.

## Working with AI

Use language models as much as you like. We do. Have one write code, argue with it about
the data, ask it what it would try next: all fair, and we would find it odd if you didn't.
Know, though, that we will also hand this same folder to Claude and see what it comes back
with on its own. That is the baseline. What we are looking for is what you add on top of
it: the question you asked that it did not, the thing in the data you noticed and it
missed, the judgment call you made and can defend. Tell us about those in your note.

## What to hand in

`strategy.py`, filled in, with a short note at the top: what you came to believe about this
market, what you built and why, where the AI did the work and where you did, and what you
expect to go wrong over a long time. A page is plenty. If your strategy needs other files,
put them in this folder and say so in the note.

## How we evaluate

The Sharpe ratio over the scoring period is the headline number, with the beta condition
above. Beyond it, we read the code and the note, and we judge two things separately,
wherever in your code they live:

- Alpha research. How you went looking for expected returns in this data, what you found,
  how you decided what to believe and how much to believe it, and how you expect it to hold
  up over a long time.
- Portfolio construction. How you turn forecasts into positions: the risk model, how you
  handle costs and turnover, how you size positions, and the engineering that keeps a call
  under 100 milliseconds.

A strategy can be strong on one and weak on the other. We want to see both, and we want to
see what is yours.

## The examples

`example_equal_weight.py` has no forecast and holds every stock at 0.1 percent; its beta is
one, so it fails the beta condition on purpose. `example_naive_mv.py` forecasts each stock's
trailing one-year mean return and, each day, solves a mean-variance problem on the trailing
year's covariance, charging itself the cost of getting there. The 50 in it is a risk
aversion we picked to keep the book a sane size; choose your own. It is slow, about a
second per call with cvxpy, ten times the budget, and its forecasts are mostly noise. Both
are things to fix, not hints.

## Pictures

`figures/` has four pictures of the data, there to orient you: the total return of an
equal-weight portfolio of all 1000 stocks, its trailing one-year volatility, and the
full-sample covariance and correlation matrices of the stocks, each with the stocks
ordered by clustering so that groups that move together sit next to each other. Everything
in them you can recompute from the CSVs.

## Running things

```
python score.py example_equal_weight
python score.py example_naive_mv
python score.py strategy
```

`score.py` runs `forecast` once over the fifteen years if you have one, then replays
`rebalance` day by day from day 252 starting with an empty book, and prints the Sharpe
ratio, the annual return and volatility, the beta to the equal-weight market, the yearly
cost, the average gross exposure, how long `forecast` took and what that implies per
century, and the time per `rebalance` call. Change `START` for a shorter look. We will run
your strategy with numpy, pandas, scipy, cvxpy, scikit-learn and lightgbm installed and
nothing else, so stay within those.

Good luck. We are curious what you find.
