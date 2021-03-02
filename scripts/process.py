"""Fetch CSV and compute daily numbers."""
import json
import pandas as pd
import requests
import typer
from os import path
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, List

CSV_ENDPOINT = "https://www.laatjevaccineren.be/vaccination-info/get"


@dataclass
class History:
    population: int
    total_first_dose: int
    total_second_dose: int

    @property
    def total_minimum_one_dose(self) -> int:
        return self.total_first_dose + self.total_second_dose


@dataclass
class DailyResults:
    history_all: History
    history_adults: History
    per_age_population: List[int]
    per_age_first_dose: List[int]
    per_age_second_dose: List[int]

    @property
    def per_age_percentage_first_dose(self) -> List[float]:
        return [round(100*v/self.per_age_population[i], 2) for i, v in enumerate(self.per_age_first_dose)]

    @property
    def per_age_percentage_second_dose(self) -> List[float]:
        return [round(100*v/self.per_age_population[i], 2) for i, v in enumerate(self.per_age_second_dose)]


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


def load_range(start_date: date, end_date: date) -> pd.DataFrame:
    """Load a range of CSV files into a DataFrame."""
    date_range = pd.date_range(start=start_date, end=end_date).tolist()
    dfs = []

    last_date = start_date
    for d in date_range:
        df = None
        try:
            df = pd.read_csv(data_path(d))
            last_date = d
        except FileNotFoundError:
            # If it fails re-use the previous DataFrame. There is no data for the weekends for
            # example
            if len(dfs) > 0:
                df = dfs[-1].copy(deep=True)
        if df is not None:
            df["DATE"] = d
            dfs.append(df)

    all_df = pd.concat(dfs)
    all_df.last_date = last_date
    return all_df


def crunch_day(df: pd.DataFrame, municipality: str) -> DailyResults:
    """Compute numbers per municipality."""
    mdf = df[df["MUNICIPALITY"] == municipality].copy()

    def re_arrange(v):
        if v in ["0-9", "10-19"]:
            return "0-19"
        if v in ["20-29", "30-39"]:
            return "20-39"
        if v in ["40-49", "50-59"]:
            return "40-59"
        if v in ["60-69", "70-79"]:
            return "60-79"
        return "80+"

    mdf["AGE_CD"] = mdf.apply(lambda row: re_arrange(row["AGE_CD"]), axis=1)
    # print(df)
    df_ages = mdf.groupby("AGE_CD", as_index=False).agg({
        'POPULATION_NBR': sum,
        'VACCINATED_FIRST_DOSIS_NBR': sum,
        'VACCINATED_SECOND_DOSIS_NBR': sum
    })
    df_ages = df_ages.sort_values(by='AGE_CD', ascending=False)
    df_adults = mdf[mdf["ADULT_FL(18+)"] == 1]

    return DailyResults(
        history_all=History(
            population=int(mdf["POPULATION_NBR"].fillna(0).sum()),
            total_first_dose=int(mdf["VACCINATED_FIRST_DOSIS_NBR"].fillna(0).sum()),
            total_second_dose=int(mdf["VACCINATED_SECOND_DOSIS_NBR"].fillna(0).sum()),
        ),
        history_adults=History(
            population=int(df_adults["POPULATION_NBR"].fillna(0).sum()),
            total_first_dose=int(df_adults["VACCINATED_FIRST_DOSIS_NBR"].fillna(0).sum()),
            total_second_dose=int(df_adults["VACCINATED_SECOND_DOSIS_NBR"].fillna(0).sum()),
        ),
        per_age_population=df_ages['POPULATION_NBR'].values.tolist(),
        per_age_first_dose=df_ages['VACCINATED_FIRST_DOSIS_NBR'].values.tolist(),
        per_age_second_dose=df_ages['VACCINATED_SECOND_DOSIS_NBR'].values.tolist()
    )


def crunch(df: pd.DataFrame, start_date: date, end_date: date, municipality: str) -> Any:
    """."""
    date_range = pd.date_range(start=start_date, end=end_date).tolist()
    labels = [f"{d:%d-%m}" for d in date_range]
    results = {}
    last_day = crunch_day(df[df["DATE"] == pd.Timestamp(end_date)], municipality)
    mdf = df[df["MUNICIPALITY"] == municipality]

    def timeseries(_df, population: int):
        grouped = _df.groupby("DATE", as_index=False).agg({
            "POPULATION_NBR": sum,
            "VACCINATED_FIRST_DOSIS_NBR": sum,
            "VACCINATED_SECOND_DOSIS_NBR": sum
        }).sort_values(by="DATE", ascending=True)
        grouped["VACCINATED_ONE_DOSIS_NBR"] = grouped.apply(
            lambda r: r["VACCINATED_FIRST_DOSIS_NBR"] + r["VACCINATED_SECOND_DOSIS_NBR"], axis=1)

        return {
            "timeseries_minimum_one_dose": [0] + grouped["VACCINATED_ONE_DOSIS_NBR"].apply(
                lambda v: round(v / population * 100, 2)).tolist(),
            "timeseries_second_dose": [0] + grouped["VACCINATED_SECOND_DOSIS_NBR"].apply(
                lambda v: round(v / population * 100, 2)).tolist()
        }

    # Compute timeseries
    # Historical numbers (all & adults only)
    results["history_all"] = {
        "labels": labels,
        "population": last_day.history_all.population,
        "minimum_one_dose": last_day.history_all.total_minimum_one_dose,
        "second_dose": last_day.history_all.total_second_dose,
        **timeseries(mdf, last_day.history_all.population)
    }
    results["history_adults"] = {
        "labels": labels,
        "population": last_day.history_adults.population,
        "minimum_one_dose": last_day.history_adults.total_minimum_one_dose,
        "second_dose": last_day.history_adults.total_second_dose,
        **timeseries(mdf[mdf["ADULT_FL(18+)"] == 1], last_day.history_adults.population)
    }

    # Per age numbers
    results["per_age"] = {
        "labels": ["80+", "60-79", "40-59", "20-39", "0-19"],
        "population": last_day.per_age_population,
        "first_dose": last_day.per_age_first_dose,
        "second_dose": last_day.per_age_second_dose,
        "percentage_first_dose": last_day.per_age_percentage_first_dose,
        "percentage_second_dose": last_day.per_age_percentage_second_dose,
    }
    results["last_date"] = f"{df.last_date:%d/%m/%Y}"
    return results


cli = typer.Typer()


@cli.command(name="fetch")
# def do_fetch(date_to_fetch: str = "01-03-2021") -> None:
# def do_fetch(date_to_fetch: str = typer.Argument(f"{date.today():%d-%m-%Y}")) -> None:
def do_fetch(date_to_fetch: str = typer.Argument(...)) -> None:
    """Fetch a CSV file."""
    dt = datetime.strptime(date_to_fetch, "%d-%m-%Y")
    typer.echo(f"Fetching {dt.date()}")
    fetch(dt.date())


@cli.command(name="crunch")
def do_crunch() -> None:
    """Compute timeseries & store results to a JSON file."""
    typer.echo("Hallo")
    # _start_date = date(2021, 1, 11)
    _start_date = date(2021, 2, 24)
    _end_date = date.today() - timedelta(days=1)
    print(f"Loading data from {_start_date} to {_end_date}")
    df = load_range(_start_date, _end_date)
    print(f"Crunch daily numbers")
    data = crunch(df, _start_date, _end_date, "Lommel")
    print("Store JSON")
    # print(data)
    json.dump(data, open(json_path(), "w"), indent=4)


if __name__ == "__main__":
    cli()
