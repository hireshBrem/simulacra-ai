from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parents[1]
SIM_DATA = ROOT / "sim-data"

PUMS_SOURCE = (
    "U.S. Census Bureau ACS 2022 ACS 5-year PUMS API, state=06, "
    "San Francisco PUMA10 codes 07501-07504. Variables: SERIALNO, SPORDER, "
    "AGEP, SEX, RAC1P, HISP, OCCP, PINCP, HINCP, TEN, PWGTP, PUMA10."
)

DERIVATION_RULES = (
    "OCEAN scores are synthetic but rule-derived, not random. Baselines start "
    "at 5, then shift from PUMS microdata fields: occupation code/broad class, "
    "age, person income, household income, tenure, PUMA-level neighborhood "
    "context, and public-facing versus technical work. Technical, research, "
    "arts, education, legal, and young-adult contexts raise Openness; licensed, "
    "managerial, financial, healthcare, owner-stable, and older routine contexts "
    "raise Conscientiousness; sales, service, teaching, caregiving, hospitality, "
    "and community-facing roles raise Extraversion and Agreeableness; low income, "
    "renter exposure, unstable work, and high-cost neighborhood pressure raise "
    "Neuroticism, while high household income and ownership lower it."
)

TENURE = {
    "1": "Owner with mortgage",
    "2": "Owner free and clear",
    "3": "Renter",
}

RACE = {
    "1": "White alone",
    "2": "Black alone",
    "3": "American Indian or Alaska Native alone",
    "5": "Other Pacific Islander alone",
    "6": "Asian alone",
    "7": "Some other race alone",
    "8": "Two or more major race groups",
    "9": "Two or more detailed race groups",
}

PUMA_AREAS = {
    "07501": "north/east San Francisco PUMA",
    "07502": "west/northwest San Francisco PUMA",
    "07503": "central San Francisco PUMA",
    "07504": "south/southeast San Francisco PUMA",
}


PROFILES = [
    ("Mateo Rivera", "Male", "Sunset", "Latino", "Data engineer", "1010", "computer/math"),
    ("James Park", "Male", "Excelsior", "Korean American", "Software developer", "1021", "computer/math"),
    ("Wei Chen", "Male", "Mission", "Chinese American", "Network systems analyst", "1530", "computer/math"),
    ("Nadia Lewis", "Female", "Nob Hill", "Multiracial", "Software engineer", "1021", "computer/math"),
    ("Rosa Calderon", "Male", "Haight", "Latina and multiracial", "Facilities operations manager", "0440", "management"),
    ("Andre Brooks", "Male", "Chinatown", "Black", "Food service manager", "0052", "management"),
    ("Tane Fale", "Male", "Richmond", "Pacific Islander", "Assistant manager, neighborhood retail", "0110", "management"),
    ("Connor Wallace", "Male", "Portola", "White", "Financial analyst", "0735", "business/finance"),
    ("Leilani Cruz", "Male", "Mission", "Pacific Islander and Latino", "Market research analyst", "0710", "business/finance"),
    ("Diego Morales", "Male", "North Beach", "Latino and multiracial", "Social worker", "2145", "education/legal/social service"),
    ("Arjun Patel", "Male", "Sunset", "Indian American", "Paralegal", "2205", "education/legal/social service"),
    ("Elena Yazzie", "Female", "Bayview", "Native American and Latina", "Elementary school teacher", "2320", "education/legal/social service"),
    ("Malik Johnson", "Male", "Chinatown", "Black", "Writer and editor", "2360", "arts/media"),
    ("Samuel Miller", "Male", "Bayview", "White", "Health technologist", "2850", "healthcare"),
    ("Minh Nguyen", "Male", "Mission", "Vietnamese American", "Medical records specialist", "2905", "healthcare"),
    ("Avery Thompson", "Female", "Sunset", "Multiracial", "Registered nurse", "2640", "healthcare"),
    ("Aiyana Begay", "Female", "Castro", "Native American", "Food service worker", "3500", "service"),
    ("Malia Kealoha", "Male", "Excelsior", "Pacific Islander and Latino", "Protective service supervisor", "3323", "service"),
    ("Lucia Ortega", "Male", "Tenderloin", "Latina and multiracial", "Healthcare support aide", "3090", "service"),
    ("Darius Carter", "Male", "Richmond", "Black", "Healthcare support aide", "3090", "service"),
    ("Tane Mahina", "Male", "Chinatown", "Pacific Islander", "Office clerk", "4230", "office/admin"),
    ("Megan Yazzie", "Female", "Mission", "Native American", "Customer service representative", "4540", "office/admin"),
    ("Grace Liu", "Female", "Sunset", "Chinese American", "Retail salesperson", "3940", "sales"),
    ("Peter Novak", "Male", "Portola", "White", "Real estate sales agent", "3870", "sales"),
    ("Keone Tui", "Male", "Richmond", "Pacific Islander", "Building maintenance worker", "4720", "maintenance"),
    ("Samir Haddad", "Male", "Mission", "Multiracial", "Repair technician", "4840", "maintenance"),
    ("Monique Davis", "Female", "North Beach", "Black", "Dispatch and logistics worker", "5740", "transportation/logistics"),
    ("Isabel Torres", "Female", "Bayview", "Latina and multiracial", "Production worker", "5100", "production"),
    ("Carol Yazzie", "Female", "Chinatown", "Native American", "Retired office worker", "N", "retired/not in labor force"),
    ("Rafael Santana", "Male", "Mission", "Latino and Pacific Islander", "Retired service worker", "N", "retired/not in labor force"),
]

