"""Plain-language labels for the student profile card.

Codes come from the UCI variable table for "Predict Students' Dropout and
Academic Success". Field names are the column names in eda_uci_data/data/dropout_data.csv.
test_spec.py checks that every code used in the data has a label.
"""

MARITAL = {1: "Single", 2: "Married", 3: "Widowed", 4: "Divorced",
           5: "Living together (de facto union)", 6: "Legally separated"}

APPLICATION_MODE = {
    1: "Regular admission, 1st round",
    2: "Special admission route (government regulation)",
    5: "Special quota for Azores residents, 1st round",
    7: "Already holds another higher-education degree",
    10: "Special admission route (government regulation)",
    15: "International student (bachelor's)",
    16: "Special quota for Madeira residents, 1st round",
    17: "Regular admission, 2nd round",
    18: "Regular admission, 3rd round",
    26: "Special admission route (different study plan)",
    27: "Special admission route (from another institution)",
    39: "Mature-student entry (over 23)",
    42: "Transfer",
    43: "Change of course",
    44: "Holds a technological specialization diploma",
    51: "Change of institution or course",
    53: "Holds a short-cycle diploma",
    57: "Change of institution or course (international)",
}

COURSE = {
    33: "Biofuel production technologies",
    171: "Animation and multimedia design",
    8014: "Social service (evening attendance)",
    9003: "Agronomy",
    9070: "Communication design",
    9085: "Veterinary nursing",
    9119: "Informatics engineering",
    9130: "Equinculture",
    9147: "Management",
    9238: "Social service",
    9254: "Tourism",
    9500: "Nursing",
    9556: "Oral hygiene",
    9670: "Advertising and marketing management",
    9773: "Journalism and communication",
    9853: "Basic education",
    9991: "Management (evening attendance)",
}

PREVIOUS_QUALIFICATION = {
    1: "Secondary education",
    2: "Bachelor's degree",
    3: "Degree",
    4: "Master's degree",
    5: "Doctorate",
    6: "Frequency of higher education",
    9: "12th year, not completed",
    10: "11th year, not completed",
    12: "Other: 11th year",
    14: "10th year",
    15: "10th year, not completed",
    19: "Basic education 3rd cycle (9th to 11th year)",
    38: "Basic education 2nd cycle (6th to 8th year)",
    39: "Technological specialization course",
    40: "Degree (1st cycle)",
    42: "Professional higher technical course",
    43: "Master (2nd cycle)",
}

NATIONALITY = {
    1: "Portuguese", 2: "German", 6: "Spanish", 11: "Italian", 13: "Dutch", 14: "English",
    17: "Lithuanian", 21: "Angolan", 22: "Cape Verdean", 24: "Guinean", 25: "Mozambican",
    26: "Santomean", 32: "Turkish", 41: "Brazilian", 62: "Romanian", 100: "Moldovan",
    101: "Mexican", 103: "Ukrainian", 105: "Russian", 108: "Cuban", 109: "Colombian",
}

# Parents' education: one table covers both mother and father.
EDUCATION = {
    1: "Secondary education (12th year)",
    2: "Bachelor's degree",
    3: "Degree",
    4: "Master's degree",
    5: "Doctorate",
    6: "Frequency of higher education",
    9: "12th year, not completed",
    10: "11th year, not completed",
    11: "7th year (old system)",
    12: "Other: 11th year",
    13: "2nd year of complementary high school course",
    14: "10th year",
    18: "General commerce course",
    19: "Basic education 3rd cycle (9th to 11th year)",
    20: "Complementary high school course",
    22: "Technical-professional course",
    25: "Complementary high school course, not concluded",
    26: "7th year",
    27: "2nd cycle of general high school course",
    29: "9th year, not completed",
    30: "8th year",
    31: "General course of administration and commerce",
    33: "Supplementary accounting and administration",
    34: "Unknown",
    35: "Cannot read or write",
    36: "Can read, without a 4th-year diploma",
    37: "Basic education 1st cycle (4th/5th year)",
    38: "Basic education 2nd cycle (6th to 8th year)",
    39: "Technological specialization course",
    40: "Degree (1st cycle)",
    41: "Specialized higher studies course",
    42: "Professional higher technical course",
    43: "Master (2nd cycle)",
    44: "Doctorate (3rd cycle)",
}

