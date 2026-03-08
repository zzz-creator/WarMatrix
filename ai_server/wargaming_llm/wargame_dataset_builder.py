import json
import random
from collections import Counter

OUTPUT_FILE = "wargame_dataset.jsonl"
TARGET_SIZE = 1000

STYLE_INSTRUCTIONS = [
    "Produce a mission-focused update with risk considerations.",
    "Generate a strategic battlefield update for command review.",
    "Provide an operational assessment with likely near-term outcomes.",
    "Write a command-ready analysis of the current battlefield state.",
    "Create an intelligence-informed operational summary.",
    "Draft a staff analysis highlighting implications and priorities.",
]

REPORT_HEADERS = [
    "Operational Assessment:",
    "Commander Update:",
    "Intelligence Summary:",
    "Contingency Brief:",
    "Staff Analysis:",
    "Mission Update:",
]

MONTE_CARLO_TARGET = 50

locations = [
    "Eastern Highlands",
    "Northern Corridor",
    "Central Valley",
    "Western Frontier",
    "Southern Pass",
    "Coastal Delta",
    "River Junction",
    "Industrial Belt",
]

terrain = {
    "Eastern Highlands": ["mountainous", "broken ridgeline", "narrow passes"],
    "Northern Corridor": ["open plains", "rolling steppe", "mixed farmland"],
    "Central Valley": ["river valley", "semi-urban", "agricultural lowlands"],
    "Western Frontier": ["dry plateau", "sparse urban belt", "desert edge"],
    "Southern Pass": ["mountain pass", "forest approach", "constricted roads"],
    "Coastal Delta": ["coastal wetlands", "river delta", "low-elevation urban fringe"],
    "River Junction": ["bridge network", "floodplain", "canal-lined approaches"],
    "Industrial Belt": ["dense urban industrial zone", "rail-centric logistics hub", "warehouse districts"],
}

enemy_activities = [
    "artillery bombardment on forward positions",
    "mechanized probing attack along the main axis",
    "electronic warfare interference against communications",
    "drone reconnaissance over logistics corridors",
    "insurgent sabotage targeting fuel depots",
    "armored concentration near key crossing points",
    "counterbattery fire from dispersed firing points",
    "infiltration attempts through secondary routes",
]

friendly_actions = [
    "deploy reconnaissance units to confirm enemy disposition",
    "reinforce defensive lines with mobile reserves",
    "secure supply routes and convoy timing windows",
    "conduct precision fires on enemy staging zones",
    "fortify command posts and redundant communications",
    "rotate frontline battalions to restore combat effectiveness",
    "establish blocking positions on likely maneuver corridors",
    "integrate UAV surveillance with artillery targeting",
]

risk_levels = ["low", "moderate", "high"]
morale_levels = ["fragile", "steady", "confident", "strained"]
supply_levels = ["stable", "stretched", "intermittent", "degraded"]
weather_states = ["clear", "heavy rain", "fog", "crosswinds", "heat haze", "freezing conditions"]

intent_phrases = [
    "hold terrain while preserving maneuver options",
    "degrade enemy momentum before a counteraction",
    "protect logistics depth and command continuity",
    "shape the battlespace for a deliberate offensive",
    "deny enemy access to crossing points and road hubs",
]

risk_drivers = [
    "extended supply lines under persistent interdiction",
    "uncertain enemy reserve timing",
    "communications disruption during peak activity",
    "limited engineer capacity on damaged routes",
    "higher ammunition expenditure than planned",
]

priority_actions = [
    "tighten ISR coverage on secondary avenues",
    "stagger resupply movements to reduce exposure",
    "pre-position casualty evacuation assets",
    "synchronize fires with reconnaissance refresh cycles",
    "prepare branch plans for rapid sector reinforcement",
]

assessment_openers = [
    "Current reporting indicates",
    "Latest battlefield indicators show",
    "Operational tracking confirms",
    "Field updates suggest",
]

force_ratio_lines = [
    "Force parity ({ratio}) suggests terrain, logistics, and timing will likely decide the engagement.",
    "With a force ratio of {ratio}, tactical execution and sustainment discipline will be decisive.",
    "The {ratio} force ratio implies no automatic advantage, so command agility will shape outcomes.",
    "At {ratio}, battlefield effects will depend more on coordination than raw mass.",
]

risk_actions = [
    "prioritize route security and communication redundancy",
    "tighten reconnaissance refresh cycles before major maneuver",
    "phase fires and movement to avoid overextension",
    "protect logistics nodes while preserving reserve flexibility",
]

