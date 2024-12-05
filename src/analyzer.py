import pandas as pd
from typing import Dict
from .constants import TARGET_PERIOD, TOP_N


class CommissionAnalyzer:
    """
    This class analyzes commission data, focusing on identifying top-earning agents
    and generating summaries for specific periods.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        
        
    # Identify the top N earning agents for a given period.
    def calculate_top_earning_agents(
        self, top_n: int = TOP_N, target_period: str = TARGET_PERIOD
    ) -> pd.DataFrame:
        
        # Filter data for the specified period
        filtered_data = self.data[
            self.data["commission_period"] == target_period
            ].copy()
        # Ensure commission amounts are numeric
        filtered_data["commission_amount"] = pd.to_numeric(
             filtered_data["commission_amount"], errors="coerce"
             ).fillna(0.0)

        # Aggregate commission data by agent
        agent_totals = (
              filtered_data.groupby("agent_name")
              .agg(
                   total_commission=("commission_amount", "sum"),
                   carriers=("carrier_name",
                              lambda x: ", ".join(sorted(set(x)))),
                   )
               .reset_index()
              )

        agent_totals = agent_totals.sort_values(
               "total_commission", ascending=False)

        # Add placeholder rows if there are fewer than `top_n` agents
        if len(agent_totals) < top_n:
                missing_rows = top_n - len(agent_totals)
                for _ in range(missing_rows):
                    agent_totals = pd.concat(
                        [
                            agent_totals,
                            pd.DataFrame(
                                {
                                    "agent_name": ["Agent Placeholder"],
                                    "total_commission": [0.0],
                                    "carriers": ["N/A"],
                                }
                            ),
                        ],
                        ignore_index=True,
                    )

        
        return agent_totals.head(top_n)

    # Generate a summary of the commission data for a given period.
    def generate_period_summary(self, commission_period: str = TARGET_PERIOD) -> Dict:
        print(f"Data Review for period {commission_period}:")
        
        # Filter data for the target period
        period_data = self.data[self.data["commission_period"] == commission_period].copy()
        
        # Ensure commission amounts are numeric
        period_data["commission_amount"] = pd.to_numeric(
            period_data["commission_amount"], errors="coerce"
        ).fillna(0.0)
        
        # Compile and return summary statistics
        return {
            "total_commission": f'{period_data["commission_amount"].sum():.2f}',
            "agent_name": period_data["agent_name"].nunique(),
            "agent_id": period_data["agent_id"].nunique(),
            "carriers": sorted(period_data["carrier_name"].unique()),
            "commission_period": commission_period,
        }
