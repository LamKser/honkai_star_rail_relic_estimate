EXTRACT_SUB_STAT_FROM_LIGHTCONE = \
"""
You are given one or more information of a lightcone, weapon from a game. Each of them contains a name and a description of the ability of that lightcone. You need to identify and extract the sub stat of lightcone based on the available sub stat.

### Steps
1. Analyze the ability's description.
2. Identify the lihgtcone's sub-stat appear in available list and extract values and sign of these values of this sub-stat.
3. Identify the lihgtcone's sub-stat not appear in available list, extract values and sign of these values of this sub-stat.
4. If the identifed sub-stat has any condition to activate, add notes to this.
5. Determine when the sub-stat is activated
- "true" if activating after entering the combat
- "false" if activating before entering the combat
6. Return in format. 
- The result should return as JSON below

### JSON Format:
```json
{
    "sub_stat_name": {
        "values": "values of sub-stat",
        "notes": "note of sub-stat"
    }
}
```

### Input:
<lightcone information>

### Response:
""".strip()

EXTRACT_SUB_STAT_FROM_RELIC = \
"""

""".strip()