comm_effects = {
    "stable": [
        "Stable communications should support synchronized maneuver and fires timing.",
        "Reliable communications improve coordination across command, ISR, and fires networks.",
    ],
    "intermittent jamming": [
        "Intermittent jamming will likely complicate cross-unit coordination and delay fire missions.",
        "Periodic jamming increases the risk of desynchronized maneuver and targeting cycles.",
    ],
    "localized disruption": [
        "Localized communications disruption may create short-lived command gaps at critical moments.",
        "Localized disruption can reduce responsiveness between frontline units and support elements.",
    ],
}

terrain_weather_effects = {
    "coastal wetlands": "Wetland terrain will restrict armored maneuver and favor indirect fires and channelized movement.",
    "river delta": "Delta terrain and crossing complexity increase vulnerability at bridge and ferry nodes.",
    "low-elevation urban fringe": "Low-elevation urban density can complicate fires deconfliction and civilian management.",
    "dense urban industrial zone": "Urban industrial density may compress maneuver space and stress command-and-control clarity.",
    "rail-centric logistics hub": "A rail-centric hub offers sustainment leverage but creates high-value interdiction targets.",
    "warehouse districts": "Warehouse districts create concealment opportunities and increase close-quarters uncertainty.",
    "mountain pass": "Pass terrain can bottleneck movement and amplify the impact of artillery interdiction.",
    "narrow passes": "Narrow passes restrict lateral maneuver and increase dependence on route control.",
    "broken ridgeline": "Ridge fragmentation can disrupt line-of-sight communications and observation continuity.",
    "freezing conditions": "Freezing conditions may slow resupply cycles and increase mechanical stress on vehicles.",
    "heavy rain": "Heavy rain may degrade mobility, reduce sensor fidelity, and delay sustainment movement.",
    "fog": "Fog can reduce detection range and increase uncertainty in fires correction.",
}

tempo_variants = {
    "high-tempo": [
        "Operational tempo across the sector remains elevated.",
        "Command is maintaining a high-tempo posture.",
        "Battle rhythm remains accelerated across the area.",
    ],
    "contested": [
        "Operational tempo remains contested as both sides probe for initiative.",
        "The battle rhythm is contested with frequent shifts in local advantage.",
        "Command is operating in a contested tempo environment.",
    ],
    "deliberate": [
        "Current battle rhythm remains deliberate to preserve control and sequencing.",
        "Command is maintaining a deliberate operational posture.",
        "Operational tempo is deliberate with emphasis on controlled phasing.",
    ],
    "attritional": [
        "The engagement is trending toward an attritional rhythm.",
        "Command is operating in an attritional posture focused on endurance.",
        "Battle rhythm remains attritional with gradual force degradation effects.",
    ],
}


def clamp(value, low, high):
    return max(low, min(high, value))


def tempo_phrase(tempo):
    variants = tempo_variants.get(tempo)
    if variants:
        return random.choice(variants)
    return f"Operational tempo remains {tempo}."


def parse_ratio(force_ratio):
    left, right = force_ratio.split(":")
    return float(left), float(right)


def force_ratio_reasoning(force_ratio):
    left, right = parse_ratio(force_ratio)
    base = random.choice(force_ratio_lines).format(ratio=force_ratio)
    if left > right:
        return f"{base} Friendly numerical edge is present but can be negated by poor timing or route congestion."
    if left < right:
        return f"{base} Relative mass disadvantage increases the penalty for delayed decisions and fragmented fires."
    return f"{base} Balanced force levels increase the importance of weather, morale, and supply resilience."


def choose_tone(style_counter):
    # Keep distribution balanced without making it deterministic.
    minimum = min(style_counter[tone] for tone in REPORT_HEADERS)
    candidates = [tone for tone in REPORT_HEADERS if style_counter[tone] <= minimum + 1]
    return random.choice(candidates)