# Parents' jobs: one table covers both mother and father.
OCCUPATION = {
    0: "Student (as recorded)",
    1: "Legislators, senior officials and managers",
    2: "Specialists in intellectual and scientific activities",
    3: "Intermediate-level technicians and professions",
    4: "Administrative staff",
    5: "Personal services, security workers and sellers",
    6: "Farmers and skilled agricultural, fishery and forestry workers",
    7: "Skilled workers in industry, construction and crafts",
    8: "Machine operators and assembly workers",
    9: "Unskilled workers",
    10: "Armed forces professions",
    90: "Other situation",
    99: "Blank (not stated)",
    101: "Armed forces officers",
    102: "Armed forces sergeants",
    103: "Other armed forces personnel",
    112: "Directors of administrative and commercial services",
    114: "Hotel, catering, trade and other services directors",
    121: "Physical sciences, mathematics and engineering specialists",
    122: "Health professionals",
    123: "Teachers",
    124: "Finance and accounting specialists",
    125: "ICT specialists",
    131: "Intermediate science and engineering technicians",
    132: "Intermediate health technicians",
    134: "Intermediate legal, social, sports and cultural technicians",
    135: "ICT technicians",
    141: "Office workers and secretaries",
    143: "Data, accounting, statistical and financial operators",
    144: "Other administrative support staff",
    151: "Personal service workers",
    152: "Sellers",
    153: "Personal care workers",
    154: "Protection and security workers",
    161: "Market-oriented farmers and skilled agricultural workers",
    163: "Subsistence farmers, fishers, hunters and gatherers",
    171: "Skilled construction workers (not electricians)",
    172: "Skilled metalworkers",
    173: "Skilled printing, precision-instrument and craft workers",
    174: "Skilled electricity and electronics workers",
    175: "Food, wood, clothing and other craft workers",
    181: "Fixed plant and machine operators",
    182: "Assembly workers",
    183: "Vehicle drivers and mobile equipment operators",
    191: "Cleaning workers",
    192: "Unskilled agricultural, fishery and forestry workers",
    193: "Unskilled extractive, construction, manufacturing and transport workers",
    194: "Meal preparation assistants",
    195: "Street vendors and street service providers",
}

CODEBOOK = {
    "Marital status": MARITAL,
    "Application mode": APPLICATION_MODE,
    "Course": COURSE,
    "Previous qualification": PREVIOUS_QUALIFICATION,
    "Nacionality": NATIONALITY,
    "Mother's qualification": EDUCATION,
    "Father's qualification": EDUCATION,
    "Mother's occupation": OCCUPATION,
    "Father's occupation": OCCUPATION,
}

# (data field, plain label, kind). Headings follow the team's list.
GROUPS = [
    ("Background", [
        ("Age at enrollment", "Age when starting", "int"),
        ("Gender", "Gender", "gender"),
        ("Nacionality", "Nationality", "code"),
        ("International", "International student", "yesno"),
        ("Marital status", "Marital status", "code"),
        ("Displaced", "Displaced", "yesno"),
        ("Educational special needs", "Special educational needs", "yesno"),
        ("Previous qualification", "Previous qualification", "code"),
        ("Previous qualification (grade)", "Previous qualification grade", "grade200"),
    ]),
    ("Application", [
        ("Application mode", "Admission route", "code"),
        ("Application order", "Application choice", "order"),
        ("Course", "Course", "code"),
        ("Daytime/evening attendance", "Attendance", "attendance"),
        ("Admission grade", "Admission grade", "grade200"),
    ]),
    ("Family", [
        ("Mother's qualification", "Mother's education", "code"),
        ("Father's qualification", "Father's education", "code"),
        ("Mother's occupation", "Mother's job", "code"),
        ("Father's occupation", "Father's job", "code"),
    ]),
    ("Finances", [
        ("Scholarship holder", "Scholarship", "yesno"),
        ("Tuition fees up to date", "Tuition fees paid up to date", "yesno"),
        ("Debtor", "Owes money to the university", "yesno"),
    ]),
    ("First-semester results", [
        ("Curricular units 1st sem (enrolled)", "Units enrolled (course subjects)", "int"),
        ("Curricular units 1st sem (credited)", "Units credited from earlier studies", "int"),
        ("Curricular units 1st sem (evaluations)", "Evaluations taken (exams or assessments)", "int"),
        ("Curricular units 1st sem (approved)", "Units passed", "int"),
        ("Curricular units 1st sem (without evaluations)", "Units with no evaluation", "int"),
        ("Curricular units 1st sem (grade)", "Average grade", "grade20"),
    ]),
    ("National economy", [
        ("Unemployment rate", "Unemployment rate (%)", "num1"),
        ("Inflation rate", "Inflation rate (%)", "num1"),
        ("GDP", "GDP growth (%)", "num1"),
    ]),
]

YES_NO = {1: "Yes", 0: "No"}
GENDER = {1: "Male", 0: "Female"}
ATTENDANCE = {1: "Daytime", 0: "Evening"}


def format_value(kind, field, raw):
    v = float(raw)
    if kind == "code":
        return CODEBOOK[field][int(v)]
    if kind == "yesno":
        return YES_NO[int(v)]
    if kind == "gender":
        return GENDER[int(v)]
    if kind == "attendance":
        return ATTENDANCE[int(v)]
    if kind == "order":
        return "%d (0 = first choice, 9 = last choice)" % int(v)
    if kind == "int":
        return "%d" % round(v)
    if kind == "grade200":
        return "%.1f out of 200" % v
    if kind == "grade20":
        if v == 0:
            return "none (no units passed)"
        return "%.1f out of 20 (pass mark 10)" % v
    if kind == "pct":
        return "%.1f%%" % v
    if kind == "num1":
        return "%.1f" % v
    raise ValueError("unknown kind %s" % kind)


def profile_text(case):
    values = {p["field"]: p["value"] for p in case["profile"]}
    lines = []
    for heading, fields in GROUPS:
        lines.append(heading)
        for field, label, kind in fields:
            lines.append("%s: %s" % (label, format_value(kind, field, values[field])))
        lines.append("")
    return "\n".join(lines).rstrip()