PUMS_RECORDS = [
    ("2018HU0525741", "1", 40, "1", "3", "11", "1010", 70000, 180000, "3", 25, "07502"),
    ("2020HU0988696", "2", 39, "1", "1", "01", "1021", 175000, 326000, "3", 13, "07504"),
    ("2018HU1167517", "2", 39, "1", "6", "01", "1530", 205050, 227590, "3", 12, "07503"),
    ("2019HU1367380", "1", 24, "2", "9", "01", "1021", 140000, 290000, "3", 20, "07501"),
    ("2018HU1116118", "4", 35, "1", "8", "19", "0440", 12000, 165000, "3", 45, "07503"),
    ("2020HU0124483", "3", 34, "1", "2", "01", "0052", 75000, 112800, "2", 36, "07501"),
    ("2019HU0051808", "1", 21, "1", "7", "01", "0110", 8000, 30900, "3", 9, "07502"),
    ("2021HU0428279", "1", 50, "1", "1", "01", "0735", 320000, 392000, "3", 44, "07504"),
    ("2019HU1134409", "1", 67, "1", "5", "02", "0710", 10400, 10400, "3", 27, "07503"),
    ("2021HU1254430", "1", 30, "1", "9", "02", "2145", 93000, 93000, "1", 20, "07501"),
    ("2021HU0414172", "1", 29, "1", "6", "01", "2205", 40000, 40000, "3", 47, "07502"),
    ("2018HU0485772", "2", 64, "2", "8", "02", "2320", 72000, 162000, "2", 64, "07504"),
    ("2018HU0018595", "2", 71, "1", "2", "01", "2360", 17000, 197000, "1", 15, "07501"),
    ("2018HU0049059", "1", 68, "1", "1", "01", "2850", 25300, 25300, "3", 10, "07504"),
    ("2019HU0586545", "1", 47, "1", "6", "01", "2905", 24050, 74150, "3", 17, "07503"),
    ("2018HU1104724", "1", 46, "2", "9", "01", "2640", 70000, 140000, "1", 19, "07502"),
    ("2021HU0594760", "1", 41, "2", "3", "01", "3500", 35000, 61300, "3", 11, "07503"),
    ("2018HU0159072", "1", 50, "1", "5", "02", "3323", 185000, 335000, "2", 34, "07504"),
    ("2021HU0221733", "1", 57, "1", "8", "03", "3090", 300000, 605000, "1", 60, "07501"),
    ("2020HU0839175", "1", 32, "1", "2", "01", "3090", 130000, 130000, "3", 25, "07502"),
    ("2020HU0706485", "2", 42, "1", "7", "01", "4230", 19000, 156300, "3", 9, "07501"),
    ("2019HU1189055", "1", 44, "2", "3", "01", "4540", 110000, 110000, "3", 70, "07503"),
    ("2021HU0343129", "2", 50, "2", "6", "01", "3940", 11300, 18650, "3", 11, "07502"),
    ("2021HU1089055", "2", 40, "1", "1", "01", "3870", 100000, 230000, "1", 11, "07504"),
    ("2018HU1086713", "3", 38, "1", "7", "01", "4720", 20000, 80200, "3", 3, "07502"),
    ("2021HU1383650", "1", 26, "1", "9", "01", "4840", 37500, 147100, "3", 10, "07503"),
    ("2019HU1326723", "2", 47, "2", "2", "01", "5740", 39200, 139200, "2", 19, "07501"),
    ("2018HU0878660", "3", 36, "2", "8", "12", "5100", 32000, 148700, "1", 30, "07504"),
    ("2021HU1383455", "2", 72, "2", "3", "01", "N", 12910, 150820, "1", 8, "07501"),
    ("2018HU0004219", "1", 73, "1", "7", "11", "N", 18000, 21000, "1", 13, "07503"),
]


