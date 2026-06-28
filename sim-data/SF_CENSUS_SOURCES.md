# San Francisco Resident Population Data Sources

Generated 30 synthetic San Francisco resident Agents in `agent-1` through `agent-30`.

## PUMS Microdata Used
- U.S. Census Bureau ACS 2022 ACS 5-year PUMS API, state=06, San Francisco PUMA10 codes 07501-07504. Variables: SERIALNO, SPORDER, AGEP, SEX, RAC1P, HISP, OCCP, PINCP, HINCP, TEN, PWGTP, PUMA10.
- Sampling frame: adult person records from San Francisco PUMA10 codes 07501, 07502, 07503, and 07504.
- Final sample geography counts: 07501: 8, 07502: 7, 07503: 8, 07504: 7.
- Final sample tenure counts: 18 renters and 12 owners.
- Final sample work classes represented: arts/media, business/finance, computer/math, education/legal/social service, healthcare, maintenance, management, office/admin, production, retired/not in labor force, sales, service, transportation/logistics.

## Important Interpretation Notes
- PUMS provides anonymized individual records, not names or exact neighborhoods.
- Names, exact neighborhoods, and short life histories are synthetic overlays.
- Age, PUMA, race code, Hispanic-origin code, occupation code, person income, household income, tenure, and person weight come directly from sampled PUMS records.
- Exact neighborhood assignment is constrained by the sampled San Francisco PUMA but should be treated as approximate.

## OCEAN Derivation Rule
OCEAN scores are synthetic but rule-derived, not random. Baselines start at 5, then shift from PUMS microdata fields: occupation code/broad class, age, person income, household income, tenure, PUMA-level neighborhood context, and public-facing versus technical work. Technical, research, arts, education, legal, and young-adult contexts raise Openness; licensed, managerial, financial, healthcare, owner-stable, and older routine contexts raise Conscientiousness; sales, service, teaching, caregiving, hospitality, and community-facing roles raise Extraversion and Agreeableness; low income, renter exposure, unstable work, and high-cost neighborhood pressure raise Neuroticism, while high household income and ownership lower it.
