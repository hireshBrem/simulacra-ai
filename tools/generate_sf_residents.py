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

CIVIC_DERIVATION_RULES = (
    "Civic reasoning profiles are synthetic, general-purpose priors derived from "
    "occupation class, age, income, housing tenure, neighborhood context, and OCEAN "
    "scores. They are not issue-specific voting instructions; they describe how an "
    "agent tends to evaluate tradeoffs across many civic, workplace, economic, and "
    "neighborhood scenarios."
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


def civic_profile(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, e, a, n = scores
    work = p["work_class"]
    age = p["age"]
    hinc = p["household_income"]
    renter = p["tenure_code"] == "3"

    orientation = _political_orientation(p, scores)
    trust = _institutional_trust(p, scores)
    worldview = _economic_worldview(p, scores)
    regulation = _regulation_tolerance(p, scores)
    convenience = _consumer_convenience_priority(p, scores)
    solidarity = _solidarity_radius(p, scores)
    risk = _risk_tolerance(p, scores)
    info = _information_diet(p)
    persuasion = _persuasion_triggers(p, scores)
    suspicion = _suspicion_triggers(p, scores)
    heuristic = _ballot_heuristic(p, scores)

    return textwrap.dedent(
        f"""\
        ## Civic Reasoning Profile
        - **Political orientation:** {orientation}
        - **Institutional trust:** {trust}
        - **Economic worldview:** {worldview}
        - **Regulation tolerance:** {regulation}
        - **Consumer convenience priority:** {convenience}
        - **Solidarity radius:** {solidarity}
        - **Risk tolerance:** {risk}
        - **Information diet:** {info}
        - **Persuasion triggers:** {persuasion}
        - **Suspicion triggers:** {suspicion}
        - **Default ballot heuristic:** {heuristic}
        """
    ).strip()


def _political_orientation(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, _e, a, _n = scores
    work = p["work_class"]
    if work in {"education/legal/social service", "arts/media"} or a >= 7:
        return "Progressive-pragmatic; sympathetic to public goods and vulnerable residents, but still wants implementation details to make sense."
    if work in {"business/finance", "sales"} and p["household_income"] >= 150000:
        return "Moderate and market-aware; open to social protections but cautious about rules that disrupt services, prices, or business activity."
    if work in {"computer/math"} and o >= 7:
        return "Technocratic center-left; prefers evidence, measurable outcomes, and practical fixes over slogans."
    if p["age"] >= 65 or c >= 7:
        return "Pragmatic and stability-oriented; more local than ideological, with a bias toward predictable services and clear accountability."
    return "Non-ideological center-left; decides from household pressure, neighborhood experience, and perceived fairness."


def _institutional_trust(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    _o, c, _e, a, n = scores
    if n >= 7:
        return "Medium-low trust in City Hall and large institutions; trusts direct experience, coworkers, and neighborhood signals more."
    if c >= 7 and p["age"] >= 60:
        return "Medium trust in formal institutions when rules are clear, with skepticism toward rushed or poorly explained changes."
    if p["work_class"] in {"business/finance", "computer/math"}:
        return "Medium trust in data and competent administration; low patience for vague claims from campaigns or agencies."
    if a >= 7:
        return "Medium trust in schools, healthcare, service providers, and community organizations; more cautious about corporations."
    return "Mixed trust; listens to official arguments but checks them against workplace and neighborhood experience."


def _economic_worldview(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    _o, _c, _e, a, n = scores
    work = p["work_class"]
    if work in {"business/finance", "sales", "management"}:
        return "Business-aware; values entrepreneurship, predictable rules, and local commerce, while recognizing that large institutions can exploit leverage."
    if work in {"service", "maintenance", "production", "transportation/logistics", "office/admin"}:
        return "Work-and-cost focused; evaluates policy by wages, prices, scheduling pressure, and whether ordinary workers absorb the downside."
    if work in {"education/legal/social service", "healthcare"} or a >= 7:
        return "Community-and-care focused; weighs household stability, access, public benefit, and impact on people with less bargaining power."
    if work == "computer/math":
        return "Systems-oriented; receptive to innovation and platforms, but skeptical when market power creates unfair or inefficient outcomes."
    if n >= 6:
        return "Household-security focused; looks first at rent, bills, job stability, and exposure to sudden cost increases."
    return "Pragmatic mixed economy; supports markets and public rules when each seems suited to the problem."


def _regulation_tolerance(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, _e, a, n = scores
    work = p["work_class"]
    if work in {"business/finance", "sales", "management"} and c >= 6:
        return "Medium-low; supports guardrails for obvious harm but worries about compliance burden and unintended side effects."
    if work in {"education/legal/social service", "healthcare"} or a >= 7:
        return "Medium-high; supports regulation when it protects access, fairness, safety, or vulnerable residents."
    if work == "computer/math" and o >= 7:
        return "Medium; wants targeted, evidence-backed rules rather than broad symbolic restrictions."
    if n >= 7:
        return "Medium; supports protections against shocks but is wary of rules that could raise daily costs."
    return "Medium; willing to regulate concrete harms, skeptical of vague promises."


def _consumer_convenience_priority(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    _o, _c, _e, _a, n = scores
    work = p["work_class"]
    if work in {"computer/math", "business/finance", "management", "transportation/logistics"} and p["household_income"] >= 125000:
        return "High; time-saving services matter, especially when work is demanding or schedules are tight."
    if p["age"] >= 65:
        return "Medium-high; values convenience and access, but dislikes hidden fees and unreliable service."
    if n >= 7 or p["household_income"] < 75000:
        return "Medium; convenience matters, but price and household risk usually come first."
    return "Medium; appreciates convenience but weighs it against cost, fairness, and neighborhood effects."


def _solidarity_radius(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    _o, _c, _e, a, n = scores
    if a >= 7:
        return "Starts with household and workplace, then extends quickly to neighbors, patients, students, customers, and vulnerable residents."
    if n >= 7:
        return "Starts with household security and close community, then expands when the policy risk feels manageable."
    if p["tenure_code"] != "3":
        return "Starts with household, block, and neighborhood stability, with attention to long-term city livability."
    return "Starts with household budget and neighborhood routines, then considers citywide fairness."


def _risk_tolerance(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, _e, _a, n = scores
    if n >= 7 or p["household_income"] < 50000:
        return "Low; avoids policies that could create new costs, instability, or service loss."
    if o >= 7 and c <= 5 and p["age"] < 45:
        return "Medium-high; open to experiments if the logic is clear and the downside is bounded."
    if c >= 7 or p["age"] >= 60:
        return "Low-medium; prefers incremental, enforceable changes over sweeping experiments."
    return "Medium; accepts tradeoffs when the benefit is concrete."


def _information_diet(p: dict) -> str:
    work = p["work_class"]
    if work == "computer/math":
        return "Local news summaries, search, social feeds, coworkers, group chats, and ballot guides."
    if work in {"education/legal/social service", "healthcare"}:
        return "Workplace conversations, local news, union or professional circles, neighborhood groups, and ballot guides."
    if work in {"service", "sales", "office/admin", "maintenance", "production", "transportation/logistics"}:
        return "Coworkers, customers, family, neighborhood conversations, local headlines, social media, and campaign mailers."
    if work in {"business/finance", "management"}:
        return "Local business news, professional peers, clients, neighborhood signals, ballot mailers, and mainstream news."
    return "Local news, family, neighbors, campaign mailers, and long-running memories of city change."


def _persuasion_triggers(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, _e, a, n = scores
    triggers = []
    if o >= 7:
        triggers.append("clear evidence")
    if c >= 7:
        triggers.append("specific implementation details")
    if a >= 7:
        triggers.append("credible harm reduction for people they encounter directly")
    if n >= 7 or p["household_income"] < 75000:
        triggers.append("lower household risk")
    if p["work_class"] in {"business/finance", "management", "sales"}:
        triggers.append("predictable economic effects")
    if not triggers:
        triggers.extend(["concrete examples", "trusted local messengers"])
    return ", ".join(triggers) + "."


def _suspicion_triggers(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    _o, c, _e, _a, n = scores
    triggers = ["vague funding", "interest-group slogans"]
    if p["work_class"] in {"business/finance", "management", "sales"}:
        triggers.append("rules that ignore operating realities")
    if p["work_class"] == "computer/math":
        triggers.append("claims without data")
    if p["household_income"] < 75000 or n >= 7:
        triggers.append("policies that could raise daily costs")
    if c >= 7 or p["age"] >= 60:
        triggers.append("unclear enforcement")
    return ", ".join(triggers) + "."


def _ballot_heuristic(p: dict, scores: tuple[int, int, int, int, int]) -> str:
    o, c, _e, a, n = scores
    if n >= 7 or p["household_income"] < 50000:
        return "If unsure, votes for the option that seems least likely to destabilize rent, work, bills, or essential services."
    if c >= 7 or p["age"] >= 60:
        return "If unsure, votes No on complicated structural changes and Yes on simple, enforceable protections with clear beneficiaries."
    if p["work_class"] in {"business/finance", "management", "sales"}:
        return "If unsure, follows the side with the clearest account of who pays, who benefits, and how businesses will adapt."
    if o >= 7:
        return "If unsure, looks for evidence and mechanism rather than relying on partisan or moral framing."
    if a >= 7:
        return "If unsure, leans toward the side that reduces harm for people they personally recognize from work or neighborhood life."
    return "If unsure, uses a practical cost-benefit test grounded in household and neighborhood consequences."


def role_markdown(p: dict) -> str:
    scores = ocean(p)
    o, c, e, a, n = scores
    content = textwrap.dedent(
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

        %%CIVIC_PROFILE%%

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
    return content.replace("%%CIVIC_PROFILE%%", civic_profile(p, scores))


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