def bracket(value: int) -> str:
    if value < 10000:
        return "Less than $10,000"
    bounds = [
        (15000, "$10,000 to $14,999"), (20000, "$15,000 to $19,999"),
        (25000, "$20,000 to $24,999"), (30000, "$25,000 to $29,999"),
        (35000, "$30,000 to $34,999"), (40000, "$35,000 to $39,999"),
        (45000, "$40,000 to $44,999"), (50000, "$45,000 to $49,999"),
        (60000, "$50,000 to $59,999"), (75000, "$60,000 to $74,999"),
        (100000, "$75,000 to $99,999"), (125000, "$100,000 to $124,999"),
        (150000, "$125,000 to $149,999"), (200000, "$150,000 to $199,999"),
    ]
    for high, label in bounds:
        if value < high:
            return label
    return "$200,000 or more"


def ocean(profile: dict) -> tuple[int, int, int, int, int]:
    o = c = e = a = n = 5
    work = profile["work_class"]
    age = profile["age"]
    hinc = profile["household_income"]
    ten = profile["tenure_code"]

    if work in {"computer/math", "education/legal/social service", "arts/media"}:
        o += 2
    if work in {"management", "business/finance", "healthcare"}:
        c += 2
    if work in {"sales", "service", "office/admin"}:
        e += 2
    if work in {"service", "healthcare", "education/legal/social service"}:
        a += 2
    if work in {"maintenance", "production", "transportation/logistics"}:
        c += 1
    if age >= 60:
        c += 1
        e -= 1
        n -= 1
    if age <= 29:
        o += 1
        n += 1
    if hinc >= 200000:
        n -= 2
    elif hinc < 50000:
        n += 2
    elif hinc < 100000:
        n += 1
    if ten == "3":
        n += 1
    else:
        c += 1
        n -= 1
    return tuple(max(1, min(10, score)) for score in (o, c, e, a, n))


def profile_dict(i: int, overlay: tuple, record: tuple) -> dict:
    serial, sporder, age, sex, race, hisp, occp, pincp, hincp, ten, weight, puma = record
    name, gender, neighborhood, ethnicity, occupation, occp_check, work_class = overlay
    assert occp == occp_check
    return {
        "id": i,
        "name": name,
        "age": age,
        "gender": gender,
        "neighborhood": neighborhood,
        "ethnicity": ethnicity,
        "occupation": occupation,
        "work_class": work_class,
        "serial": serial,
        "sporder": sporder,
        "race_code": race,
        "hisp_code": hisp,
        "occp": occp,
        "person_income": pincp,
        "household_income": hincp,
        "tenure_code": ten,
        "tenure": TENURE[ten],
        "weight": weight,
        "puma": puma,
        "puma_area": PUMA_AREAS[puma],
        "income_bracket": bracket(hincp),
    }


