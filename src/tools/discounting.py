import logging


def register_discounting_tools(mcp: object) -> None:
    @mcp.tool("calculate_straight_discounting")
    def calculate_straight_discounting(
        items: list[dict],
        discount_rate_percentage: float,
    ) -> tuple[float, list[dict]]:
        logging.info(
            "[TOOL_CALL] calculate_straight_discounting | discount_rate_percentage=%s | items=%s",
            discount_rate_percentage,
            items,
        )

        if discount_rate_percentage < 0:
            raise ValueError("discount_rate_percentage must be >= 0")

        if 0 < discount_rate_percentage < 1:
            logging.warning(
                "[TOOL_WARN] discount_rate_percentage looks decimal (%s), converting to percent",
                discount_rate_percentage,
            )
            discount_rate_percentage *= 100

        rows: list[dict] = []
        total_pv = 0.0

        for idx, item in enumerate(items):
            amount = item.get("amount")
            days = item.get("days_to_maturity", item.get("days"))

            if amount is None:
                raise ValueError(f"items[{idx}].amount is required")
            if days is None:
                raise ValueError(f"items[{idx}].days_to_maturity (or days) is required")
            if days < 0:
                raise ValueError(f"items[{idx}].days_to_maturity must be >= 0")

            factor = 1 - (discount_rate_percentage / 100) * (days / 360)
            pv = amount * factor

            logging.info(
                "[TOOL_ITEM] calculate_straight_discounting | idx=%s | amount=%s | days=%s | factor=%s | pv=%s",
                idx,
                amount,
                days,
                factor,
                pv,
            )

            rows.append(
                {
                    "nominal_value": amount,
                    "days": days,
                    "factor": float(factor),
                    "pv": float(pv),
                }
            )
            total_pv += pv

        logging.info(
            "[TOOL_RESULT] calculate_straight_discounting | total_pv=%s | rows_count=%s",
            total_pv,
            len(rows),
        )
        return float(total_pv), rows


    @mcp.tool("calculate_discount_to_yield")
    def calculate_discount_to_yield(
        items: list[dict],
        yield_rate: float,
    ) -> tuple[float, list[dict]]:
        logging.info(
            "[TOOL_CALL] calculate_discount_to_yield | yield_rate=%s | items=%s",
            yield_rate,
            items,
        )

        if yield_rate < 0:
            raise ValueError("yield_rate must be >= 0")

        if 0 < yield_rate < 1:
            logging.warning(
                "[TOOL_WARN] yield_rate looks decimal (%s), converting to percent",
                yield_rate,
            )
            yield_rate *= 100

        rows: list[dict] = []
        total_pv = 0.0

        for idx, item in enumerate(items):
            amount = item.get("amount")
            days = item.get("days_to_maturity", item.get("days"))

            if amount is None:
                raise ValueError(f"items[{idx}].amount is required")
            if days is None:
                raise ValueError(f"items[{idx}].days_to_maturity (or days) is required")
            if days < 0:
                raise ValueError(f"items[{idx}].days_to_maturity must be >= 0")

            n_years = days // 360
            d_extra = days % 360

            factor = ((1 + (yield_rate / 100)) ** n_years) * (1 + (yield_rate / 100) * (d_extra / 360))
            pv = amount / factor

            logging.info(
                "[TOOL_ITEM] calculate_discount_to_yield | idx=%s | amount=%s | days=%s | full_years=%s | extra_days=%s | factor=%s | pv=%s",
                idx,
                amount,
                days,
                n_years,
                d_extra,
                factor,
                pv,
            )

            rows.append(
                {
                    "nominal_value": amount,
                    "days": days,
                    "full_years": n_years,
                    "extra_days": d_extra,
                    "factor": float(factor),
                    "pv": float(pv),
                }
            )
            total_pv += pv

        logging.info(
            "[TOOL_RESULT] calculate_discount_to_yield | total_pv=%s | rows_count=%s",
            total_pv,
            len(rows),
        )
        return float(total_pv), rows