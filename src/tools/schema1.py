import logging


def register_schema1_tools(mcp: object) -> None:
    @mcp.tool("generate_schema1_schedule")
    def generate_schema1_schedule(
        principal: float,   # P
        rate_i: float,        # i (за період, у відсотках або десятковому вигляді)
        periods: int,       # n
        round_to: int = 6,  
    ) -> dict:
        logging.info(
            "[TOOL_CALL] generate_schema1_schedule | principal=%s | rate_i=%s | periods=%s | round_to=%s",
            principal, rate_i, periods,round_to,
        )

        if principal <= 0:
            raise ValueError("principal must be > 0")
        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_i < 0:
            raise ValueError("rate i must be >= 0")

        rate_decimal = rate_i / 100 if rate_i > 1 else rate_i

        principal_payment = principal / periods
        rows: list[dict] = []

        total_interest = 0.0
        total_principal = 0.0
        total_nominal = 0.0

        for t in range(1, periods + 1):
            interest_payment = principal * rate_decimal * (1 - (t - 1) / periods)
            nominal_value = principal_payment + interest_payment

            row = {
                "bill_number": t,
                "interest_payment": round(interest_payment, round_to),
                "principal_payment": round(principal_payment, round_to),
                "nominal_value": round(nominal_value, round_to),
            }
            rows.append(row)

            total_interest += interest_payment
            total_principal += principal_payment
            total_nominal += nominal_value

            logging.info(
                "[TOOL_ITEM] generate_schema1_schedule | t=%s | interest=%s | principal=%s | nominal=%s",
                t,
                interest_payment,
                principal_payment,
                nominal_value,
            )

        result = {
            "input": {
                "principal": principal,
                "rate_decimal": rate_decimal,
                "periods": periods,
            },
            "rows": rows,
            "totals": {
                "interest_payment": round(total_interest, round_to),
                "principal_payment": round(total_principal, round_to),
                "nominal_value": round(total_nominal, round_to),
            },
        }

        logging.info(
            "[TOOL_RESULT] generate_schema1_schedule | totals=%s | rows_count=%s",
            result["totals"],
            len(rows),
        )
        return result

    
    @mcp.tool("calculate_correction_factor_z1")
    def calculate_correction_factor_z1(
        periods: int,
        rate_i: float,
        rate_d: float,
        round_to: int = 6,
    ) -> dict:
        logging.info(
            "[TOOL_CALL] calculate_correction_factor_z1 | periods=%s | rate_i=%s | rate_d=%s | round_to=%s",
            periods, rate_i, rate_d, round_to,
        )

        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_i < 0:
            raise ValueError("rate_i must be >= 0")
        if rate_d < 0:
            raise ValueError("rate_d must be >= 0")

        i = rate_i / 100 if rate_i > 1 else rate_i
        d = rate_d / 100 if rate_d > 1 else rate_d
        n = periods

        z1 = 1 + ((n+1)/2) * (i - d - d*i*((n+2)/3))

        result = {
            "periods": n,
            "rate_i": i,
            "rate_d": d,
            "z1": round(z1, round_to),
        }

        logging.info("[TOOL_RESULT] calculate_correction_factor_z1 | result=%s", result)
        return result


    @mcp.tool("generate_schema1_schedule_with_z1")
    def generate_schema1_schedule_with_z1(
        principal: float,
        rate_i: float,
        periods: int,
        z1: float,
        round_to: int = 6,
    ) -> dict:
        logging.info("[TOOL_CALL] generate_schema1_schedule_with_z1 | principal=%s | rate_i=%s |periods=%s | z1=%s | round_to=%s",
         principal, rate_i, periods, z1, round_to,
        )

        if principal <=0:
            raise ValueError("principal must be > 0")
        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_i < 0:
            raise ValueError("rate_i must be > 0")
        if z1 <= 0:
            raise ValueError("z1 must be > 0")

        i = rate_i / 100 if rate_i > 1 else rate_i
        principal_payment_base = principal / periods
        correction_factor = 1 / z1
        rows: list[dict] = []

        total_i_adjusted = total_p_adjusted = total_n_adjusted = 0.0

        for t in range(1, periods + 1):
            interest_base = principal * i * (1 - (t - 1) / periods)
            principal_base = principal_payment_base
            nominal_base = principal_base + interest_base

            interest_adjusted = interest_base * correction_factor
            principal_adjested = principal_base * correction_factor
            nominal_adjested = nominal_base * correction_factor
        
            rows.append(
                {
                    "bill_number": t,
                    "interest_payment": round(interest_adjusted, round_to),
                    "principal_payment": round(principal_adjested, round_to),
                    "nominal_value": round(nominal_adjested, round_to),
                }
            )

            total_i_adjusted += interest_adjusted
            total_p_adjusted += principal_adjested
            total_n_adjusted += nominal_adjested

        result = {
            "input": {
                "principal": principal,
                "rate_i_decimal": i,
                "periods": periods,
                "z1": round(z1, round_to),
            },
            "rows": rows,
            "totals": {
                "interest_payment": round(total_i_adjusted, round_to),
                "principal_payment": round(total_p_adjusted, round_to),
                "nominal_value": round(total_n_adjusted, round_to),
            },
        }

        logging.info(
            "[TOOL_RESULT] generate_schema1_schedule_with_z1 | totals=%s | rows_count=%s",
            result["totals"],
            len(rows),
        )
        return result


    @mcp.tool("calculate_correction_rate_i1")
    def calculate_correction_rate_i1(
        periods: int,
        rate_d: float,
        round_to: int = 6,
   ) -> dict:
        logging.info(
            "[TOOL_CALL] calculate_correction_rate_i1 | periods=%s | rate_d=%s | round_to=%s",
            periods, rate_d, round_to,
        )

        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_d < 0:
            raise ValueError("rate d must be > 0")

        d = rate_d / 100 if rate_d > 1 else rate_d
        n = periods

        i = d/(1-((n+2)*d)/3)

        result = {
            "periods": periods,
            "rate_d": d,
            "rate_i": round(i,round_to),
        }

        logging.info("[TOOL_RESULT] calculate_correction_rate_i1 | result=%s", result)
        return result

    
    @mcp.tool("calculate_current_total_importer_costs_a1")
    def calculate_current_total_importer_costs_a1(
        principal: float, # P
        rate_i: float, # i
        rate_j: float, 
        periods: int,
        z1: float,
        duration_years: int, # t
        round_to: int = 6,
    ) -> dict:
        logging.info("[TOOL_CALL] calculate_current_total_importer_costs_a1 | principal=%s |  rate_i=%s | rate_j=%s | periods=%s | z1=%s | duration_years=%s | round_to=%s",
        principal, rate_i, rate_j, periods, z1, duration_years, round_to,

       )

        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_i < 0:
            raise ValueError("rate i must be > 0")
        if rate_j < 0:
            raise ValueError("rate j must be > 0")
        if duration_years <0:
            raise ValueError("duration of years must be > 0")

        i = rate_i / 100 if rate_i > 1 else rate_i
        j_annual = rate_j / 100 if rate_j > 1 else rate_j
        n = periods

        if duration_years <= 0 or n % duration_years != 0:
            raise ValueError("duration_years must divide periods evenly")
        
        periods_per_year = n // duration_years
        j_period = (1 + j_annual) ** (1 / periods_per_year) - 1

        total = 0.0
        for k in range(1, n+1):
            numerator_factor = 1 + (n-k+1) * i
            total += numerator_factor / ((1 + j_period) ** k)
        
        a1 = (principal / (n*z1)) * total

        result = {
            "principal": principal,
            "rate_i": i,
            "rate_j": j_period,
            "rate_j_annual": j_annual,
            "periods": n,
            "z1": z1,
            "duration_years": duration_years,
            "periods_per_year": periods_per_year,
            "a1": round(a1, round_to),
        }
        logging.info("[TOOL_RESULT] calculate_current_total_importer_costs_a1 | result=%s", result)
        return result
            