def make_state():
    loc = random.choice(locations)
    terr = random.choice(terrain[loc])
    enemy = random.choice(enemy_activities)
    friendly = random.choice(friendly_actions)
    risk = random.choice(risk_levels)
    morale = random.choice(morale_levels)
    supply = random.choice(supply_levels)
    weather = random.choice(weather_states)

    success = random.randint(48, 79)
    force_ratio = random.choice(["0.9:1", "1.0:1", "1.1:1", "1.2:1", "1.3:1"])
    tempo = random.choice(["deliberate", "contested", "high-tempo", "attritional"])
    civ = random.choice(["minimal", "moderate", "significant"])
    intent = random.choice(intent_phrases)
    driver = random.choice(risk_drivers)
    priority = random.choice(priority_actions)

    if risk == "high":
        success = clamp(success - random.randint(4, 10), 40, 75)
    if supply in {"degraded", "intermittent"}:
        success = clamp(success - random.randint(2, 7), 40, 76)
    if morale == "confident" and supply == "stable":
        success = clamp(success + random.randint(2, 6), 45, 84)

    input_text = (
        f"Location: {loc}\n"
        f"Terrain: {terr}\n"
        f"Enemy Activity: {enemy}\n"
        f"Friendly Action: {friendly}\n"
        f"Operational Risk: {risk}\n"
        f"Success Probability: {success}%\n"
        f"Morale: {morale}\n"
        f"Supply Stability: {supply}\n"
        f"Weather: {weather}\n"
        f"Estimated Force Ratio (Friendly:Enemy): {force_ratio}\n"
        f"Current Operational Tempo: {tempo}\n"
        f"Civilian Environment Pressure: {civ}\n"
        f"Command Intent: {intent}\n"
        f"Primary Risk Driver: {driver}\n"
        f"Immediate Priority: {priority}\n"
        f"Communications Status: {random.choice(['stable', 'intermittent jamming', 'localized disruption'])}\n"
        f"Mobility Status: {random.choice(['routes mostly open', 'key routes contested', 'bridges under observation'])}\n"
        f"Fires Status: {random.choice(['adequate ammunition levels', 'moderate expenditure pressure', 'tight fire allocation'])}"
    )

    return {
        "location": loc,
        "terrain": terr,
        "enemy": enemy,
        "friendly": friendly,
        "risk": risk,
        "success": success,
        "morale": morale,
        "supply": supply,
        "weather": weather,
        "tempo": tempo,
        "civ": civ,
        "intent": intent,
        "driver": driver,
        "priority": priority,
        "comms": input_text.split("Communications Status: ")[1].split("\n")[0],
        "input": input_text,
    }


def make_output(state):
    header = state["tone"]
    ratio_line = force_ratio_reasoning(state["force_ratio"])
    tempo_line = tempo_phrase(state["tempo"])
    comms_line = random.choice(comm_effects.get(state["comms"], comm_effects["stable"]))
    terrain_weather_line = random.choice([
        terrain_weather_effects.get(state["terrain"], ""),
        terrain_weather_effects.get(state["weather"], ""),
    ]).strip()
    opener = random.choice(assessment_openers)

    if header == "Commander Update:":
        parts = [
            f"{header} {opener} enemy {state['enemy']} near {state['location']}.",
            f"{state['terrain'].capitalize()} terrain and {state['weather']} conditions are affecting maneuver timing.",
            f"Priority is to {state['friendly']} while maintaining intent to {state['intent']}.",
            f"Risk remains {state['risk']} with morale {state['morale']} and supply {state['supply']}; {tempo_line}",
            comms_line,
            terrain_weather_line,
            f"Immediate action should {random.choice(risk_actions)} and execute {state['priority']}.",
            f"Estimated success remains near {state['success']}%. {ratio_line}",
        ]
    elif header == "Intelligence Summary:":
        parts = [
            f"{header} {opener} adversary activity: {state['enemy']} in {state['location']}.",
            f"Terrain ({state['terrain']}) and weather ({state['weather']}) are likely to shape detection windows and engagement geometry.",
            f"Friendly posture to {state['friendly']} supports intent to {state['intent']} but remains sensitive to {state['driver']}.",
            f"Operational risk is {state['risk']}; morale is {state['morale']}; supply stability is {state['supply']}; {tempo_line}",
            comms_line,
            terrain_weather_line,
            f"Recommended near-term focus: {state['priority']} with continued pressure to {random.choice(risk_actions)}.",
            f"Modelled mission success is approximately {state['success']}%. {ratio_line}",
        ]
    elif header == "Contingency Brief:":
        parts = [
            f"{header} {opener} the operating picture in {state['location']} is being shaped by {state['enemy']}.",
            f"Given {state['terrain']} terrain and {state['weather']}, contingency planning should account for mobility disruption.",
            f"Current action to {state['friendly']} remains aligned to intent to {state['intent']}.",
            f"Risk is assessed as {state['risk']} with morale {state['morale']} and supply {state['supply']}; {tempo_line}",
            comms_line,
            terrain_weather_line,
            f"Primary hedge is to {state['priority']} and {random.choice(risk_actions)}.",
            f"Projected success under current assumptions is near {state['success']}%. {ratio_line}",
        ]
    elif header == "Staff Analysis:":
        parts = [
            f"{header} {opener} enemy {state['enemy']} in {state['location']}.",
            f"The interaction of {state['terrain']} terrain, {state['weather']}, and civilian pressure ({state['civ']}) constrains options.",
            f"Friendly intent to {state['intent']} is operationalized by plans to {state['friendly']}.",
            f"The principal risk driver is {state['driver']}; overall risk is {state['risk']}, morale is {state['morale']}, supply is {state['supply']}; {tempo_line}",
            comms_line,
            terrain_weather_line,
            f"Staff recommendation is to {state['priority']} and {random.choice(risk_actions)}.",
            f"Estimated probability of mission success is {state['success']}%. {ratio_line}",
        ]
    elif header == "Mission Update:":
        parts = [
            f"{header} {opener} enemy forces continue {state['enemy']} around {state['location']}.",
            f"Friendly units are executing {state['friendly']} to support intent to {state['intent']}.",
            f"Operational risk is {state['risk']} with morale {state['morale']} and supply {state['supply']}. {tempo_line}",
            comms_line,
            terrain_weather_line,
            f"Priority remains {state['priority']} as success probability tracks near {state['success']}%. {ratio_line}",
        ]
    else:
        parts = [
            f"{header} {opener} enemy forces are executing {state['enemy']} in {state['location']}.",
            f"{state['terrain'].capitalize()} terrain, {state['weather']}, and current operational tempo effects require controlled sequencing.",
            f"Friendly action to {state['friendly']} supports command intent to {state['intent']}.",
            f"Operational risk is {state['risk']} with morale {state['morale']} and supply stability {state['supply']}; {tempo_line}",
            f"Priority should remain on {state['priority']} while efforts continue to {random.choice(risk_actions)}.",
            f"Current success probability is approximately {state['success']}%. {ratio_line}",
        ]

    return " ".join(parts)


