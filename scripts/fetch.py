"""Fetch CSV and compute daily numbers."""
import json
import pandas as pd
import requests
import typer
from os import path
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

CSV_ENDPOINT = "https://www.laatjevaccineren.be/vaccination-info/get"


@dataclass
class DailyResult:
    population: int
    total_first_dose: int
    total_second_dose: int

    @property
    def total_minimum_one_dose(self) -> int:
        return self.total_first_dose + self.total_second_dose

    @property
    def percentage_minimum_one_dose(self) -> float:
        return round((self.total_minimum_one_dose / self.population)*100, 2)

    @property
    def percentage_first_dose(self) -> float:
        return round((self.total_first_dose / self.population)*100, 2)

    @property
    def percentage_second_dose(self) -> float:
        return round((self.total_second_dose / self.population)*100, 2)


def data_path(date_of_file: date) -> str:
    """Construct absolute path of a CSV file."""
    data_dir = path.realpath(path.join(path.dirname(path.realpath(__file__)), "..", "data"))
    return path.join(data_dir, f"vaccinations_{date_of_file:%Y-%m-%d}.csv")


def json_path() -> str:
    """Construct absolute path of the JSON output."""
    output_dir = path.realpath(path.join(path.dirname(path.realpath(__file__)), "..", "website", "data"))
    return path.join(output_dir, "numbers.json")


def fetch(date_to_store: date, endpoint: str = CSV_ENDPOINT) -> None:
    """
    The 'vaccinatieteller' updates the Open Data csv file on a daily basis, except for weekend days.

    CSV File endpoint: https://www.laatjevaccineren.be/vaccination-info/get
    Explanation of the CSV file: https://www.laatjevaccineren.be/toelichting-csv-bestand-open-data
    """
    output_path = data_path(date_to_store)
    if path.exists(output_path):
        raise IOError(f"File already exists {output_path}")
    result = requests.get(endpoint)
    with open(output_path, "w") as f:
        f.write(result.text)


def crunch(date_to_crunch: date, municipality: str) -> DailyResult:
    """Compute numbers per municipality."""
    fp = data_path(date_to_crunch)
    df = pd.read_csv(fp)
    df = df[df["MUNICIPALITY"] == municipality]
    # print(df)
    return DailyResult(
        population=int(df["POPULATION_NBR"].fillna(0).sum()),
        total_first_dose=int(df["VACCINATED_FIRST_DOSIS_NBR"].fillna(0).sum()),
        total_second_dose=int(df["VACCINATED_SECOND_DOSIS_NBR"].fillna(0).sum())
    )


def crunch_range(start_date: date, end_date: date, municipality: str) -> Any:
    """."""
    date_range = pd.date_range(start=start_date, end=end_date).tolist()
    results = {
        "labels": [f"{d:%d-%m}" for d in date_range],
        "timeseries_minimum_one_dose": [],
        "timeseries_second_dose": []
    }

    current = DailyResult(1, 0, 0)
    last_date = start_date
    for d in date_range:
        try:
            current = crunch(d, municipality)
            last_date = d
        except FileNotFoundError:
            # If it fails re-use the previous results. There is no data for the weekends for
            # example
            pass

        results["last_date"] = f"{last_date:%d/%m/%Y}"
        results["population"] = current.population
        results["minimum_one_dose"] = current.total_minimum_one_dose
        results["second_dose"] = current.total_second_dose
        results["timeseries_minimum_one_dose"].append(current.percentage_minimum_one_dose)
        results["timeseries_second_dose"].append(current.percentage_second_dose)

    return results


cli = typer.Typer()


@cli.command(name="fetch")
def do_fetch(date_to_fetch: str = "28-02-2021") -> None:
    """Fetch a CSV file."""
    dt = datetime.strptime(date_to_fetch, "%d-%m-%Y")
    typer.echo(f"Fetching {dt.date()}")
    fetch(dt.date())
    typer.echo(crunch(dt.date(), "Lommel"))


@cli.command(name="crunch")
def do_crunch() -> None:
    """Compute timeseries & store results to a JSON file."""
    typer.echo("Hallo")
    # _start_date = date(2021, 1, 11)
    _start_date = date(2021, 2, 24)
    _end_date = date.today()
    print(f"Crunch numbers from {_start_date} to {_end_date}")
    data = crunch_range(_start_date, _end_date, "Lommel")
    print("Store JSON")
    json.dump(data, open(json_path(), "w"), indent=4)


if __name__ == "__main__":
    cli()
