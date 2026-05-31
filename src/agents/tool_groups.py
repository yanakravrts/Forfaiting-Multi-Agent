from typing import Literal

Route = Literal["discounting", "schema1", "schema2", "evaluation", "clarify"]

TOOL_GROUPS: dict[str, set[str]] = {
    "discounting": {
        "calculate_straight_discounting",
        "calculate_discount_to_yield",
    },
    "schema1": {
        "generate_schema1_schedule",
        "calculate_correction_factor_z1",
        "generate_schema1_schedule_with_z1",
        "calculate_correction_rate_i1",
        "calculate_current_total_importer_costs_a1",
    },
    "schema2": {
        "generate_schema2_schedule",
        "calculate_correction_factor_z2",
        "generate_schema2_schedule_with_z2",
        "calculate_correction_rate_i2",
        "calculate_current_total_importer_costs_a2",
    },
    "evaluation": {
        "count_npv",
        "count_discount_critical",
    },
}
