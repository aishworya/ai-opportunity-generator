import json
import os
from datetime import datetime

DATA_FILE = "opportunities.json"


def load_opportunities():

    if not os.path.exists(DATA_FILE):

        with open(DATA_FILE, "w") as file:
            json.dump([], file)

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_opportunities(opportunities):

    with open(DATA_FILE, "w") as file:
        json.dump(opportunities, file, indent=4)


def generate_opportunity_number(opportunities):

    if not opportunities:
        return "OPP-1001"

    last_number = int(
        opportunities[-1]["opportunity_number"].split("-")[1]
    )

    return f"OPP-{last_number + 1}"


def create_opportunity(data):

    opportunities = load_opportunities()

    data["opportunity_number"] = generate_opportunity_number(
        opportunities
    )

    data["created_on"] = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    opportunities.append(data)

    save_opportunities(opportunities)


def update_opportunity(updated_data):

    opportunities = load_opportunities()

    for index, opp in enumerate(opportunities):

        if (
            opp["opportunity_number"]
            == updated_data["opportunity_number"]
        ):

            opportunities[index] = updated_data
            break

    save_opportunities(opportunities)


def delete_opportunity(opportunity_number):

    opportunities = load_opportunities()

    updated_opportunities = []

    for opp in opportunities:

        if opp["opportunity_number"] != opportunity_number:
            updated_opportunities.append(opp)

    save_opportunities(updated_opportunities)