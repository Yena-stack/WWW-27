# REACH · Response Explorer

An English research artifact for comparing observed human survey responses with stored LLM responses, and inspecting completed REACH-adj evaluations.

## Publish on GitHub Pages

1. Extract the ZIP. Upload its **contents**, including `index.html`, `assets/`, `data/`, and `.github/`, to the root of your repository on `main`.
2. Open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
3. Open **Actions → Deploy REACH to GitHub Pages**, then run the workflow if it has not already started.
4. The finished deployment provides the site URL. It works at both `https://ACCOUNT.github.io/` and `https://ACCOUNT.github.io/REPOSITORY/`.

An alternative is **Deploy from a branch → main → /(root)**; `.nojekyll` is included. Use either the workflow or branch publishing, not both.

GitHub documentation: [Creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) and [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Preview locally

Open `index.html` in a browser. The country data use local script files, so the explorer also works without a server. For a server preview:

```sh
python3 -m http.server 8000
```

Visit `http://localhost:8000/`. No build step, API key, external font, package install, or LLM service is needed to use the site.

## Research tasks

- Select a country, model, age group, gender, political orientation, and religious identity. Attribute filters are applied together.
- Compare one distribution or inspect all 15 items. Switch between weighted and unweighted human estimates.
- Pin group A, change filters to create group B, and inspect human and LLM mean contrasts.
- Export the current 15-item comparison to CSV; export filters, statistics, source fingerprint, and a review note to JSON.
- Share the current view using a URL that includes filters and a pinned comparison. Review notes are not included in shared URLs.
- Inspect the completed matched GPT-OSS method comparison, and the two historical-cohort REACH-adj sample-size evaluations.
- Read the item wording, scale directions, dataset coverage, measure definitions, and adjustment protocol.

## Scope of this release

The diagnostic explorer connects the five completed models, 28 countries and regions, 1.4 million LLM response sets, and 45,036 WVS/EVS survey records. It uses the verified September 21 snapshot. The adjustment views use the completed October 12/13 aggregate analyses, not live experiment status.

The two model sets are different. GPT-OSS and DeepSeek historical adjustment cohorts are separate from the five diagnostic models and the later 1,000-profile matched Direct runs. Final DeepSeek matched generation comparisons and persona-ablation results are not included.

The public site contains aggregate histograms, not individual human/persona records. It supports fixed age and political ranges. Custom numeric age intervals and individual-persona browsing from the former local database tool are intentionally absent from this public release. Estimates require at least 50 valid answers and effective n ≥ 30. These are display rules, not significance tests.

Country files are loaded on demand (roughly 1–2 MB each). All calculations and notes stay in the browser. Review notes are retained locally when browser storage is available.

## Source and reproducibility

`assets/app.js` contains measures and interactions; `assets/style.css` contains the responsive design. `data/` contains the aggregate snapshot; `tools/build_data.py` rebuilds it from the read-only local response index and existing follow-up CSVs. The original data are not part of this repository. See `DATA.md` and `validation/`.

```sh
python -m pip install -r tools/requirements.txt
python tools/build_data.py --db /path/to/responses.sqlite --followup /path/to/FollowupData --reference /path/to/metrics_common.csv
```

Source paper titles and dataset names are retained. The artifact does not include author or institutional identification. Repository ownership and publication settings are chosen by the submitting authors. The noindex metadata can be removed after review if search indexing is wanted.
