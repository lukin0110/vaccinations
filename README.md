# Vaccination Stats per municipality
Dashboard to visualize the progress of the covid vaccination per municipality.

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
A script that downloads the CSV, with the daily vaccination status, and compute the numbers for a given municipality 
(eg: Lommel). The CSV will be added to the [data folder](./data). The output of the crunched numbers will be added to 
the [Hugo data folder](./website/data/).

```bash
cd scripts
python process.py fetch
python process.py crunch
```

## Deployment

Webpage is hosted on [AWS Amplify](https://aws.amazon.com/amplify/) and automatically deployed on each commit. 

## Other

* [How are inhabitants called?](https://nl.wikipedia.org/wiki/Lijst_van_inwonersbenamingen_naar_plaats-_of_streeknaam_in_Belgi%C3%AB)
