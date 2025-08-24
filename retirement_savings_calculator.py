"""
Hybrid Retirement Planning Calculator

This module implements a comprehensive retirement planning system that combines:
1. HKMC Annuity Plan (Hong Kong government-backed annuity)
2. Self-investment strategy

The calculator helps users determine the optimal allocation between guaranteed
annuity income and growth-oriented self-investment to meet retirement goals.

Key Features:
- Gender-specific annuity rates (males: 6.1%, females: 5.6% at age 60)
- Healthcare cost inflation modeling
- Present value calculations for retirement expenses
- Monthly savings requirements calculation
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class HealthcareCoverage:
    """
    Healthcare coverage options with associated costs.

    Defines three tiers of healthcare coverage:
    - BASIC: Lower cost, basic medical coverage
    - MODERATE: Balanced cost and comprehensive coverage
    - COMPREHENSIVE: Higher cost, extensive medical coverage
    """
    BASIC = "Basic"
    MODERATE = "Moderate"
    COMPREHENSIVE = "Comprehensive"

    def __init__(self, coverage_name: str, base_cost: float):
        self.coverage_name = coverage_name
        self.base_cost = base_cost


@dataclass
class RetirementParameters:
    """
    Core parameters for retirement planning calculations.

    Contains all essential inputs needed to model retirement scenarios:
    - Demographics (age, life expectancy)
    - Financial situation (expenses, savings, returns)
    - Economic assumptions (inflation)
    """
    current_age: int  # User's current age
    retirement_age: int  # Planned retirement age (minimum 60 for HKMC annuity)
    life_expectancy: int  # Expected lifespan for payout calculations
    current_annual_expense: float  # Current yearly living expenses
    current_savings: float  # Existing retirement savings
    pre_retirement_return: float  # Expected investment return before retirement (e.g., 0.08 = 8%)
    post_retirement_return: float  # Expected investment return during retirement (e.g., 0.04 = 4%)
    inflation_rate: float  # General inflation rate for expense growth (e.g., 0.03 = 3%)


@dataclass
class HealthcareParameters:
    """
    Parameters for modeling healthcare cost inflation during retirement.

    Healthcare costs typically grow faster than general inflation and increase
    significantly with age due to higher medical needs.
    """
    base_cost: float  # Base annual healthcare cost at retirement
    inflation_rate: float  # Healthcare-specific inflation rate (typically 5%+)
    coverage_type: str  # Type of coverage (Basic/Moderate/Comprehensive)
    age_multipliers: Dict[int, float]  # How healthcare costs multiply by age

    def __post_init__(self):
        """
        Set default age multipliers if not provided.

        Healthcare costs typically increase dramatically with age:
        - Age 65: Baseline (1.0x)
        - Age 80: 2.2x baseline costs
        - Age 95: 4.2x baseline costs
        - Age 100: 5.0x baseline costs
        """
        if not self.age_multipliers:
            self.age_multipliers = {
                65: 1.0,  # Baseline at retirement
                70: 1.3,  # 30% increase - early retirement health issues
                75: 1.7,  # 70% increase - more medical interventions
                80: 2.2,  # 120% increase - chronic conditions become common
                85: 2.8,  # 180% increase - significant care needs
                90: 3.5,  # 250% increase - extensive medical support
                95: 4.2,  # 320% increase - intensive care requirements
                100: 5.0  # 400% increase - maximum care needs
            }


@dataclass
class HongKongAnnuityProduct:
    """
    Data structure representing the HKMC Annuity Plan specifications.

    The HKMC (Hong Kong Mortgage Corporation) Annuity Plan is a government-backed
    immediate annuity product designed for Hong Kong permanent residents aged 60+.

    Key features:
    - Gender-specific pricing (males get higher rates due to shorter life expectancy)
    - Lifelong guaranteed payments
    - 20-year guaranteed period with 105% minimum return guarantee
    - 2024 promotional boost of 25% for first HK$300,000
    """
    product_name: str  # "HKMC Annuity Plan"
    gender: str  # "male" or "female" for rate determination
    entry_age_ranges: Dict[str, Dict[str, float]]  # Age-based pricing structure
    guaranteed_period: int  # Years of guaranteed payments (20 years)
    payout_to_age: int  # Maximum payout age (999 = lifelong)
    currency: str  # "HKD" - Hong Kong Dollars
    minimum_premium: float  # HK$50,000 minimum investment
    maximum_premium: float  # HK$5,000,000 maximum investment
    irr_estimates: Dict[int, float]  # Expected IRR by life expectancy
    promotional_benefits: Dict[str, Any]  # Current promotional offers

    @classmethod
    def create_hk_standard_plan(cls, gender: str = "male") -> 'HongKongAnnuityProduct':
        """
        Create HKMC Annuity Plan with gender-specific rates.

        Pricing structure explanation:
        - premium_per_unit: HK$ needed to generate HK$10,000 annual income
        - Lower numbers = better rates (less premium for same income)
        - Males get better rates due to shorter statistical life expectancy

        Rate examples at age 60:
        - Male: 16.39 units = 6.1% annual payout rate
        - Female: 17.86 units = 5.6% annual payout rate

        Args:
            gender: "male" or "female" for rate calculation

        Returns:
            HongKongAnnuityProduct configured with gender-specific rates
        """
        if gender.lower() == "male":
            # Male rates - higher payouts due to shorter life expectancy
            entry_age_ranges = {
                "60-64": {"premium_per_unit": 16.39, "annual_payout": 1.0},  # 6.1% annual rate
                "65-69": {"premium_per_unit": 15.15, "annual_payout": 1.0},  # 6.6% annual rate
                "70-74": {"premium_per_unit": 14.08, "annual_payout": 1.0},  # 7.1% annual rate
                "75-79": {"premium_per_unit": 13.16, "annual_payout": 1.0},  # 7.6% annual rate
                "80+": {"premium_per_unit": 12.35, "annual_payout": 1.0}  # 8.1% annual rate
            }
        else:  # female rates - lower payouts due to longer life expectancy
            entry_age_ranges = {
                "60-64": {"premium_per_unit": 17.86, "annual_payout": 1.0},  # 5.6% annual rate
                "65-69": {"premium_per_unit": 16.67, "annual_payout": 1.0},  # 6.0% annual rate
                "70-74": {"premium_per_unit": 15.38, "annual_payout": 1.0},  # 6.5% annual rate
                "75-79": {"premium_per_unit": 14.29, "annual_payout": 1.0},  # 7.0% annual rate
                "80+": {"premium_per_unit": 13.33, "annual_payout": 1.0}  # 7.5% annual rate
            }

        return cls(
            product_name="HKMC Annuity Plan",
            gender=gender.lower(),
            entry_age_ranges=entry_age_ranges,
            guaranteed_period=20,  # 20 years guaranteed payments
            payout_to_age=999,  # Lifelong payments (999 = no age limit)
            currency="HKD",
            minimum_premium=50000,  # HK$50,000 minimum
            maximum_premium=5000000,  # HK$5,000,000 maximum
            # IRR estimates based on life expectancy - males get slightly higher IRRs
            irr_estimates={
                75: 2.8 if gender.lower() == "male" else 2.5,  # Die at 75
                80: 4.1 if gender.lower() == "male" else 3.8,  # Die at 80
                85: 5.1 if gender.lower() == "male" else 4.8,  # Die at 85
                90: 5.8 if gender.lower() == "male" else 5.5,  # Die at 90
                95: 6.3 if gender.lower() == "male" else 6.0,  # Die at 95
                100: 6.6 if gender.lower() == "male" else 6.3,  # Die at 100
                105: 6.8 if gender.lower() == "male" else 6.5  # Die at 105
            },
            # 2024 promotional benefits
            promotional_benefits={
                "lifelong_monthly_booster": {
                    "applicable_premium_limit": 300000,  # First HK$300,000 gets boost
                    "boost_percentage": 25  # 25% increase in monthly payments
                }
            }
        )


@dataclass
class AnnuityAnalysis:
    """
    Results from HKMC Annuity Plan analysis.

    Contains all calculated values needed to evaluate the annuity component
    of the hybrid retirement strategy, including costs, benefits, and returns.
    """
    product_name: str  # "HKMC Annuity Plan"
    entry_age: int  # Age when annuity payments begin
    premium_per_unit: float  # HK$ premium per unit of income
    annual_payout_per_unit: float  # Annual income per unit (typically HK$10,000)
    total_premium_needed: float  # Total upfront premium required
    annual_income: float  # Guaranteed annual income from annuity
    guaranteed_years: int  # Years of guaranteed payments (20)
    expected_irr: float  # Expected internal rate of return
    break_even_age: int  # Age when total payouts equal premium
    total_guaranteed_payout: float  # Minimum guaranteed total payout
    lifetime_payout_estimate: float  # Estimated total payout over lifetime
    monthly_savings_required: float  # Monthly savings needed (calculated later)


class HKMCAnnuityCalculator:
    """
    Calculator for HKMC Annuity Plan requirements and analysis.

    This class handles all calculations related to the annuity portion of the
    hybrid retirement strategy, including premium calculations, payout estimates,
    and return analysis.
    """

    def __init__(self, gender: str = "male"):
        """
        Initialize calculator with gender-specific HKMC plan.

        Args:
            gender: "male" or "female" for appropriate rate table
        """
        self.gender = gender.lower()
        self.plan = HongKongAnnuityProduct.create_hk_standard_plan(gender)

    def update_gender(self, gender: str):
        """
        Update gender and recalculate rates.

        Useful when user changes gender selection during planning session.

        Args:
            gender: New gender for rate recalculation
        """
        self.gender = gender.lower()
        self.plan = HongKongAnnuityProduct.create_hk_standard_plan(gender)

    def _get_age_range_key(self, age: int) -> str:
        """
        Map specific age to appropriate age range bracket for pricing.

        HKMC uses age ranges rather than specific ages for rate determination.
        Minimum age is 60 for eligibility.

        Args:
            age: Specific age at retirement

        Returns:
            Age range key (e.g., "60-64", "65-69", etc.)
        """
        if age < 60:
            return "60-64"  # Minimum age requirement
        elif age < 65:
            return "60-64"  # Ages 60-64
        elif age < 70:
            return "65-69"  # Ages 65-69
        elif age < 75:
            return "70-74"  # Ages 70-74
        elif age < 80:
            return "75-79"  # Ages 75-79
        else:
            return "80+"  # Ages 80+

    def _interpolate_irr(self, life_expectancy: int) -> float:
        """
        Calculate expected IRR based on life expectancy using linear interpolation.

        IRR (Internal Rate of Return) depends heavily on how long the annuitant lives:
        - Shorter life = lower IRR (fewer payments received)
        - Longer life = higher IRR (more payments received)

        Args:
            life_expectancy: Expected age at death

        Returns:
            Interpolated IRR percentage (e.g., 4.5 for 4.5%)
        """
        irr_data = self.plan.irr_estimates
        ages = sorted(irr_data.keys())

        # Handle edge cases - use closest available data
        if life_expectancy <= ages[0]:
            return irr_data[ages[0]]
        elif life_expectancy >= ages[-1]:
            return irr_data[ages[-1]]

        # Linear interpolation between two closest data points
        for i in range(len(ages) - 1):
            if ages[i] <= life_expectancy <= ages[i + 1]:
                lower_age, upper_age = ages[i], ages[i + 1]
                lower_irr, upper_irr = irr_data[lower_age], irr_data[upper_age]

                # Calculate interpolation weight
                weight = (life_expectancy - lower_age) / (upper_age - lower_age)
                return lower_irr + weight * (upper_irr - lower_irr)

        return 3.8  # Fallback default IRR

    def calculate_annuity_requirements(self, retirement_age: int, annual_income_needed: float,
                                       life_expectancy: int) -> AnnuityAnalysis:
        """
        Calculate HKMC Annuity Plan requirements for desired income level.

        This is the core calculation that determines:
        1. How much premium is needed for desired annual income
        2. Actual income after promotional benefits and limits
        3. Expected returns and break-even analysis

        Args:
            retirement_age: Age when annuity payments begin (minimum 60)
            annual_income_needed: Desired annual income from annuity
            life_expectancy: Expected lifespan for return calculations

        Returns:
            AnnuityAnalysis with all calculated values
        """
        # Enforce minimum age requirement
        if retirement_age < 60:
            retirement_age = 60  # HKMC minimum eligibility age

        # Get appropriate pricing data for age
        age_range = self._get_age_range_key(retirement_age)
        pricing_data = self.plan.entry_age_ranges[age_range]

        # Calculate premium requirements
        # pricing_data values are per HK$10,000 annual income, so multiply by 10,000
        premium_per_unit = pricing_data["premium_per_unit"] * 10000  # e.g., 163,900 HKD
        annual_payout_per_unit = pricing_data["annual_payout"] * 10000  # 10,000 HKD

        # Calculate how many units needed for desired income
        units_needed = annual_income_needed / annual_payout_per_unit
        base_total_premium = units_needed * premium_per_unit

        # Apply 2024 promotional benefits (25% boost for first HK$300,000)
        promo_limit = self.plan.promotional_benefits["lifelong_monthly_booster"]["applicable_premium_limit"]
        boost_percentage = self.plan.promotional_benefits["lifelong_monthly_booster"]["boost_percentage"]

        total_premium = base_total_premium
        actual_annual_income = annual_income_needed

        # Apply promotional boost if eligible
        if base_total_premium <= promo_limit:
            # Entire premium qualifies for 25% income boost
            actual_annual_income = annual_income_needed * (1 + boost_percentage / 100)

        # Validate against HKMC premium limits
        if total_premium < self.plan.minimum_premium:
            # Adjust to minimum premium and recalculate income
            total_premium = self.plan.minimum_premium
            actual_annual_income = (total_premium / premium_per_unit) * annual_payout_per_unit
        elif total_premium > self.plan.maximum_premium:
            # Adjust to maximum premium and recalculate income
            total_premium = self.plan.maximum_premium
            actual_annual_income = (total_premium / premium_per_unit) * annual_payout_per_unit

        # Calculate performance metrics
        expected_irr = self._interpolate_irr(life_expectancy)

        # Break-even analysis: when do total payouts equal premium?
        break_even_years = premium_per_unit / annual_payout_per_unit
        break_even_age = retirement_age + break_even_years

        # Guaranteed payout calculations
        guaranteed_years = self.plan.guaranteed_period  # 20 years
        min_guaranteed_amount = total_premium * 1.05  # 105% minimum guarantee
        period_guaranteed_amount = actual_annual_income * guaranteed_years
        # Use higher of the two guarantees
        total_guaranteed_payout = max(min_guaranteed_amount, period_guaranteed_amount)

        # Lifetime payout estimate based on life expectancy
        payout_years = max(0, life_expectancy - retirement_age)
        lifetime_payout_estimate = actual_annual_income * payout_years

        return AnnuityAnalysis(
            product_name=self.plan.product_name,
            entry_age=retirement_age,
            premium_per_unit=premium_per_unit,
            annual_payout_per_unit=annual_payout_per_unit,
            total_premium_needed=total_premium,
            annual_income=actual_annual_income,
            guaranteed_years=guaranteed_years,
            expected_irr=expected_irr,
            break_even_age=int(break_even_age),
            total_guaranteed_payout=total_guaranteed_payout,
            lifetime_payout_estimate=lifetime_payout_estimate,
            monthly_savings_required=0  # Will be calculated by main calculator
        )


class RetirementCalculator:
    """
    Main calculator for hybrid retirement planning strategy.

    Combines HKMC Annuity Plan with self-investment approach to create
    a balanced retirement income strategy that provides both guaranteed
    income and growth potential.

    The hybrid approach:
    1. Uses annuity for guaranteed income (user-specified percentage)
    2. Uses self-investment for remaining income needs and inflation protection
    3. Calculates total capital requirements and monthly savings needed
    """

    def __init__(self, gender: str = "male"):
        """
        Initialize the hybrid retirement calculator.

        Args:
            gender: Gender for annuity rate calculations
        """
        self.retirement_params = None
        self.healthcare_params = None
        self.annuity_calc = HKMCAnnuityCalculator(gender)

    def set_retirement_parameters(self, current_age: int, retirement_age: int, life_expectancy: int,
                                  current_annual_expense: float, current_savings: float = 0,
                                  pre_retirement_return: float = 0.08, post_retirement_return: float = 0.04,
                                  inflation_rate: float = 0.03):
        """
        Set core retirement planning parameters.

        These parameters form the foundation for all retirement calculations,
        including expense projections, savings requirements, and return assumptions.

        Args:
            current_age: User's current age
            retirement_age: Planned retirement age (minimum 60 for HKMC)
            life_expectancy: Expected lifespan for planning purposes
            current_annual_expense: Current yearly living expenses
            current_savings: Existing retirement savings (default: 0)
            pre_retirement_return: Expected investment return before retirement (default: 8%)
            post_retirement_return: Expected investment return during retirement (default: 4%)
            inflation_rate: General inflation rate for expense growth (default: 3%)
        """
        self.retirement_params = RetirementParameters(
            current_age, retirement_age, life_expectancy, current_annual_expense,
            current_savings, pre_retirement_return, post_retirement_return, inflation_rate
        )

    def set_healthcare_parameters(self, coverage_type: str = HealthcareCoverage.MODERATE,
                                  base_cost: float = 50000, healthcare_inflation: float = 0.05):
        """
        Set healthcare cost parameters for retirement planning.

        Healthcare costs are modeled separately because they:
        1. Inflate faster than general expenses (typically 5%+ vs 3%)
        2. Increase significantly with age due to higher medical needs
        3. Can represent a major portion of retirement expenses

        Args:
            coverage_type: Level of coverage (Basic/Moderate/Comprehensive)
            base_cost: Annual healthcare cost at retirement age (default: HK$50,000)
            healthcare_inflation: Healthcare-specific inflation rate (default: 5%)
        """
        self.healthcare_params = HealthcareParameters(
            base_cost=base_cost,
            inflation_rate=healthcare_inflation,
            coverage_type=coverage_type,
            age_multipliers={}  # Will use default multipliers from __post_init__
        )

    def _calculate_first_year_expense(self) -> float:
        """
        Calculate first-year retirement expense adjusted for inflation.

        Takes current annual expenses and projects them forward to retirement
        age using the inflation rate to determine purchasing power needs.

        Formula: Current_Expense × (1 + inflation_rate)^years_to_retirement

        Returns:
            Inflation-adjusted first year retirement expense
        """
        years_to_retirement = self.retirement_params.retirement_age - self.retirement_params.current_age
        return (self.retirement_params.current_annual_expense *
                (1 + self.retirement_params.inflation_rate) ** years_to_retirement)

    def _get_age_multiplier(self, age: int) -> float:
        """
        Get healthcare cost multiplier for a specific age using interpolation.

        Healthcare costs increase non-linearly with age. This method uses
        linear interpolation between defined age points to estimate the
        cost multiplier for any age.

        Example:
        - Age 70: 1.3x baseline
        - Age 75: 1.7x baseline
        - Age 72: interpolated to ~1.46x baseline

        Args:
            age: Age to calculate multiplier for

        Returns:
            Healthcare cost multiplier (1.0 = baseline at age 65)
        """
        if not self.healthcare_params:
            return 1.0  # No healthcare cost modeling

        age_multipliers = self.healthcare_params.age_multipliers
        ages = sorted(age_multipliers.keys())

        # Handle edge cases
        if age <= ages[0]:
            return age_multipliers[ages[0]]
        elif age >= ages[-1]:
            return age_multipliers[ages[-1]]

        # Linear interpolation between two closest age points
        for i in range(len(ages) - 1):
            if ages[i] <= age <= ages[i + 1]:
                lower_age, upper_age = ages[i], ages[i + 1]
                lower_mult, upper_mult = age_multipliers[lower_age], age_multipliers[upper_age]

                # Calculate interpolation weight
                weight = (age - lower_age) / (upper_age - lower_age)
                return lower_mult + weight * (upper_mult - lower_mult)

        return 1.0  # Fallback

    def _calculate_expenses_by_year(self) -> Tuple[list, list, list]:
        """
        Calculate projected expenses for each year of retirement.

        Models three components:
        1. Basic living expenses (grow with general inflation)
        2. Healthcare costs (grow with healthcare inflation + age multipliers)
        3. Total expenses (sum of basic + healthcare)

        This year-by-year calculation is essential for:
        - Present value calculations
        - Understanding expense trajectory over time
        - Separating fixed vs. age-dependent costs

        Returns:
            Tuple of (basic_expenses, healthcare_costs, total_expenses) lists
            Each list contains annual costs for each year of retirement
        """
        retirement_years = self.retirement_params.life_expectancy - self.retirement_params.retirement_age
        first_year_expense = self._calculate_first_year_expense()

        # Basic living expenses: grow with general inflation each year
        basic_expenses = [first_year_expense * (1 + self.retirement_params.inflation_rate) ** year
                          for year in range(retirement_years)]

        # Healthcare costs: more complex modeling with age multipliers
        healthcare_costs = []
        if self.healthcare_params:
            # Project healthcare base cost to retirement
            years_to_retirement = self.retirement_params.retirement_age - self.retirement_params.current_age
            base_cost_at_retirement = (self.healthcare_params.base_cost *
                                       (1 + self.healthcare_params.inflation_rate) ** years_to_retirement)

            # Calculate healthcare cost for each retirement year
            for year in range(retirement_years):
                current_age = self.retirement_params.retirement_age + year
                age_multiplier = self._get_age_multiplier(current_age)

                # Apply both healthcare inflation and age multiplier
                annual_cost = (base_cost_at_retirement * age_multiplier *
                               (1 + self.healthcare_params.inflation_rate) ** year)
                healthcare_costs.append(annual_cost)
        else:
            # No healthcare cost modeling
            healthcare_costs = [0] * retirement_years

        # Total expenses = basic living + healthcare costs
        total_expenses = [basic + healthcare for basic, healthcare in zip(basic_expenses, healthcare_costs)]

        return basic_expenses, healthcare_costs, total_expenses

    def calculate_hybrid_strategy(self, annuity_percentage: float) -> Tuple[AnnuityAnalysis, float, float]:
        """
        Calculate the complete hybrid retirement strategy.

        This is the main calculation that:
        1. Determines annuity requirements for specified percentage of income
        2. Calculates remaining corpus needed for self-investment
        3. Computes total capital requirements and monthly savings needed

        The hybrid approach provides:
        - Guaranteed income from annuity (inflation protection limited)
        - Growth potential from self-investment (inflation protection through growth)
        - Risk diversification across two approaches

        Args:
            annuity_percentage: Percentage of retirement income from annuity (0-100)

        Returns:
            Tuple of (AnnuityAnalysis, remaining_corpus_needed, future_value_current_savings)
        """
        # Get year-by-year expense projections
        basic_expenses, healthcare_costs, total_expenses = self._calculate_expenses_by_year()
        first_year_expense = total_expenses[0]

        # STEP 1: Calculate annuity portion
        # Determine how much annual income annuity should provide
        annuity_income_needed = first_year_expense * (annuity_percentage / 100)

        # Get detailed annuity analysis
        annuity_analysis = self.annuity_calc.calculate_annuity_requirements(
            self.retirement_params.retirement_age,
            annuity_income_needed,
            self.retirement_params.life_expectancy
        )

        # STEP 2: Calculate self-investment portion
        # Determine remaining expenses after annuity income
        # Note: Annuity provides fixed income, so remaining expenses grow over time
        remaining_expenses = [max(0, expense - annuity_income_needed) for expense in total_expenses]

        # Calculate present value of remaining expenses using post-retirement return rate
        # This tells us how much corpus we need at retirement to fund remaining expenses
        remaining_corpus_needed = sum(
            expense / (1 + self.retirement_params.post_retirement_return) ** (i + 1)
            for i, expense in enumerate(remaining_expenses)
        )

        # STEP 3: Calculate total capital requirements
        total_capital_needed = annuity_analysis.total_premium_needed + remaining_corpus_needed

        # STEP 4: Account for existing savings
        # Calculate future value of current savings at retirement
        years_to_retirement = self.retirement_params.retirement_age - self.retirement_params.current_age
        future_value_current_savings = 0
        if self.retirement_params.current_savings > 0:
            future_value_current_savings = (self.retirement_params.current_savings *
                                            (1 + self.retirement_params.pre_retirement_return) ** years_to_retirement)

        # Calculate additional savings needed
        additional_needed = max(0, total_capital_needed - future_value_current_savings)

        # STEP 5: Calculate monthly savings using annuity formula
        # This determines how much to save monthly to reach the target
        months_to_retirement = years_to_retirement * 12
        monthly_rate = self.retirement_params.pre_retirement_return / 12

        if monthly_rate == 0:
            # Simple division if no investment return
            monthly_savings = additional_needed / months_to_retirement
        else:
            # Future Value of Annuity formula: FV = PMT × [((1 + r)^n - 1) / r]
            # Solving for PMT: PMT = FV / [((1 + r)^n - 1) / r]
            monthly_savings = additional_needed / (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate)

        # Update annuity analysis with monthly savings requirement
        annuity_analysis.monthly_savings_required = monthly_savings

        return annuity_analysis, remaining_corpus_needed, future_value_current_savings


def get_user_input():
    """
    Collect all user inputs for retirement planning.

    Gathers comprehensive information needed for hybrid strategy calculation:
    - Demographics and timeline
    - Financial situation and goals
    - Investment assumptions
    - Healthcare preferences
    - Strategy allocation preference

    Returns:
        Dictionary containing all user inputs for calculation
    """
    print("🎯 HYBRID RETIREMENT PLANNING CALCULATOR")
    print("=" * 60)

    # Basic demographic and timeline information
    print("\n📋 BASIC RETIREMENT INFORMATION:")
    current_age = int(input("Enter your current age: "))
    retirement_age = int(input("Enter your planned retirement age (default 65): ") or "65")
    life_expectancy = int(input("Enter your life expectancy (default 85): ") or "85")
    current_annual_expense = float(input("Enter your current annual expenses: $"))
    current_savings = float(input("Enter your current retirement savings (default 0): $") or "0")

    # Investment return assumptions
    print("\n💼 INVESTMENT ASSUMPTIONS:")
    pre_retirement_return = float(
        input("Expected annual return before retirement (default 8%): ").replace('%', '') or "8") / 100
    post_retirement_return = float(
        input("Expected annual return during retirement (default 4%): ").replace('%', '') or "4") / 100
    inflation_rate = float(input("Expected inflation rate (default 3%): ").replace('%', '') or "3") / 100

    # Gender for annuity rate calculation
    print("\n👤 ANNUITY INFORMATION:")
    gender = input("Enter your gender (male/female, default male): ").strip().lower() or "male"

    # Core strategy allocation decision
    print("\n🔄 HYBRID STRATEGY ALLOCATION:")
    print("You will use HKMC Annuity + Self-Investment combination")
    annuity_percentage = float(
        input("What percentage should come from annuity? (default 50%): ").replace('%', '') or "50")

    # Healthcare cost planning
    print("\n🏥 HEALTHCARE COST PLANNING:")
    include_healthcare = input("Include healthcare costs? (y/n, default y): ").lower().startswith('y') if input(
        "Include healthcare costs? (y/n, default y): ") else True

    healthcare_params = {}
    if include_healthcare:
        coverage_map = {
            "1": (HealthcareCoverage.BASIC, 30000),
            "2": (HealthcareCoverage.MODERATE, 50000),
            "3": (HealthcareCoverage.COMPREHENSIVE, 80000)
        }
        coverage_choice = input("Healthcare coverage (1=Basic, 2=Moderate, 3=Comprehensive, default 2): ") or "2"
        coverage_type, base_cost = coverage_map.get(coverage_choice, (HealthcareCoverage.MODERATE, 50000))
        healthcare_inflation = float(input("Healthcare inflation rate (default 5%): ").replace('%', '') or "5") / 100
        healthcare_params = {
            'coverage_type': coverage_type,
            'base_cost': base_cost,
            'healthcare_inflation': healthcare_inflation
        }

    return {
        'current_age': current_age, 'retirement_age': retirement_age, 'life_expectancy': life_expectancy,
        'current_annual_expense': current_annual_expense, 'current_savings': current_savings,
        'pre_retirement_return': pre_retirement_return, 'post_retirement_return': post_retirement_return,
        'inflation_rate': inflation_rate, 'gender': gender, 'annuity_percentage': annuity_percentage,
        'include_healthcare': include_healthcare, 'healthcare_params': healthcare_params
    }


def print_analysis_results(annuity_analysis: AnnuityAnalysis, remaining_corpus: float,
                           future_value_current: float, user_params: dict):
    """
    Print comprehensive analysis results in organized format.

    Presents the complete hybrid strategy analysis including:
    - HKMC Annuity Plan details and performance metrics
    - Capital requirements breakdown
    - Monthly savings plan
    - Retirement income projections
    - Longevity scenario analysis

    Args:
        annuity_analysis: Complete annuity analysis results
        remaining_corpus: Self-investment corpus needed
        future_value_current: Future value of existing savings
        user_params: Original user inputs for reference
    """
    print(f"\n" + "=" * 80)
    print(f"🎯 HYBRID RETIREMENT STRATEGY ANALYSIS")
    print(f"=" * 80)

    # HKMC Annuity Plan Analysis Section
    print(f"\n💰 HKMC ANNUITY PLAN ANALYSIS:")
    print(f"Product: {annuity_analysis.product_name}")
    print(f"Gender: {user_params['gender'].title()}")
    print(f"Entry Age: {annuity_analysis.entry_age}")

    print(f"\n📊 ANNUITY DETAILS:")
    # Calculate and display the actual payout rate
    annuity_payout_rate = (annuity_analysis.annual_income / annuity_analysis.total_premium_needed) * 100
    print(f"Premium needed: ${annuity_analysis.total_premium_needed:,.0f}")
    print(f"Annual income: ${annuity_analysis.annual_income:,.0f}")
    print(f"Monthly income: ${annuity_analysis.annual_income / 12:,.0f}")
    print(f"Payout rate: {annuity_payout_rate:.1f}% (Gender-specific)")
    print(f"Guaranteed period: {annuity_analysis.guaranteed_years} years")
    print(f"Break-even age: {annuity_analysis.break_even_age}")

    # Hybrid Strategy Breakdown Section
    total_capital = annuity_analysis.total_premium_needed + remaining_corpus
    annuity_pct = user_params['annuity_percentage']

    print(f"\n💼 HYBRID STRATEGY BREAKDOWN:")
    print(f"Strategy: {annuity_pct:.0f}% Annuity + {100 - annuity_pct:.0f}% Self-Investment")
    print(f"Annuity Premium: ${annuity_analysis.total_premium_needed:,.0f}")
    print(f"Self-Investment Corpus: ${remaining_corpus:,.0f}")
    print(f"Total Capital Required: ${total_capital:,.0f}")

    # Monthly Savings Plan Section
    print(f"\n💰 SAVINGS PLAN:")
    print(f"Monthly savings needed: ${annuity_analysis.monthly_savings_required:,.0f}")

    if future_value_current > 0:
        print(f"Future value of current savings: ${future_value_current:,.0f}")

    years_to_retirement = user_params['retirement_age'] - user_params['current_age']
    total_contributions = annuity_analysis.monthly_savings_required * 12 * years_to_retirement
    print(f"Total contributions over {years_to_retirement} years: ${total_contributions:,.0f}")

    # Retirement Income Projections Section
    self_investment_income = remaining_corpus * user_params['post_retirement_return']
    total_first_year_income = annuity_analysis.annual_income + self_investment_income

    print(f"\n🎯 RETIREMENT INCOME BREAKDOWN:")
    print(
        f"Guaranteed Annuity: ${annuity_analysis.annual_income:,.0f}/year (${annuity_analysis.annual_income / 12:,.0f}/month)")
    print(f"Self-Investment: ${self_investment_income:,.0f}/year (${self_investment_income / 12:,.0f}/month)")
    print(f"Total First Year: ${total_first_year_income:,.0f}/year (${total_first_year_income / 12:,.0f}/month)")

    # Longevity Scenario Analysis Section
    print(f"\n📈 LONGEVITY SCENARIOS:")
    # Test scenarios: 5 years shorter, expected, 5 years longer
    scenarios = [user_params['life_expectancy'] - 5, user_params['life_expectancy'], user_params['life_expectancy'] + 5]

    for life_exp in scenarios:
        if life_exp > 0:
            # Create temporary analysis for this life expectancy
            temp_analysis = AnnuityAnalysis("", 0, 0, 0, annuity_analysis.total_premium_needed,
                                            annuity_analysis.annual_income, 0, 0, 0, 0, 0, 0)

            # Calculate total payout for this scenario
            payout_years = max(0, life_exp - user_params['retirement_age'])
            temp_analysis.lifetime_payout_estimate = annuity_analysis.annual_income * payout_years

            # Calculate return on investment
            roi_percent = ((temp_analysis.lifetime_payout_estimate / temp_analysis.total_premium_needed - 1) * 100)

            # Display with appropriate emoji indicator
            status = "📉" if life_exp < user_params['life_expectancy'] else "📊" if life_exp == user_params[
                'life_expectancy'] else "📈"
            print(f"  {status} Live to {life_exp}: Total Return = {roi_percent:.1f}%")


def main():
    """
    Main execution function for the hybrid retirement calculator.

    Orchestrates the complete calculation process:
    1. Collect user inputs
    2. Initialize calculator with user preferences
    3. Set planning parameters
    4. Calculate hybrid strategy
    5. Display comprehensive results
    6. Handle errors gracefully
    """
    try:
        # Step 1: Collect all user inputs
        user_params = get_user_input()

        # Step 2: Initialize calculator with gender-specific rates
        calculator = RetirementCalculator(user_params['gender'])

        # Step 3: Configure calculator with user parameters
        calculator.set_retirement_parameters(
            current_age=user_params['current_age'],
            retirement_age=user_params['retirement_age'],
            life_expectancy=user_params['life_expectancy'],
            current_annual_expense=user_params['current_annual_expense'],
            current_savings=user_params['current_savings'],
            pre_retirement_return=user_params['pre_retirement_return'],
            post_retirement_return=user_params['post_retirement_return'],
            inflation_rate=user_params['inflation_rate']
        )

        # Configure healthcare parameters if requested
        if user_params['include_healthcare']:
            calculator.set_healthcare_parameters(**user_params['healthcare_params'])

        # Step 4: Calculate the complete hybrid strategy
        annuity_analysis, remaining_corpus, future_value_current = calculator.calculate_hybrid_strategy(
            user_params['annuity_percentage']
        )

        # Step 5: Display comprehensive results
        print_analysis_results(annuity_analysis, remaining_corpus, future_value_current, user_params)

        # Final summary and recommendations
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"💡 Benefits of Your Hybrid Strategy:")
        print(f"   ✅ Guaranteed lifelong income from HKMC Annuity")
        print(f"   ✅ Growth potential from self-invested portion")
        print(f"   ✅ Risk diversification and longevity protection")

    except KeyboardInterrupt:
        print(f"\n\nCalculation interrupted.")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()