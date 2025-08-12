#!/usr/bin/env python3

"""
Retirement Savings Calculator with Hong Kong Healthcare Costs

This program estimates the monthly savings needed from now until retirement
to maintain a desired lifestyle after retirement, accounting for inflation
both before and during retirement, plus comprehensive healthcare costs.

Now includes Immediate Life Annuity analysis as an alternative to corpus withdrawal strategy.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class HealthcareCoverage(Enum):
    """Healthcare coverage types with their base costs."""
    BASIC = ("basic", 50000)
    MODERATE = ("moderate", 120000)
    COMPREHENSIVE = ("comprehensive", 200000)

    def __init__(self, name: str, base_cost: float):
        self.coverage_name = name
        self.base_cost = base_cost


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


@dataclass
class AnnuityResults:
    """Data class to hold annuity analysis results."""
    annuity_rate: float
    annuity_to_age: int
    annuity_premium_required: float
    level_payment_equivalent: float
    years_covered_by_annuity: int
    uncovered_years: int
    uncovered_corpus_needed: float
    total_needed_hybrid: float
    future_value_current_savings: float
    additional_needed_annuity_only: float
    additional_needed_hybrid: float
    monthly_savings_annuity_only: float
    monthly_savings_hybrid: float
    total_expenses_pv_annuity_rate: float


class RetirementCalculator:
    """Main calculator class for retirement planning analysis."""

    def __init__(self):
        """Initialize the retirement calculator."""
        self.retirement_params: Optional[RetirementParameters] = None
        self.healthcare_params: Optional[HealthcareParameters] = None
        self._first_year_retirement_expense: Optional[float] = None

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

        self._print_expense_sample(expense_breakdown)

    def _print_expense_sample(self, expense_breakdown: Dict[str, List[float]]) -> None:
        """Print sample of expense breakdown."""
        total_expenses = expense_breakdown['total_expenses']
        living_expenses = expense_breakdown['living_expenses']
        healthcare_costs = expense_breakdown['healthcare_costs']

        print(f"\nExpense breakdown by retirement year (sample):")
        print(f"{'Year':<4} {'Age':<3} {'Living':<12} {'Healthcare':<12} {'Total':<12}")
        print("-" * 50)

        # Show first 3 years
        for i in range(min(3, len(total_expenses))):
            age = self.retirement_params.retirement_age + i
            print(f"{i + 1:<4} {age:<3} ${living_expenses[i]:<11,.0f} "
                  f"${healthcare_costs[i]:<11,.0f} ${total_expenses[i]:<11,.0f}")

        # Show last 3 years if more than 6 total
        if len(total_expenses) > 6:
            print("...  ... ...         ...         ...")
            for i in range(max(3, len(total_expenses) - 3), len(total_expenses)):
                age = self.retirement_params.retirement_age + i
                print(f"{i + 1:<4} {age:<3} ${living_expenses[i]:<11,.0f} "
                      f"${healthcare_costs[i]:<11,.0f} ${total_expenses[i]:<11,.0f}")

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

        years_to_retirement = (self.retirement_params.retirement_age -
                               self.retirement_params.current_age)
        months_to_retirement = years_to_retirement * 12
        monthly_return = (1 + self.retirement_params.pre_retirement_return) ** (1 / 12) - 1

        if additional_needed <= 0:
            monthly_savings = 0
        elif monthly_return == 0:
            monthly_savings = additional_needed / months_to_retirement
        else:
            fv_factor = ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
            monthly_savings = additional_needed / fv_factor

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
            years_to_retirement=years_to_retirement,
            years_in_retirement=self.retirement_params.life_expectancy - self.retirement_params.retirement_age,
            current_annual_expense=self.retirement_params.current_annual_expense,
            first_year_retirement_expense=self._first_year_retirement_expense,
            expense_breakdown=expense_breakdown,
            total_healthcare_corpus=total_healthcare_corpus
        )

    def calculate_annuity_analysis(self, annuity_rate: float = 4.5,
                                   annuity_to_age: int = 100) -> AnnuityResults:
        """Calculate immediate life annuity analysis."""
        expense_breakdown = self.get_retirement_expense_breakdown()
        total_expenses = expense_breakdown['total_expenses']
        annuity_rate_decimal = annuity_rate / 100

        self._print_annuity_analysis_header(annuity_rate, annuity_to_age)

        # Calculate required annuity premium
        annuity_premium_pv = sum(
            expense / (1 + annuity_rate_decimal) ** (i + 1)
            for i, expense in enumerate(total_expenses)
        )

        # Calculate level payment and other metrics
        years_for_annuity = min(annuity_to_age - self.retirement_params.retirement_age,
                                len(total_expenses))

        if years_for_annuity > 0:
            total_pv_at_annuity_rate = sum(
                expense / (1 + annuity_rate_decimal) ** (i + 1)
                for i, expense in enumerate(total_expenses)
            )
            pv_annuity_factor = (1 - (1 + annuity_rate_decimal) ** (-years_for_annuity)) / annuity_rate_decimal
            level_payment = total_pv_at_annuity_rate / pv_annuity_factor if pv_annuity_factor > 0 else 0
        else:
            level_payment = 0
            total_pv_at_annuity_rate = 0

        # Handle longevity risk
        uncovered_years = max(0, self.retirement_params.life_expectancy - annuity_to_age)
        uncovered_corpus = self._calculate_uncovered_corpus(total_expenses, years_for_annuity, uncovered_years)

        # Calculate savings requirements
        future_value_current_savings = self.calculate_future_value_of_current_savings()
        total_needed_hybrid = annuity_premium_pv + uncovered_corpus

        monthly_savings_annuity = self._calculate_monthly_savings_needed(
            annuity_premium_pv - future_value_current_savings
        )
        monthly_savings_hybrid = self._calculate_monthly_savings_needed(
            total_needed_hybrid - future_value_current_savings
        )

        return AnnuityResults(
            annuity_rate=annuity_rate,
            annuity_to_age=annuity_to_age,
            annuity_premium_required=annuity_premium_pv,
            level_payment_equivalent=level_payment,
            years_covered_by_annuity=years_for_annuity,
            uncovered_years=uncovered_years,
            uncovered_corpus_needed=uncovered_corpus,
            total_needed_hybrid=total_needed_hybrid,
            future_value_current_savings=future_value_current_savings,
            additional_needed_annuity_only=annuity_premium_pv - future_value_current_savings,
            additional_needed_hybrid=total_needed_hybrid - future_value_current_savings,
            monthly_savings_annuity_only=monthly_savings_annuity,
            monthly_savings_hybrid=monthly_savings_hybrid,
            total_expenses_pv_annuity_rate=total_pv_at_annuity_rate
        )

    def _print_annuity_analysis_header(self, annuity_rate: float, annuity_to_age: int) -> None:
        """Print annuity analysis header information."""
        print(f"\n💰 IMMEDIATE LIFE ANNUITY ANALYSIS:")
        print(f"Annuity rate offered: {annuity_rate:.1%}")
        print(f"Annuity guaranteed to age: {annuity_to_age}")
        print(f"Your life expectancy: {self.retirement_params.life_expectancy}")

    def _calculate_uncovered_corpus(self, total_expenses: List[float],
                                    years_covered: int, uncovered_years: int) -> float:
        """Calculate corpus needed for uncovered years beyond annuity."""
        if uncovered_years <= 0:
            return 0.0

        uncovered_expenses = []
        for year in range(uncovered_years):
            expense_year = years_covered + year
            if expense_year < len(total_expenses):
                uncovered_expenses.append(total_expenses[expense_year])
            else:
                # Extrapolate expenses beyond calculated range
                last_expense = total_expenses[-1]
                extra_years = expense_year - len(total_expenses) + 1
                projected_expense = last_expense * (1 + self.retirement_params.inflation_rate) ** extra_years
                uncovered_expenses.append(projected_expense)

        # Calculate present value of uncovered expenses
        return sum(
            expense / (1 + self.retirement_params.post_retirement_return) ** (i + 1)
            for i, expense in enumerate(uncovered_expenses)
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


class RetirementVisualizer:
    """Class for creating retirement planning visualizations."""

    def __init__(self, calculator: RetirementCalculator):
        self.calculator = calculator

    def create_comprehensive_visualization(self, results: CalculationResults,
                                           annuity_results: Optional[AnnuityResults] = None) -> None:
        """Create comprehensive visualization of retirement planning."""
        fig_size = (16, 18) if annuity_results else (16, 12)
        subplot_config = (3, 2) if annuity_results else (2, 2)

        fig, axes = plt.subplots(*subplot_config, figsize=fig_size)
        axes = axes.flatten() if annuity_results else [[axes[0][0], axes[0][1]], [axes[1][0], axes[1][1]]]

        self._plot_savings_accumulation(axes[0] if annuity_results else axes[0][0], results, annuity_results)
        self._plot_expense_breakdown(axes[1] if annuity_results else axes[0][1], results, annuity_results)
        self._plot_retirement_balance(axes[2] if annuity_results else axes[1][0], results)
        self._plot_healthcare_costs(axes[3] if annuity_results else axes[1][1], results)

        if annuity_results:
            self._plot_strategy_comparison(axes[4], results, annuity_results)
            self._plot_risk_comparison(axes[5], results, annuity_results)

        plt.tight_layout()
        filename = 'comprehensive_retirement_analysis_with_annuity.png' if annuity_results else 'comprehensive_retirement_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()

    def _plot_savings_accumulation(self, ax, results: CalculationResults,
                                   annuity_results: Optional[AnnuityResults]) -> None:
        """Plot savings accumulation until retirement."""
        years = np.arange(0, results.years_to_retirement + 1)
        current_balance = self.calculator.retirement_params.current_savings

        # Calculate corpus strategy savings
        savings_balance = self._calculate_savings_projection(years, results.monthly_savings_required, current_balance)

        ages = years + self.calculator.retirement_params.current_age
        ax.plot(ages, savings_balance, 'b-', linewidth=2, marker='o', markersize=4, label='Corpus Strategy')
        ax.axhline(y=results.corpus_needed, color='r', linestyle='--',
                   label=f'Target: ${results.corpus_needed / 1000000:.1f}M')

        # Add annuity strategy if provided
        if annuity_results:
            annuity_savings = self._calculate_savings_projection(years, annuity_results.monthly_savings_hybrid,
                                                                 current_balance)
            ax.plot(ages, annuity_savings, 'g--', linewidth=2, marker='s', markersize=4, label='Annuity Strategy')
            ax.axhline(y=annuity_results.total_needed_hybrid, color='orange', linestyle=':',
                       label=f'Annuity Target: ${annuity_results.total_needed_hybrid / 1000000:.1f}M')

        ax.set_xlabel('Age')
        ax.set_ylabel('Savings Balance ($)')
        ax.set_title('Savings Growth Until Retirement')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x / 1000000:.1f}M'))

    def _calculate_savings_projection(self, years: np.ndarray, monthly_savings: float,
                                      initial_balance: float) -> List[float]:
        """Calculate savings projection over years."""
        savings_balance = []
        current_balance = initial_balance

        for year in years:
            if year == 0:
                savings_balance.append(current_balance)
            else:
                annual_savings = monthly_savings * 12
                current_balance = ((current_balance + annual_savings) *
                                   (1 + self.calculator.retirement_params.pre_retirement_return))
                savings_balance.append(current_balance)

        return savings_balance

    def _plot_expense_breakdown(self, ax, results: CalculationResults,
                                annuity_results: Optional[AnnuityResults]) -> None:
        """Plot expense breakdown over retirement."""
        expense_breakdown = results.expense_breakdown

        # Ensure consistent array lengths
        min_length = min(len(expense_breakdown['living_expenses']),
                         len(expense_breakdown['healthcare_costs']),
                         len(expense_breakdown['total_expenses']))

        living_expenses = expense_breakdown['living_expenses'][:min_length]
        healthcare_costs = expense_breakdown['healthcare_costs'][:min_length]
        total_expenses = expense_breakdown['total_expenses'][:min_length]

        ages = list(range(self.calculator.retirement_params.retirement_age,
                          self.calculator.retirement_params.retirement_age + min_length))

        ax.plot(ages, living_expenses, 'b-', linewidth=2, label='Living Expenses', marker='o', markersize=3)
        ax.plot(ages, healthcare_costs, 'r-', linewidth=2, label='Healthcare Costs', marker='s', markersize=3)
        ax.plot(ages, total_expenses, 'purple', linewidth=3, label='Total Expenses', marker='^', markersize=4)

        if annuity_results and annuity_results.level_payment_equivalent > 0:
            ax.axhline(y=annuity_results.level_payment_equivalent, color='green', linestyle='--',
                       label=f'Annuity Payment: ${annuity_results.level_payment_equivalent:,.0f}')

        ax.set_xlabel('Age')
        ax.set_ylabel('Annual Expenses ($)')
        ax.set_title(
            f'Retirement Expenses Breakdown ({self.calculator.healthcare_params.coverage_type.title()} Healthcare)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x / 1000:.0f}K'))

    def _plot_retirement_balance(self, ax, results: CalculationResults) -> None:
        """Plot retirement balance over time."""
        expense_breakdown = results.expense_breakdown
        min_length = min(len(expense_breakdown['living_expenses']),
                         len(expense_breakdown['total_expenses']))

        ages = list(range(self.calculator.retirement_params.retirement_age,
                          self.calculator.retirement_params.retirement_age + min_length))
        total_expenses = expense_breakdown['total_expenses'][:min_length]

        balance = results.corpus_needed
        balances = [balance]

        for expense in total_expenses:
            balance = (balance - expense) * (1 + self.calculator.retirement_params.post_retirement_return)
            balances.append(balance)

        # Ensure consistent lengths
        min_plot_length = min(len(ages), len(balances))
        ages = ages[:min_plot_length]
        balances = balances[:min_plot_length]

        ax.plot(ages, balances, 'g-', linewidth=2, marker='s', markersize=4, label='Corpus Balance')
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Depletion Point')
        ax.set_xlabel('Age')
        ax.set_ylabel('Balance ($)')
        ax.set_title('Retirement Balance Over Time (Including Healthcare)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x / 1000000:.1f}M'))

    def _plot_healthcare_costs(self, ax, results: CalculationResults) -> None:
        """Plot healthcare cost progression."""
        healthcare_costs = results.expense_breakdown['healthcare_costs']
        ages = list(range(self.calculator.retirement_params.retirement_age,
                          self.calculator.retirement_params.retirement_age + len(healthcare_costs)))

        ax.plot(ages, healthcare_costs, 'red', linewidth=3, marker='o', markersize=4,
                label=f'{self.calculator.healthcare_params.coverage_type.title()} Coverage')

        # Add age milestone annotations
        age_milestones = [65, 70, 75, 80, 85]
        for age in age_milestones:
            if (age <= self.calculator.retirement_params.life_expectancy and
                    age >= self.calculator.retirement_params.retirement_age and age in ages):
                idx = ages.index(age)
                if idx < len(healthcare_costs):
                    ax.annotate(f'Age {age}\n${healthcare_costs[idx]:,.0f}',
                                xy=(age, healthcare_costs[idx]), xytext=(10, 10), textcoords='offset points',
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7), fontsize=8)

        ax.set_xlabel('Age')
        ax.set_ylabel('Annual Healthcare Cost ($)')
        ax.set_title(f'Healthcare Cost Progression (Inflation: {self.calculator.healthcare_params.inflation_rate:.1%})')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x / 1000:.0f}K'))

    def _plot_strategy_comparison(self, ax, results: CalculationResults, annuity_results: AnnuityResults) -> None:
        """Plot strategy comparison for monthly savings."""
        strategies = ['Corpus\nWithdrawal', 'Annuity\n(Hybrid)']
        monthly_savings = [results.monthly_savings_required, annuity_results.monthly_savings_hybrid]

        colors = ['blue', 'green']
        bars = ax.bar(strategies, monthly_savings, color=colors, alpha=0.7)

        for bar, value in zip(bars, monthly_savings):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + max(monthly_savings) * 0.01,
                    f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel('Monthly Savings Required ($)')
        ax.set_title('Strategy Comparison: Monthly Savings Required')
        ax.grid(True, alpha=0.3, axis='y')

    def _plot_risk_comparison(self, ax, results: CalculationResults, annuity_results: AnnuityResults) -> None:
        """Plot risk profile comparison."""
        risk_categories = ['Longevity\nRisk', 'Market\nRisk', 'Inflation\nRisk', 'Healthcare\nRisk']
        corpus_risks = [8, 7, 6, 8]
        annuity_risks = [3, 4, 8, 6]

        x = np.arange(len(risk_categories))
        width = 0.35

        ax.bar(x - width / 2, corpus_risks, width, label='Corpus Strategy', color='blue', alpha=0.7)
        ax.bar(x + width / 2, annuity_risks, width, label='Annuity Strategy', color='green', alpha=0.7)

        ax.set_ylabel('Risk Level (1-10)')
        ax.set_title('Risk Profile Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(risk_categories)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, 10)


class RetirementReporter:
    """Class for generating retirement planning reports."""

    def __init__(self, calculator: RetirementCalculator):
        self.calculator = calculator

    def print_comprehensive_summary(self, results: CalculationResults,
                                    annuity_results: Optional[AnnuityResults] = None) -> None:
        """Print comprehensive retirement analysis summary."""
        self._print_header()
        self._print_input_parameters()
        self._print_healthcare_analysis(results)
        self._print_inflation_analysis(results)
        self._print_corpus_strategy_results(results)

        if annuity_results:
            self._print_annuity_strategy_results(annuity_results)
            self._print_strategy_comparison(results, annuity_results)
            self._print_risk_analysis()

        self._print_healthcare_recommendations(results)

    def _print_header(self) -> None:
        """Print report header."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE RETIREMENT SAVINGS ANALYSIS (Hong Kong)")
        print("=" * 80)

    def _print_input_parameters(self) -> None:
        """Print input parameters section."""
        params = self.calculator.retirement_params
        healthcare = self.calculator.healthcare_params

        print("\n📋 INPUT PARAMETERS:")
        print(f"Current Age: {params.current_age}")
        print(f"Retirement Age: {params.retirement_age}")
        print(f"Life Expectancy: {params.life_expectancy}")
        print(f"Current Savings: ${params.current_savings:,.2f}")
        print(f"Current Annual Expenses (today): ${params.current_annual_expense:,.2f}")
        print(f"Expected General Inflation Rate: {params.inflation_rate:.1%}")
        print(f"Expected Healthcare Inflation Rate: {healthcare.inflation_rate:.1%}")
        print(f"Expected Return Before Retirement: {params.pre_retirement_return:.1%}")
        print(f"Expected Return After Retirement: {params.post_retirement_return:.1%}")

    def _print_healthcare_analysis(self, results: CalculationResults) -> None:
        """Print healthcare analysis section."""
        healthcare = self.calculator.healthcare_params
        healthcare_costs = results.expense_breakdown['healthcare_costs']

        print(f"\n🏥 HEALTHCARE PARAMETERS:")
        print(f"Healthcare Coverage Type: {healthcare.coverage_type.title()}")
        print(f"Base Annual Healthcare Cost (at retirement): ${healthcare.base_cost:,.2f}")
        print(f"First Year Healthcare Cost: ${healthcare_costs[0]:,.2f}")
        print(f"Final Year Healthcare Cost: ${healthcare_costs[-1]:,.2f}")
        print(f"Total Healthcare Corpus Needed: ${results.total_healthcare_corpus:,.2f}")
        print(f"Healthcare as % of Total Corpus: {results.total_healthcare_corpus / results.corpus_needed:.1%}")

    def _print_inflation_analysis(self, results: CalculationResults) -> None:
        """Print inflation impact analysis."""
        params = self.calculator.retirement_params
        healthcare = self.calculator.healthcare_params
        healthcare_costs = results.expense_breakdown['healthcare_costs']
        total_expenses = results.expense_breakdown['total_expenses']

        print("\n📈 INFLATION IMPACT ANALYSIS:")
        print(f"Years until retirement: {results.years_to_retirement}")
        print(f"Years in retirement: {results.years_in_retirement}")
        print(f"Current annual expenses: ${params.current_annual_expense:,.2f}")
        print(f"First year retirement expenses (total): ${total_expenses[0]:,.2f}")
        print(f"Final year retirement expenses (total): ${total_expenses[-1]:,.2f}")

        healthcare_inflation_total = (healthcare_costs[-1] / healthcare_costs[0] - 1) * 100
        print(f"\nHealthcare cost increase during retirement: +{healthcare_inflation_total:.1f}%")

        # Real return analysis
        real_pre_return = (1 + params.pre_retirement_return) / (1 + params.inflation_rate) - 1
        real_post_return = (1 + params.post_retirement_return) / (1 + params.inflation_rate) - 1
        healthcare_real_return = (1 + params.post_retirement_return) / (1 + healthcare.inflation_rate) - 1

        print(f"\n💰 REAL RETURNS (above inflation):")
        print(f"Real return before retirement: {real_pre_return:.1%}")
        print(f"Real return after retirement (vs general inflation): {real_post_return:.1%}")
        print(f"Real return vs healthcare inflation: {healthcare_real_return:.1%}")

    def _print_corpus_strategy_results(self, results: CalculationResults) -> None:
        """Print corpus withdrawal strategy results."""
        print(f"\n🎯 CORPUS WITHDRAWAL STRATEGY:")
        print(f"Total corpus needed at retirement: ${results.corpus_needed:,.2f}")
        print(f"  - Living expenses corpus: ${results.corpus_needed - results.total_healthcare_corpus:,.2f}")
        print(f"  - Healthcare corpus: ${results.total_healthcare_corpus:,.2f}")
        print(f"Future value of current savings: ${results.future_value_current_savings:,.2f}")
        print(f"Additional amount needed: ${results.additional_needed:,.2f}")

        if results.monthly_savings_required <= 0:
            print("🎉 Excellent! Your current savings are sufficient for retirement.")
            excess = abs(results.additional_needed)
            print(f"You will have an excess of ${excess:,.2f} at retirement.")
        else:
            print(f"💰 Monthly savings required: ${results.monthly_savings_required:,.2f}")
            annual_savings = results.monthly_savings_required * 12
            print(f"📅 Annual savings required: ${annual_savings:,.2f}")
            savings_rate = (annual_savings / results.current_annual_expense) * 100
            print(f"📊 Savings rate needed: {savings_rate:.1f}% of current expenses")

    def _print_annuity_strategy_results(self, annuity_results: AnnuityResults) -> None:
        """Print annuity strategy results."""
        print(f"\n💰 IMMEDIATE LIFE ANNUITY STRATEGY:")
        print(f"Annuity rate: {annuity_results.annuity_rate:.1%}")
        print(f"Annuity guaranteed to age: {annuity_results.annuity_to_age}")
        print(f"Required annuity premium: ${annuity_results.annuity_premium_required:,.2f}")
        print(f"Equivalent level annual payment: ${annuity_results.level_payment_equivalent:,.2f}")

        if annuity_results.uncovered_years > 0:
            print(f"\n⚠️  HYBRID STRATEGY NEEDED:")
            print(f"Years not covered by annuity: {annuity_results.uncovered_years}")
            print(f"Additional corpus for uncovered years: ${annuity_results.uncovered_corpus_needed:,.2f}")
            print(f"Total needed (annuity + corpus): ${annuity_results.total_needed_hybrid:,.2f}")
            print(f"Monthly savings required: ${annuity_results.monthly_savings_hybrid:,.2f}")
        else:
            print(f"Monthly savings required: ${annuity_results.monthly_savings_annuity_only:,.2f}")

    def _print_strategy_comparison(self, results: CalculationResults, annuity_results: AnnuityResults) -> None:
        """Print strategy comparison analysis."""
        print(f"\n📊 STRATEGY COMPARISON:")
        corpus_monthly = results.monthly_savings_required
        annuity_monthly = annuity_results.monthly_savings_hybrid

        print(f"Corpus Strategy - Monthly savings: ${corpus_monthly:,.2f}")
        print(f"Annuity Strategy - Monthly savings: ${annuity_monthly:,.2f}")

        if annuity_monthly < corpus_monthly:
            savings_difference = corpus_monthly - annuity_monthly
            savings_percent = (savings_difference / corpus_monthly) * 100
            print(f"💡 Annuity strategy saves: ${savings_difference:,.2f}/month ({savings_percent:.1f}%)")
        elif annuity_monthly > corpus_monthly:
            extra_cost = annuity_monthly - corpus_monthly
            extra_percent = (extra_cost / corpus_monthly) * 100
            print(f"⚠️  Annuity strategy costs: ${extra_cost:,.2f}/month extra ({extra_percent:.1f}%)")
        else:
            print("💡 Both strategies require similar monthly savings")

    def _print_risk_analysis(self) -> None:
        """Print risk analysis for both strategies."""
        print(f"\n🎯 RISK CONSIDERATIONS:")
        print("Corpus Strategy:")
        print("  ✅ Full control over investments")
        print("  ✅ Potential for higher returns")
        print("  ⚠️  Market risk during retirement")
        print("  ⚠️  Longevity risk (money may run out)")

        print("\nAnnuity Strategy:")
        print("  ✅ Guaranteed income for life (or to specified age)")
        print("  ✅ No market risk during retirement")
        print("  ✅ Longevity protection")
        print("  ⚠️  Lower potential returns")
        print("  ⚠️  Inflation risk (fixed payments)")
        print("  ⚠️  Insurance company credit risk")

    def _print_healthcare_recommendations(self, results: CalculationResults) -> None:
        """Print healthcare planning recommendations."""
        healthcare = self.calculator.healthcare_params

        print(f"\n🏥 HEALTHCARE PLANNING RECOMMENDATIONS:")
        if healthcare.coverage_type == "basic":
            print("⚠️  Consider upgrading to comprehensive coverage for better protection")
        print(
            f"💊 Budget {results.total_healthcare_corpus / results.corpus_needed:.0%} of your retirement corpus for healthcare")
        print(
            f"🩺 Healthcare costs will grow {healthcare.inflation_rate:.1%} annually vs {self.calculator.retirement_params.inflation_rate:.1%} general inflation")