def behavioral_profile(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, e, a, n = scores
    context = (
        f"{p['occupation'].lower()} work, a {p['tenure'].lower()} household, "
        f"and a PUMS household income bracket of {p['income_bracket']}"
    )
    first = (
        f"{p['name'].split()[0]}'s OCEAN pattern is O{o}/C{c}/E{e}/A{a}/N{n}, "
        f"so daily behavior is shaped by {context}."
    )
    if n >= 7:
        second = "They tend to scan for financial and housing risk before relaxing into a conversation, but the profile still reflects the strengths demanded by their work and neighborhood routines."
    elif e >= 7 or a >= 7:
        second = "They are more likely to build trust through repeated small interactions, using work and neighborhood familiarity to decide who needs help, caution, or directness."
    elif c >= 8:
        second = "They prefer predictable routines and concrete obligations, which makes them reliable but sometimes impatient with vague plans."
    else:
        second = "They tend to balance personal ambition with practical limits, responding to city events through the lens of cost, time, and household stability."
    return first + " " + second


def role_markdown(p: dict) -> str:
    scores = ocean(p)
    o, c, e, a, n = scores
    return textwrap.dedent(
        f"""\
        # Role: {p['name']}

        ## Identity
        - **Full name:** {p['name']}
        - **Age:** {p['age']}
        - **Gender:** {p['gender']}
        - **Occupation:** {p['occupation']}
        - **Location:** {p['neighborhood']}, San Francisco, California
        - **Household income bracket:** {p['income_bracket']}
        - **Housing tenure:** {p['tenure']}
        - **Ethnic identity:** {p['ethnicity']}

        ## PUMS Microdata Grounding
        - **PUMS record:** SERIALNO={p['serial']}, SPORDER={p['sporder']}, PWGTP={p['weight']}
        - **PUMS geography:** PUMA10={p['puma']} ({p['puma_area']}); neighborhood is a synthetic assignment within the PUMA, not a PUMS field.
        - **PUMS demographics:** AGEP={p['age']}, SEX={p['gender']}, RAC1P={p['race_code']} ({RACE[p['race_code']]}), HISP={p['hisp_code']}
        - **PUMS economics:** OCCP={p['occp']}, PINCP=${p['person_income']:,}, HINCP=${p['household_income']:,}, TEN={p['tenure_code']} ({p['tenure']})
        - **Source dataset:** {PUMS_SOURCE}

        ## OCEAN Personality Scores
        - **Openness:** {o}/10
        - **Conscientiousness:** {c}/10
        - **Extraversion:** {e}/10
        - **Agreeableness:** {a}/10
        - **Neuroticism:** {n}/10

        ## OCEAN Derivation
        {DERIVATION_RULES}

        ## Behavioral Profile
        {behavioral_profile(p, scores)}

        ## Communication Style
        - Speaks from concrete local experience before abstract principles.
        - Notices money, time, and housing constraints as practical facts in conversation.
        - Uses a register shaped by {p['occupation'].lower()} work and daily life in {p['neighborhood']}.

        ## Goals & Motivations
        - Maintain household stability in an expensive city.
        - Preserve the relationships and routines that make {p['neighborhood']} feel navigable.
        - Make decisions that fit both personal ambition and San Francisco's cost pressures.

        ## Behavioral Constraints
        - Names, exact neighborhood, and biography are synthetic overlays; age, tenure, income, PUMA, race/Hispanic codes, and occupation code are sampled from PUMS.
        - Interprets city events through neighborhood, work, income, tenure, and family obligations.
        - Keeps responses consistent with the OCEAN scores above.
        """
    )


def memory_markdown(p: dict) -> str:
    return textwrap.dedent(
        f"""\
        # Memory Stream: {p['name']}

        [2026-06-20 08:10] Settled into the weekly routine around {p['neighborhood']}, balancing work as a {p['occupation'].lower()} with the cost of staying in San Francisco.
        [2026-06-21 18:20] Reviewed household expenses against the {p['income_bracket']} household income bracket and felt the usual tension between local roots and city prices.
        [2026-06-22 12:35] Noticed a neighborhood issue that mattered because of their {p['tenure'].lower()} situation and made a small practical adjustment rather than treating it as abstract politics.
        """
    )


def sources_markdown(profiles: list[dict]) -> str:
    renters = sum(1 for p in profiles if p["tenure_code"] == "3")
    owners = len(profiles) - renters
    pumas = ", ".join(f"{puma}: {sum(1 for p in profiles if p['puma'] == puma)}" for puma in sorted(PUMA_AREAS))
    work = ", ".join(sorted({p["work_class"] for p in profiles}))
    return textwrap.dedent(
        f"""\
        # San Francisco Resident Population Data Sources

        Generated 30 synthetic San Francisco resident Agents in `agent-1` through `agent-30`.

        ## PUMS Microdata Used
        - {PUMS_SOURCE}
        - Sampling frame: adult person records from San Francisco PUMA10 codes 07501, 07502, 07503, and 07504.
        - Final sample geography counts: {pumas}.
        - Final sample tenure counts: {renters} renters and {owners} owners.
        - Final sample work classes represented: {work}.

        ## Important Interpretation Notes
        - PUMS provides anonymized individual records, not names or exact neighborhoods.
        - Names, exact neighborhoods, and short life histories are synthetic overlays.
        - Age, PUMA, race code, Hispanic-origin code, occupation code, person income, household income, tenure, and person weight come directly from sampled PUMS records.
        - Exact neighborhood assignment is constrained by the sampled San Francisco PUMA but should be treated as approximate.

        ## OCEAN Derivation Rule
        {DERIVATION_RULES}
        """
    )


def main() -> None:
    profiles = [profile_dict(i, overlay, record) for i, (overlay, record) in enumerate(zip(PROFILES, PUMS_RECORDS), start=1)]
    for p in profiles:
        agent_dir = SIM_DATA / f"agent-{p['id']}"
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "ROLE.md").write_text(role_markdown(p), encoding="utf-8")
        (agent_dir / "MEMORY.md").write_text(memory_markdown(p), encoding="utf-8")
    (SIM_DATA / "SF_CENSUS_SOURCES.md").write_text(sources_markdown(profiles), encoding="utf-8")


if __name__ == "__main__":
    main()
