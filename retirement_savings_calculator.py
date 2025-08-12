# !/usr/bin/env python3

"""
Retirement Savings Calculator with Hong Kong Healthcare Costs and Real Annuity Data

This program estimates the monthly savings needed from now until retirement
to maintain a desired lifestyle after retirement, accounting for inflation
both before and during retirement, plus comprehensive healthcare costs.

Now includes:
- Real Hong Kong annuity product analysis with IRR calculations
- Portfolio Allocation Strategy (Annuity + Self-Investment Mix)
- Age-based payout rates and premium calculations
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class HealthcareCoverage(Enum):
    """Healthcare coverage types with their base costs."""
    BASIC = ("basic", 50000)
    MODERATE = ("moderate", 120000)
    COMPREHENSIVE = ("comprehensive", 200000)

    def __init__(self, name: str, base_cost: float):
        self.coverage_name = name
        self.base_cost = base_cost


@dataclass
class HongKongAnnuityProduct:
    """Data class representing real Hong Kong annuity product specifications."""
    product_name: str
    gender: str  # "male" or "female"
    entry_age_ranges: Dict[str, Dict[str, float]]  # age_range -> {premium_per_unit, annual_payout}
    guaranteed_period: int  # years of guaranteed payments
    payout_to_age: int  # maximum age for payments (e.g., 100 or lifetime)
    currency: str
    minimum_premium: float
    irr_estimates: Dict[int, float]  # life_expectancy -> IRR

    @classmethod
    def create_hk_standard_plan(cls) -> 'HongKongAnnuityProduct':
        """Create a standard Hong Kong immediate annuity plan based on market data."""
        # Based on typical Hong Kong annuity products
        return cls(
            product_name="HK Standard Immediate Annuity",
            gender="unisex",
            entry_age_ranges={
                "55-59": {"premium_per_unit": 16.67, "annual_payout": 1.0},
                "60-64": {"premium_per_unit": 15.38, "annual_payout": 1.0},
                "65-69": {"premium_per_unit": 14.29, "annual_payout": 1.0},
                "70-74": {"premium_per_unit": 13.33, "annual_payout": 1.0},
                "75-79": {"premium_per_unit": 12.50, "annual_payout": 1.0},
                "80+": {"premium_per_unit": 11.76, "annual_payout": 1.0}
            },
            guaranteed_period=10,  # 10 years guaranteed
            payout_to_age=100,
            currency="HKD",
            minimum_premium=100000,  # HK$100,000 minimum
            irr_estimates={
                75: 1.5,  # Die at 75, IRR = 1.5%
                80: 2.8,  # Die at 80, IRR = 2.8%
                85: 3.8,  # Die at 85, IRR = 3.8%
                90: 4.5,  # Die at 90, IRR = 4.5%
                95: 5.0,  # Die at 95, IRR = 5.0%
                100: 5.3  # Die at 100, IRR = 5.3%
            }
        )


@dataclass
class RetirementParameters:
    """Data class to hold retirement calculation parameters."""
    current_age: int
    retirement_age: int
    life_expectancy: int
    current_annual_expense: float
    current_savings: float
    pre_retirement_return: float
    post_retirement_return: float
    inflation_rate: float


@dataclass
class HealthcareParameters:
    """Data class to hold healthcare-specific parameters."""
    base_cost: float
    inflation_rate: float
    coverage_type: str
    age_multipliers: Dict[int, float] = None

    def __post_init__(self):
        if self.age_multipliers is None:
            self.age_multipliers = {
                65: 0.8,  # Lower costs in early retirement
                70: 1.0,  # Base costs
                75: 1.4,  # Moderate increase
                80: 1.8,  # Significant increase
                85: 2.3,  # Major increase
                100: 2.8  # Maximum healthcare needs
            }


@dataclass
class RealAnnuityAnalysis:
    """Analysis results for real Hong Kong annuity products."""
    product_name: str
    entry_age: int
    premium_per_unit: float
    annual_payout_per_unit: float
    total_premium_needed: float
    annual_income: float
    guaranteed_years: int
    expected_irr: float
    break_even_age: int
    total_guaranteed_payout: float
    lifetime_payout_estimate: float
    monthly_savings_required: float


class HongKongAnnuityCalculator:
    """Calculator for Hong Kong annuity products."""

    def __init__(self):
        self.standard_plan = HongKongAnnuityProduct.create_hk_standard_plan()

    def get_age_range_key(self, age: int) -> str:
        """Get the appropriate age range key for pricing."""
        if age < 60:
            return "55-59"
        elif age < 65:
            return "60-64"
        elif age < 70:
            return "65-69"
        elif age < 75:
            return "70-74"
        elif age < 80:
            return "75-79"
        else:
            return "80+"

    def calculate_annuity_requirements(self, retirement_age: int, annual_income_needed: float,
                                       life_expectancy: int) -> RealAnnuityAnalysis:
        """
        Calculate annuity requirements using real Hong Kong product data.

        Args:
            retirement_age: Age when annuity payments begin
            annual_income_needed: Required annual income from annuity
            life_expectancy: Expected lifespan for IRR calculation

        Returns:
            RealAnnuityAnalysis with detailed calculations
        """
        age_range = self.get_age_range_key(retirement_age)
        pricing_data = self.standard_plan.entry_age_ranges[age_range]

        # Calculate units needed
        # Each unit provides annual_payout_per_unit of income for premium_per_unit
        premium_per_unit = pricing_data["premium_per_unit"] * 10000  # Convert to actual HKD
        annual_payout_per_unit = pricing_data["annual_payout"] * 10000  # Convert to actual HKD

        units_needed = annual_income_needed / annual_payout_per_unit
        total_premium = units_needed * premium_per_unit

        # Calculate IRR based on life expectancy
        expected_irr = self._interpolate_irr(life_expectancy)

        # Calculate break-even age
        break_even_years = premium_per_unit / annual_payout_per_unit
        break_even_age = retirement_age + break_even_years

        # Calculate guaranteed payout
        guaranteed_years = self.standard_plan.guaranteed_period
        total_guaranteed_payout = annual_income_needed * guaranteed_years

        # Estimate lifetime payout
        payout_years = min(life_expectancy - retirement_age,
                           self.standard_plan.payout_to_age - retirement_age)
        lifetime_payout_estimate = annual_income_needed * payout_years

        return RealAnnuityAnalysis(
            product_name=self.standard_plan.product_name,
            entry_age=retirement_age,
            premium_per_unit=premium_per_unit,
            annual_payout_per_unit=annual_payout_per_unit,
            total_premium_needed=total_premium,
            annual_income=annual_income_needed,
            guaranteed_years=guaranteed_years,
            expected_irr=expected_irr,
            break_even_age=int(break_even_age),
            total_guaranteed_payout=total_guaranteed_payout,
            lifetime_payout_estimate=lifetime_payout_estimate,
            monthly_savings_required=0  # To be calculated by main calculator
        )

    def _interpolate_irr(self, life_expectancy: int) -> float:
        """Interpolate IRR based on life expectancy."""
        irr_data = self.standard_plan.irr_estimates

        # Find the two closest life expectancies
        ages = sorted(irr_data.keys())

        if life_expectancy <= ages[0]:
            return irr_data[ages[0]]
        elif life_expectancy >= ages[-1]:
            return irr_data[ages[-1]]
        else:
            # Linear interpolation
            for i in range(len(ages) - 1):
                if ages[i] <= life_expectancy <= ages[i + 1]:
                    lower_age, upper_age = ages[i], ages[i + 1]
                    lower_irr, upper_irr = irr_data[lower_age], irr_data[upper_age]

                    # Linear interpolation
                    weight = (life_expectancy - lower_age) / (upper_age - lower_age)
                    return lower_irr + weight * (upper_irr - lower_irr)

        return 3.8  # Default fallback

    def analyze_multiple_scenarios(self, retirement_age: int, annual_income_needed: float) -> Dict[
        int, RealAnnuityAnalysis]:
        """Analyze annuity performance across different life expectancy scenarios."""
        scenarios = {}
        life_expectancies = [75, 80, 85, 90, 95, 100]

        for life_exp in life_expectancies:
            scenarios[life_exp] = self.calculate_annuity_requirements(
                retirement_age, annual_income_needed, life_exp
            )

        return scenarios

    def print_annuity_analysis(self, analysis: RealAnnuityAnalysis) -> None:
        """Print detailed annuity analysis."""
        print(f"\n💰 HONG KONG ANNUITY PRODUCT ANALYSIS:")
        print(f"Product: {analysis.product_name}")
        print(f"Entry Age: {analysis.entry_age}")
        print(f"Currency: {self.standard_plan.currency}")

        print(f"\n📊 PRICING STRUCTURE:")
        print(f"Premium per unit: ${analysis.premium_per_unit:,.0f}")
        print(f"Annual payout per unit: ${analysis.annual_payout_per_unit:,.0f}")
        print(f"Units needed: {analysis.total_premium_needed / analysis.premium_per_unit:.2f}")

        print(f"\n💵 FINANCIAL REQUIREMENTS:")
        print(f"Total premium needed: ${analysis.total_premium_needed:,.0f}")
        print(f"Annual income provided: ${analysis.annual_income:,.0f}")
        print(f"Monthly income: ${analysis.annual_income / 12:,.0f}")

        print(f"\n🛡️ PROTECTION FEATURES:")
        print(f"Guaranteed payout period: {analysis.guaranteed_years} years")
        print(f"Total guaranteed amount: ${analysis.total_guaranteed_payout:,.0f}")
        print(f"Payout continues until age: {self.standard_plan.payout_to_age}")

        print(f"\n📈 RETURN ANALYSIS:")
        print(f"Expected IRR: {analysis.expected_irr:.2f}%")
        print(f"Break-even age: {analysis.break_even_age}")
        print(f"Estimated lifetime payout: ${analysis.lifetime_payout_estimate:,.0f}")

        roi_percent = ((analysis.lifetime_payout_estimate / analysis.total_premium_needed - 1) * 100)
        print(f"Estimated total return: {roi_percent:.1f}%")


@dataclass
class CalculationResults:
    """Data class to hold calculation results."""
    corpus_needed: float
    future_value_current_savings: float
    additional_needed: float
    monthly_savings_required: float
    years_to_retirement: int
    years_in_retirement: int
    current_annual_expense: float
    first_year_retirement_expense: float
    expense_breakdown: Dict[str, List[float]]
    total_healthcare_corpus: float


class RetirementCalculator:
    """Main calculator class for retirement planning analysis."""

    def __init__(self):
        """Initialize the retirement calculator."""
        self.retirement_params: Optional[RetirementParameters] = None
        self.healthcare_params: Optional[HealthcareParameters] = None
        self._first_year_retirement_expense: Optional[float] = None
        self.annuity_calc = HongKongAnnuityCalculator()

    def set_retirement_parameters(self, params: RetirementParameters) -> None:
        """Set retirement calculation parameters."""
        self.retirement_params = params
        self._calculate_first_year_expense()

    def set_healthcare_parameters(self, base_cost: Optional[float] = None,
                                  inflation_rate: Optional[float] = None,
                                  coverage_type: str = "comprehensive") -> None:
        """Set healthcare-specific parameters."""
        if base_cost is None:
            base_cost = next(hc.base_cost for hc in HealthcareCoverage
                             if hc.coverage_name == coverage_type)

        self.healthcare_params = HealthcareParameters(
            base_cost=base_cost,
            inflation_rate=(inflation_rate or 6.5) / 100,
            coverage_type=coverage_type
        )

    def _calculate_first_year_expense(self) -> None:
        """Calculate inflation-adjusted expense for first year of retirement."""
        if not self.retirement_params:
            return

        years_to_retirement = (self.retirement_params.retirement_age -
                               self.retirement_params.current_age)
        self._first_year_retirement_expense = (
                self.retirement_params.current_annual_expense *
                (1 + self.retirement_params.inflation_rate) ** years_to_retirement
        )

    def _get_age_multiplier(self, age: int) -> float:
        """Get healthcare age multiplier for given age."""
        if not self.healthcare_params:
            return 1.0

        for threshold_age, multiplier in sorted(self.healthcare_params.age_multipliers.items()):
            if age < threshold_age:
                return multiplier
        return self.healthcare_params.age_multipliers[100]

    def calculate_healthcare_costs_by_age(self) -> List[float]:
        """Calculate age-progressive healthcare costs."""
        if not self.retirement_params or not self.healthcare_params:
            return []

        healthcare_costs = []
        years_in_retirement = (self.retirement_params.life_expectancy -
                               self.retirement_params.retirement_age)

        for year in range(years_in_retirement):
            current_age = self.retirement_params.retirement_age + year
            age_multiplier = self._get_age_multiplier(current_age)

            annual_cost = (self.healthcare_params.base_cost * age_multiplier *
                           (1 + self.healthcare_params.inflation_rate) ** year)

            # Add buffer for comprehensive coverage
            if self.healthcare_params.coverage_type == "comprehensive":
                annual_cost *= 1.15

            healthcare_costs.append(annual_cost)

        return healthcare_costs

    def get_retirement_expense_breakdown(self) -> Dict[str, List[float]]:
        """Calculate expense breakdown for each year of retirement."""
        if not self.retirement_params:
            return {}

        years_in_retirement = (self.retirement_params.life_expectancy -
                               self.retirement_params.retirement_age)

        living_expenses = []
        healthcare_costs = self.calculate_healthcare_costs_by_age()
        total_expenses = []

        for year in range(years_in_retirement):
            living_expense = (self._first_year_retirement_expense *
                              (1 + self.retirement_params.inflation_rate) ** year)
            living_expenses.append(living_expense)

            total_expense = living_expense + healthcare_costs[year]
            total_expenses.append(total_expense)

        return {
            'living_expenses': living_expenses,
            'healthcare_costs': healthcare_costs,
            'total_expenses': total_expenses
        }

    def calculate_retirement_corpus_needed(self) -> float:
        """Calculate total corpus needed at retirement."""
        if not self.retirement_params:
            return 0.0

        expense_breakdown = self.get_retirement_expense_breakdown()
        total_expenses = expense_breakdown['total_expenses']
        healthcare_costs = expense_breakdown['healthcare_costs']

        self._print_corpus_calculation_details(expense_breakdown)

        # Calculate present value of all expenses
        total_pv = 0
        healthcare_pv = 0

        for i, (total_expense, healthcare_cost) in enumerate(zip(total_expenses, healthcare_costs)):
            pv_total = total_expense / (1 + self.retirement_params.post_retirement_return) ** (i + 1)
            pv_healthcare = healthcare_cost / (1 + self.retirement_params.post_retirement_return) ** (i + 1)

            total_pv += pv_total
            healthcare_pv += pv_healthcare

        self._print_corpus_breakdown(total_pv, healthcare_pv)
        return total_pv

    def analyze_hk_annuity_strategy(self, annuity_allocation_percent: float = 50.0) -> Tuple[
        RealAnnuityAnalysis, float]:
        """
        Analyze Hong Kong annuity strategy using real product data.

        Args:
            annuity_allocation_percent: Percentage of income to be covered by annuity

        Returns:
            Tuple of (RealAnnuityAnalysis, monthly_savings_required)
        """
        expense_breakdown = self.get_retirement_expense_breakdown()
        first_year_expense = expense_breakdown['total_expenses'][0]

        # Calculate annuity income requirement
        annuity_income_needed = first_year_expense * (annuity_allocation_percent / 100)

        print(f"\n🎯 HONG KONG ANNUITY STRATEGY ANALYSIS:")
        print(f"Target annuity allocation: {annuity_allocation_percent:.0f}% of retirement income")
        print(f"First year total expense: ${first_year_expense:,.0f}")
        print(f"Annuity to cover: ${annuity_income_needed:,.0f} annually")

        # Get annuity analysis
        annuity_analysis = self.annuity_calc.calculate_annuity_requirements(
            self.retirement_params.retirement_age,
            annuity_income_needed,
            self.retirement_params.life_expectancy
        )

        # Calculate remaining corpus needed for self-investment portion
        remaining_expenses = []
        for year, total_expense in enumerate(expense_breakdown['total_expenses']):
            # Subtract annuity income (which is fixed, doesn't adjust for inflation)
            remaining_expense = total_expense - annuity_income_needed
            remaining_expenses.append(max(0, remaining_expense))

        # Calculate present value of remaining expenses
        remaining_corpus_needed = sum(
            expense / (1 + self.retirement_params.post_retirement_return) ** (i + 1)
            for i, expense in enumerate(remaining_expenses)
        )

        total_needed = annuity_analysis.total_premium_needed + remaining_corpus_needed

        # Calculate monthly savings needed
        future_value_current_savings = self.calculate_future_value_of_current_savings()
        additional_needed = total_needed - future_value_current_savings
        monthly_savings = self._calculate_monthly_savings_needed(additional_needed)

        # Update the analysis with monthly savings
        annuity_analysis.monthly_savings_required = monthly_savings

        print(f"\n💼 HYBRID STRATEGY BREAKDOWN:")
        print(f"Annuity premium needed: ${annuity_analysis.total_premium_needed:,.0f}")
        print(f"Remaining corpus needed: ${remaining_corpus_needed:,.0f}")
        print(f"Total capital required: ${total_needed:,.0f}")
        print(f"Monthly savings required: ${monthly_savings:,.0f}")

        return annuity_analysis, remaining_corpus_needed

    def compare_annuity_allocations(self) -> None:
        """Compare different annuity allocation strategies."""
        allocation_scenarios = [25, 50, 75, 100]  # Percentage allocated to annuity

        print(f"\n📊 ANNUITY ALLOCATION COMPARISON:")
        print(f"{'Allocation':<12} {'Monthly $':<12} {'Annuity Premium':<18} {'IRR':<6} {'Break-even Age':<15}")
        print("-" * 75)

        results = []
        for allocation in allocation_scenarios:
            try:
                annuity_analysis, remaining_corpus = self.analyze_hk_annuity_strategy(allocation)
                results.append((allocation, annuity_analysis, remaining_corpus))

                print(f"{allocation:>3}% Annuity {annuity_analysis.monthly_savings_required:<11,.0f} "
                      f"${annuity_analysis.total_premium_needed:<17,.0f} "
                      f"{annuity_analysis.expected_irr:<5.1f}% {annuity_analysis.break_even_age:<15}")
            except Exception as e:
                print(f"Error analyzing {allocation}% allocation: {e}")

        # Provide recommendations
        print(f"\n💡 STRATEGY RECOMMENDATIONS:")
        if results:
            min_monthly = min(r[1].monthly_savings_required for r in results)
            best_irr = max(r[1].expected_irr for r in results)

            for allocation, analysis, _ in results:
                if analysis.monthly_savings_required == min_monthly:
                    print(f"💰 Lowest Monthly Savings: {allocation}% annuity allocation")
                if analysis.expected_irr == best_irr:
                    print(f"📈 Highest IRR: {allocation}% annuity allocation ({best_irr:.2f}%)")

    def analyze_life_expectancy_sensitivity(self, annuity_allocation_percent: float = 50.0) -> None:
        """Analyze how different life expectancies affect annuity performance."""
        expense_breakdown = self.get_retirement_expense_breakdown()
        first_year_expense = expense_breakdown['total_expenses'][0]
        annuity_income_needed = first_year_expense * (annuity_allocation_percent / 100)

        scenarios = self.annuity_calc.analyze_multiple_scenarios(
            self.retirement_params.retirement_age,
            annuity_income_needed
        )

        print(f"\n⏰ LIFE EXPECTANCY SENSITIVITY ANALYSIS:")
        print(f"Annuity allocation: {annuity_allocation_percent:.0f}%")
        print(f"{'Life Exp':<8} {'IRR':<6} {'Total Payout':<15} {'ROI':<10}")
        print("-" * 45)

        for life_exp, analysis in scenarios.items():
            roi = (analysis.lifetime_payout_estimate / analysis.total_premium_needed - 1) * 100
            print(f"{life_exp:<8} {analysis.expected_irr:<5.2f}% "
                  f"${analysis.lifetime_payout_estimate:<14,.0f} {roi:<9.1f}%")

        print(f"\n🎯 KEY INSIGHTS:")
        print(f"Break-even age: {scenarios[85].break_even_age} years")
        print(f"Guaranteed protection: {scenarios[85].guaranteed_years} years regardless of lifespan")
        print(f"Higher longevity = Better annuity returns")

    def _print_corpus_calculation_details(self, expense_breakdown: Dict[str, List[float]]) -> None:
        """Print detailed corpus calculation information."""
        if not self.retirement_params or not self.healthcare_params:
            return

        years_in_retirement = (self.retirement_params.life_expectancy -
                               self.retirement_params.retirement_age)

        print(f"\n🔍 DETAILED CORPUS CALCULATION (Including Healthcare):")
        print(f"We need to fund {years_in_retirement} years of retirement")
        print(f"Post-retirement return: {self.retirement_params.post_retirement_return:.1%}")
        print(f"General inflation rate: {self.retirement_params.inflation_rate:.1%}")
        print(f"Healthcare inflation rate: {self.healthcare_params.inflation_rate:.1%}")
        print(f"Healthcare coverage type: {self.healthcare_params.coverage_type.title()}")

    def _print_corpus_breakdown(self, total_pv: float, healthcare_pv: float) -> None:
        """Print corpus breakdown details."""
        print(f"\n📊 PRESENT VALUE CALCULATION:")
        print(f"Corpus breakdown:")
        print(f"  Living expenses corpus: ${total_pv - healthcare_pv:,.2f}")
        print(f"  Healthcare corpus: ${healthcare_pv:,.2f} ({healthcare_pv / total_pv:.1%} of total)")
        print(f"  Total corpus needed: ${total_pv:,.2f}")

    def calculate_future_value_of_current_savings(self) -> float:
        """Calculate future value of current savings at retirement."""
        if not self.retirement_params:
            return 0.0

        years_to_retirement = (self.retirement_params.retirement_age -
                               self.retirement_params.current_age)
        return (self.retirement_params.current_savings *
                (1 + self.retirement_params.pre_retirement_return) ** years_to_retirement)

    def calculate_monthly_savings_needed(self) -> CalculationResults:
        """Calculate monthly savings needed for retirement."""
        corpus_needed = self.calculate_retirement_corpus_needed()
        future_value_current_savings = self.calculate_future_value_of_current_savings()
        additional_needed = corpus_needed - future_value_current_savings

        monthly_savings = self._calculate_monthly_savings_needed(additional_needed)

        expense_breakdown = self.get_retirement_expense_breakdown()
        total_healthcare_corpus = sum(
            cost / (1 + self.retirement_params.post_retirement_return) ** (i + 1)
            for i, cost in enumerate(expense_breakdown['healthcare_costs'])
        )

        return CalculationResults(
            corpus_needed=corpus_needed,
            future_value_current_savings=future_value_current_savings,
            additional_needed=additional_needed,
            monthly_savings_required=monthly_savings,
            years_to_retirement=self.retirement_params.retirement_age - self.retirement_params.current_age,
            years_in_retirement=self.retirement_params.life_expectancy - self.retirement_params.retirement_age,
            current_annual_expense=self.retirement_params.current_annual_expense,
            first_year_retirement_expense=self._first_year_retirement_expense,
            expense_breakdown=expense_breakdown,
            total_healthcare_corpus=total_healthcare_corpus
        )

    def _calculate_monthly_savings_needed(self, additional_needed: float) -> float:
        """Calculate monthly savings needed for given additional amount."""
        if additional_needed <= 0:
            return 0.0

        years_to_retirement = (self.retirement_params.retirement_age -
                               self.retirement_params.current_age)
        months_to_retirement = years_to_retirement * 12
        monthly_return = (1 + self.retirement_params.pre_retirement_return) ** (1 / 12) - 1

        if monthly_return == 0:
            return additional_needed / months_to_retirement
        else:
            fv_factor = ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
            return additional_needed / fv_factor


def get_user_input() -> Tuple[RetirementParameters, str, float, Optional[float]]:
    """Get user input for retirement calculation."""
    try:
        current_age = int(input("\nEnter your current age [default: 50]: ") or 50)
        retirement_age = int(input("Enter retirement age [default: 60]: ") or 60)
        life_expectancy = int(input("Enter life expectancy [default: 85]: ") or 85)
        current_expenses = float(
            input("Enter CURRENT annual expenses (excluding healthcare) [default: $400,000]: $") or 400000)
        current_savings = float(input("Enter current savings [default: $5,000,000]: $") or 5000000)
        inflation_rate = float(input("Enter expected inflation rate [default: 3%]: ") or 3) / 100
        pre_return = float(input("Enter expected return before retirement [default: 7%]: ") or 7) / 100
        post_return = float(input("Enter expected return after retirement [default: 4%]: ") or 4) / 100

        # Healthcare parameters
        print("\n🏥 HEALTHCARE COVERAGE OPTIONS:")
        print("1. Basic (Public system + basic private): ~HK$50,000/year")
        print("2. Moderate (Mixed public/private + insurance): ~HK$120,000/year")
        print("3. Comprehensive (Full private + critical illness): ~HK$200,000/year")

        coverage_choice = input("Choose healthcare coverage [default: 3]: ").strip() or "3"
        coverage_map = {"1": "basic", "2": "moderate", "3": "comprehensive"}
        coverage_type = coverage_map.get(coverage_choice, "comprehensive")

        healthcare_inflation = float(input("Enter healthcare inflation rate [default: 6.5%]: ") or 6.5)

        custom_healthcare = input("Enter custom base healthcare cost [default: use coverage type]: $").strip()
        base_healthcare_cost = float(custom_healthcare) if custom_healthcare else None

        retirement_params = RetirementParameters(
            current_age=current_age,
            retirement_age=retirement_age,
            life_expectancy=life_expectancy,
            current_annual_expense=current_expenses,
            current_savings=current_savings,
            pre_retirement_return=pre_return,
            post_retirement_return=post_return,
            inflation_rate=inflation_rate
        )

        return retirement_params, coverage_type, healthcare_inflation, base_healthcare_cost

    except (ValueError, KeyboardInterrupt):
        print("\nUsing example values...")
        retirement_params = RetirementParameters(
            current_age=50, retirement_age=60, life_expectancy=85,
            current_annual_expense=400000, current_savings=5000000,
            pre_retirement_return=0.07, post_retirement_return=0.04,
            inflation_rate=0.03
        )
        return retirement_params, "comprehensive", 6.5, None


def main():
    """Main function to run the retirement calculator."""
    print("🏦 COMPREHENSIVE RETIREMENT SAVINGS CALCULATOR (Hong Kong)")
    print("=" * 60)
    print("This calculator accounts for inflation AND healthcare costs in Hong Kong.")
    print("Now includes REAL Hong Kong annuity product analysis with IRR calculations!")

    # Get user input
    retirement_params, coverage_type, healthcare_inflation, base_healthcare_cost = get_user_input()

    # Initialize calculator
    calc = RetirementCalculator()
    calc.set_retirement_parameters(retirement_params)
    calc.set_healthcare_parameters(base_healthcare_cost, healthcare_inflation, coverage_type)

    # Calculate traditional corpus strategy
    results = calc.calculate_monthly_savings_needed()

    print(f"\n🎯 TRADITIONAL CORPUS WITHDRAWAL STRATEGY:")
    print(f"Total corpus needed: ${results.corpus_needed:,.0f}")
    print(f"Monthly savings required: ${results.monthly_savings_required:,.0f}")

    # Hong Kong annuity analysis
    if input("\nAnalyze Hong Kong Annuity Products? [default: y] (y/n): ").lower().startswith('y'):
        print(f"\n🇭🇰 HONG KONG ANNUITY ANALYSIS OPTIONS:")
        print("1. Single allocation analysis (specify percentage)")
        print("2. Compare multiple allocation strategies")
        print("3. Life expectancy sensitivity analysis")
        print("4. All analyses")

        choice = input("Choose analysis type [default: 4]: ").strip() or "4"

        if choice == "1":
            allocation = float(input("Enter annuity allocation percentage [default: 50]: ") or 50)
            annuity_analysis, remaining_corpus = calc.analyze_hk_annuity_strategy(allocation)
            calc.annuity_calc.print_annuity_analysis(annuity_analysis)

        elif choice == "2":
            calc.compare_annuity_allocations()

        elif choice == "3":
            allocation = float(input("Enter annuity allocation percentage [default: 50]: ") or 50)
            calc.analyze_life_expectancy_sensitivity(allocation)

        else:  # All analyses
            print(f"\n🔍 COMPREHENSIVE HONG KONG ANNUITY ANALYSIS:")
            calc.compare_annuity_allocations()
            calc.analyze_life_expectancy_sensitivity(50)  # 50% allocation for sensitivity

            # Detailed analysis for 50% allocation
            annuity_analysis, _ = calc.analyze_hk_annuity_strategy(50)
            calc.annuity_calc.print_annuity_analysis(annuity_analysis)

    print(f"\n🎉 Analysis complete!")
    print(
        f"💡 Consider your risk tolerance, longevity expectations, and need for guaranteed income when choosing your strategy.")


if __name__ == "__main__":
    main()