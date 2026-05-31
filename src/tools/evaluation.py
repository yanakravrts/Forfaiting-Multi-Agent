import logging


def register_evaluation_tools(mcp: object) -> None:
    @mcp.tool("count_npv")
    def count_npv(
        principal: float,
        periods: int,
        rate_d: float,
        rate_j: float,
        round_to: int = 6,
    ) -> dict:
        """NPV of a forfaiting deal.

        principal: total nominal of ALL bills (e.g. 20000), NOT per-bill amount (not 5000).
        periods: count of payment periods (e.g. 4). Already used inside the formula.
        rate_d: discount rate d (% or decimal). rate_j: market rate j (% or decimal).
        """
        logging.info(
           "[TOOL_CALL] count_npv | principal=%s | periods=%s | rate_d=%s | rate_j=%s | round_to=%s",
            principal, periods, rate_d, rate_j, round_to,
        )

        if principal <= 0:
            raise ValueError("principal must be > 0")
        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_d < 0:
            raise ValueError("rate d must be >= 0")
        if rate_j < 0:
            raise ValueError("rate j must be >= 0")

        j_annual = rate_j / 100 if rate_j > 1 else rate_j
        d_annual = rate_d / 100 if rate_d > 1 else rate_d
        n = periods

        # Formula (4.2.1): annual rates d, j enter as semi-annual d/2, j/2
        j = j_annual / 2
        d = d_annual / 2

        numerator = ((1 + j) ** n) - 1
        denominator_a = n * (1 - d * ((1 + n) / 2))
        denominator_b = j * ((1 + j) ** n)

        npv = principal * (1 - numerator / (denominator_a * denominator_b))

        result = {
            "principal": principal,
            "periods": n,
            "rate_d_annual": d_annual,
            "rate_j_annual": j_annual,
            "rate_d_period": d,
            "rate_j_period": j,
            "npv": round(npv, round_to),
        }
        logging.info("[TOOL_RESULT] count_npv | result=%s", result)
        return result


    @mcp.tool("count_discount_critical")
    def count_discount_critical(
        periods: int,
        rate_j: float,
        round_to: int = 6,
    ) -> dict:
        logging.info(
            "[TOOL_CALL] count_discount_critical | periods=%s | rate_j=%s | round_to=%s",
            periods, rate_j, round_to
        )

        if periods <= 0:
            raise ValueError("periods must be > 0")
        if rate_j < 0:
            raise ValueError("rate j must be >= 0")

        j = rate_j / 100 if rate_j > 1 else rate_j
        n = periods

        numerator = ((1 + j)**n) - 1
        denominator = n * j * ((1 + j)**n)

        d_crit = (2/(n+1)) * (1 - (numerator/denominator))

        result = {
            "periods": n,
            "rate_j": j,
            "d_crit": round(d_crit, round_to)
        }
        logging.info("[TOOL_RESULT] count_discount_critical | result=%s", result)
        return result
        


        