def get_user_input() -> Tuple[RetirementParameters, HealthcareParameters, str, Optional[float]]:
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
    print("Enter your CURRENT annual expenses - inflation will be calculated automatically.")

    # Get user input
    retirement_params, coverage_type, healthcare_inflation, base_healthcare_cost = get_user_input()

    # Initialize calculator
    calc = RetirementCalculator()
    calc.set_retirement_parameters(retirement_params)
    calc.set_healthcare_parameters(base_healthcare_cost, healthcare_inflation, coverage_type)

    # Calculate results
    results = calc.calculate_monthly_savings_needed()

    # Optional annuity analysis
    annuity_results = None
    if input("\nAnalyze Immediate Life Annuity strategy? [default: n] (y/n): ").lower().startswith('y'):
        annuity_rate = float(input("Enter annuity rate offered by insurer [default: 4.5%]: ") or 4.5)
        annuity_to_age = int(input("Enter age until annuity is guaranteed [default: 100]: ") or 100)
        annuity_results = calc.calculate_annuity_analysis(annuity_rate, annuity_to_age)

    # Generate reports
    reporter = RetirementReporter(calc)
    reporter.print_comprehensive_summary(results, annuity_results)

    # Optional visualizations
    if input("\nShow comprehensive charts? [default: n] (y/n): ").lower().startswith('y'):
        visualizer = RetirementVisualizer(calc)
        visualizer.create_comprehensive_visualization(results, annuity_results)


if __name__ == "__main__":
    main()