def make_monte_carlo_example(style_counter):
    tone = choose_tone(style_counter)
    style_counter[tone] += 1

    action = random.choice([
        "Launch counteroffensive",
        "Hold defensive line",
        "Execute limited probing attack",
        "Conduct deliberate withdrawal to secondary positions",
        "Commit reserves to restore front integrity",
    ])
    risk = random.choice(risk_levels)
    morale = random.choice(morale_levels)
    supply = random.choice(supply_levels)
    weather = random.choice(weather_states)
    success = random.randint(35, 78)

    if risk == "high":
        success = clamp(success - random.randint(3, 8), 25, 72)
    if morale == "fragile":
        success = clamp(success - random.randint(2, 6), 25, 74)
    if supply in {"intermittent", "degraded"}:
        success = clamp(success - random.randint(2, 5), 25, 73)

    input_text = (
        f"Action: {action}\n"
        f"Success Probability: {success}%\n"
        f"Operational Risk: {risk}\n"
        f"Morale: {morale}\n"
        f"Supply Stability: {supply}\n"
        f"Weather: {weather}"
    )

    output_text = (
        f"{tone} A simulated outcome for '{action}' indicates approximately {success}% success under current assumptions. "
        f"Operational risk is {risk} while morale is {morale} and supply is {supply}, so execution reliability may vary between phases. "
        f"Weather effects ({weather}) should be treated as a compounding factor for timing and sustainment. "
        f"If risk controls are reinforced early, the action can remain viable; if not, outcome variance is likely to widen. "
        f"{force_ratio_reasoning(random.choice(['0.8:1','0.9:1','1.0:1','1.1:1']))}"
    )

    return {
        "instruction": "Explain the operational outcome.",
        "input": input_text,
        "output": output_text,
    }


def build_dataset(target_size=TARGET_SIZE):
    dataset = []
    seen_inputs = set()
    style_counter = Counter({tone: 0 for tone in REPORT_HEADERS})

    for _ in range(MONTE_CARLO_TARGET):
        sample = make_monte_carlo_example(style_counter)
        norm_key = " ".join(sample["input"].lower().split())
        if norm_key in seen_inputs:
            continue
        seen_inputs.add(norm_key)
        dataset.append(sample)

    while len(dataset) < target_size:
        state = make_state()
        state["tone"] = choose_tone(style_counter)
        state["force_ratio"] = state["input"].split("Estimated Force Ratio (Friendly:Enemy): ")[1].split("\n")[0]
        norm_key = " ".join(state["input"].lower().split())
        if norm_key in seen_inputs:
            continue
        seen_inputs.add(norm_key)
        style_counter[state["tone"]] += 1

        dataset.append(
            {
                "instruction": random.choice(STYLE_INSTRUCTIONS),
                "input": state["input"],
                "output": make_output(state),
            }
        )

    random.shuffle(dataset)
    return dataset


def save_dataset(dataset, output_file=OUTPUT_FILE):
    with open(output_file, "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    rows = build_dataset()
    save_dataset(rows)
    print(f"Dataset created: {OUTPUT_FILE}")
    print(f"Total samples: {len(rows)}")
