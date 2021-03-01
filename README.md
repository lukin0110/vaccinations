# vaccinations-lommel
Dashboard to visualize the progress of the covid vaccination in Lommel.

Numbers are imported on a daily basis from [Vaccinnet+](https://www.laatjevaccineren.be/vaccinnet). Vaccinnet+ is a 
platform from the Flemish Government.

CSV endpoint: https://www.laatjevaccineren.be/vaccination-info/get

## Hugo commands

Build
```bash
cd website
hugo -D --minify
```

Dev server
```bash
cd website
hugo server --minify --ignoreCache
```

## Import & process CSV
Will download the CSV and compute the numbers for a given municipality (eg: Lommel). The CSV will be added to the 
[data folder](./data). The output the crunched numbers will be add the [Hugo data folder](./website/data/).

```bash
cd scripts
python fetch.py 
```

## TODO
- Graph per age
- Graph per gender
- Generate og image with current stats
