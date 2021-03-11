# Vaccination stats per municipality
Dashboard to visualize the progress of covid vaccinations per municipality.

Numbers are imported on a daily basis from [Vaccinnet+](https://www.laatjevaccineren.be/vaccinnet). Vaccinnet+ is the 
platform of the Flemish Government to manage the covid vaccinations.

CSV endpoint: https://www.laatjevaccineren.be/vaccination-info/get

## Build Hugo website
A statically generated Hugo site. 

Build:
```bash
cd website
hugo -D --minify
```

Dev server (http://localhost:1313):
```bash
cd website
hugo server --minify --ignoreCache
```

## Import & process CSV
A python script that downloads the CSV, with the daily vaccination status, and computes the numbers for all available 
municipalities. The CSV will be added to the [data folder](./data). The output of the crunched numbers (JSON dumps) 
will be added to the [Hugo data folder](./website/data/) per municipality.

```bash
cd scripts
python process.py fetch 11-03-2021
python process.py crunch
```

Shortcut to download, crunch, commit & push a daily update.
```bash
./update.sh
```

## Deployment

Webpage is hosted on [AWS Amplify](https://aws.amazon.com/amplify/) and automatically deployed on each commit. 

AWS Amplify build script (needs to be copy/pasted to the AWS Console).
```yaml
version: 1
applications:
  - frontend:
      phases:
        build:
          commands:
            - hugo -D --minify
      artifacts:
        baseDirectory: public
        files:
          - '**/*'
    appRoot: website
```


## Other

* [How are inhabitants called?](https://nl.wikipedia.org/wiki/Lijst_van_inwonersbenamingen_naar_plaats-_of_streeknaam_in_Belgi%C3%AB)
