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
A script that downloads the CSV and compute the numbers for a given municipality (eg: Lommel). The CSV will be added to 
the [data folder](./data). The output of the crunched numbers will be added to the [Hugo data folder](./website/data/).

```bash
cd scripts
python process.py fetch
python process.py crunch
```

## Deployment

Webpage is hosted on [AWS Amplify](https://aws.amazon.com/amplify/) and automatically deployed on each commit. 


## TODO
- Navigeer naar ander gemeente

- Check IG municipalities: send weekly update
- Graph Distribution per gender
- Github Actions
- Generate og image with current stats



FEEDBACK TINE

Op de 2e heb je wel staan 'enkel' 1 dosis gehad
Tine sent Today at 11:45 PM
bij de eerste staat minstens
Tine sent Today at 11:45 PM
beide zijn verwarrend
Tine sent Today at 11:45 PM
Ik zou gwn zeggen 1e dosis gehad
Tine sent Today at 11:45 PM
het is duidelijk dat we altijd 2 prikken gaan krijgen, minstens is raar want 2 is het max en enkel klinkt wat negatief 🙂


Dan zou ik het inderdaad opsplitsen met de melding dat de focus in de vaccinatiestrategie - omwille van hoe het virus  werkt - ligt op +18

Op en 2e pagina kan je de aantallen vinden van de gehele bevolking omdat zeer kwetsbare jongeren tov het virus ook een intenting krijgen
Tine sent Today at 12:01 AM
en als eerste de 18+
Tine sent Today at 12:01 AM
ook gwn omdat deze cijfers beter ogen natuurlijk
Tine sent Today at 12:01 AM
perceptie is alles in mensen overtuigen voor een prik
