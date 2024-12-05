# Mapping schema definitions for different carriers
# These mappings specify how raw data columns map to standard fields

SCHEMA_MAPPINGS = {
    "Centene": {
        "agent_name": "Writing Broker Name",
        "agent_id": "Writing Broker NPN",
        "agency_name": "Earner Name",
        "agency_id": "Earner NPN",
        "commission_period": "Pay Period",
        "commission_amount": "Payment Amount",
        "plan_name": "Plan Name",
        "is_adjusted": lambda df: df["Prior Plan Type"] == df["Plan Type"],
        "effective_date": "Effective Date",
        "term_date": "Member Term Date",
        "description": "Description",
    },
    
    "Emblem": {
        "agent_name": "Rep Name",
        "agent_id": "Rep ID",
        "agency_name": "Payee Name",
        "agency_id": "Payee ID",
        "commission_period": "--",
        "commission_amount": "Payment",
        "plan_name": "Plan",
        "is_adjusted": lambda df: df["Prior Plan"] == "no",
        "effective_date": "Effective Date",
        "term_date": "Term Date",
        "description": None,
    },
    
    "Healthfirst": {
        "agent_name": "Producer Name",
        "agent_id": None,
        "agency_name": lambda df: df["Producer Name"].where(
            ~df["Producer Type"].isin(["Broker", "Agent"])
        ),
        "agency_id": None,
        "commission_period": "Period",
        "commission_amount": "Amount",
        "plan_name": "Product",
        "is_adjusted": lambda df: df["Adjustment Description"] != None,
        "effective_date": None,
        "term_date": "Disenrolled Date",
        "description": "Disenrollement Reason",
    },
}
