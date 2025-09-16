# Unit Cost Pin (T-001)

A compact Flask app that estimates per-task and monthly costs for capped-retry LLM workflows.

## Getting started

```bash
pip install -r requirements.txt  # or `pip install flask`
FLASK_APP=t001_unit_cost_pin.app flask run
```

Open <http://localhost:5000> and adjust the form inputs. The defaults show the golden-path example from the spec.

## Golden-path example

Inputs:

* `pr_in_1k = 0.003`
* `pr_out_1k = 0.015`
* `tok_in = 1500`
* `tok_out = 1000`
* `p = 0.8`
* `r = 1`
* `overhead = 1.15`
* `volume = 2000`
* `vps = 2.00`

Outputs rendered on the page:

* Cost / Attempt — `$0.01950`
* Expected Attempts / Task — `1.20`
* Success probability within cap — `96.00%`
* Cost / Task — `$0.02691`
* Monthly Cost — `$53.82`
* Breakeven $ / Success — `$0.02803`
* ROI / Task — `$1.893`
