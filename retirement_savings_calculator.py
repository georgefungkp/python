#!/usr/bin/env python3

"""
Retirement Savings Calculator

This program estimates the monthly savings needed from now until retirement
to maintain a desired lifestyle after retirement.
"""

import matplotlib.pyplot as plt
import numpy as np


class RetirementCalculator:
    def __init__(self):
        """Initialize the retirement calculator."""
        self.current_age = None
        self.retirement_age = None
        self.life_expectancy = None
        self.annual_expense_after_retirement = None
        self.current_savings = None
        self.pre_retirement_return = None
        self.post_retirement_return = None
    
    def set_parameters(self, current_age, retirement_age, life_expectancy,
                      annual_expense_after_retirement, current_savings,
                      pre_retirement_return, post_retirement_return):
        """
        Set all the parameters for the retirement calculation.
        
        Args:
            current_age: Current age in years
            retirement_age: Age at retirement
            life_expectancy: Expected age at death
            annual_expense_after_retirement: Annual expenses needed after retirement
            current_savings: Current amount saved
            pre_retirement_return: Expected annual return before retirement (as percentage, e.g., 7 for 7%)
            post_retirement_return: Expected annual return after retirement (as percentage, e.g., 4 for 4%)
        """
        self.current_age = current_age
        self.retirement_age = retirement_age
        self.life_expectancy = life_expectancy
        self.annual_expense_after_retirement = annual_expense_after_retirement
        self.current_savings = current_savings
        # Convert percentage to decimal
        self.pre_retirement_return = pre_retirement_return / 100
        self.post_retirement_return = post_retirement_return / 100
    
    def calculate_retirement_corpus_needed(self):
        """
        Calculate the total corpus needed at retirement to support post-retirement expenses.
        
        Returns:
            Total amount needed at retirement
        """
        years_in_retirement = self.life_expectancy - self.retirement_age
        
        # Calculate present value of all future expenses at retirement
        # Using the formula for present value of annuity
        if self.post_retirement_return == 0:
            # If no return expected, simple multiplication
            total_needed = self.annual_expense_after_retirement * years_in_retirement
        else:
            # Present value of annuity formula
            pv_factor = (1 - (1 + self.post_retirement_return) ** (-years_in_retirement)) / self.post_retirement_return
            total_needed = self.annual_expense_after_retirement * pv_factor
        
        return total_needed
    
    def calculate_future_value_of_current_savings(self):
        """
        Calculate what current savings will be worth at retirement.
        
        Returns:
            Future value of current savings
        """
        years_to_retirement = self.retirement_age - self.current_age
        future_value = self.current_savings * (1 + self.pre_retirement_return) ** years_to_retirement
        return future_value
    
    def calculate_monthly_savings_needed(self):
        """
        Calculate the monthly savings needed from now until retirement.
        
        Returns:
            Dictionary containing calculation results
        """
        # Step 1: Calculate total corpus needed at retirement
        corpus_needed = self.calculate_retirement_corpus_needed()
        
        # Step 2: Calculate future value of current savings
        future_value_current_savings = self.calculate_future_value_of_current_savings()
        
        # Step 3: Calculate additional amount needed
        additional_needed = corpus_needed - future_value_current_savings
        
        # Step 4: Calculate monthly savings needed
        years_to_retirement = self.retirement_age - self.current_age
        months_to_retirement = years_to_retirement * 12
        monthly_return = (1 + self.pre_retirement_return) ** (1/12) - 1
        
        if additional_needed <= 0:
            monthly_savings = 0
        elif monthly_return == 0:
            # If no return, simple division
            monthly_savings = additional_needed / months_to_retirement
        else:
            # Future value of annuity formula (solving for payment)
            # FV = PMT * [((1 + r)^n - 1) / r]
            # PMT = FV * r / ((1 + r)^n - 1)
            fv_factor = ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
            monthly_savings = additional_needed / fv_factor
        
        return {
            'corpus_needed': corpus_needed,
            'future_value_current_savings': future_value_current_savings,
            'additional_needed': additional_needed,
            'monthly_savings_required': monthly_savings,
            'years_to_retirement': years_to_retirement,
            'years_in_retirement': self.life_expectancy - self.retirement_age
        }
    
    def create_savings_projection(self, results):
        """
        Create a visualization of the savings projection.
        
        Args:
            results: Results dictionary from calculate_monthly_savings_needed()
        """
        years_to_retirement = results['years_to_retirement']
        monthly_savings = results['monthly_savings_required']
        
        # Create yearly projections
        years = np.arange(0, years_to_retirement + 1)
        savings_balance = []
        
        current_balance = self.current_savings
        
        for year in years:
            if year == 0:
                savings_balance.append(current_balance)
            else:
                # Add annual savings and apply return
                annual_savings = monthly_savings * 12
                current_balance = (current_balance + annual_savings) * (1 + self.pre_retirement_return)
                savings_balance.append(current_balance)
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Savings accumulation over time
        ax1.plot(years + self.current_age, savings_balance, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.axhline(y=results['corpus_needed'], color='r', linestyle='--', 
                   label=f'Target Corpus: ${results["corpus_needed"]:,.0f}')
        ax1.set_xlabel('Age')
        ax1.set_ylabel('Savings Balance ($)')
        ax1.set_title('Projected Savings Growth Until Retirement')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Plot 2: Post-retirement withdrawal scenario
        retirement_years = np.arange(0, self.life_expectancy - self.retirement_age + 1)
        retirement_balance = []
        balance = results['corpus_needed']
        
        for year in retirement_years:
            retirement_balance.append(balance)
            if year < len(retirement_years) - 1:  # Don't subtract in the last year
                balance = (balance - self.annual_expense_after_retirement) * (1 + self.post_retirement_return)
        
        ax2.plot(retirement_years + self.retirement_age, retirement_balance, 'g-', 
                linewidth=2, marker='s', markersize=4)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Depletion Point')
        ax2.set_xlabel('Age')
        ax2.set_ylabel('Retirement Balance ($)')
        ax2.set_title('Projected Balance During Retirement')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        plt.tight_layout()
        plt.savefig('retirement_projection.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_summary(self, results):
        """
        Print a detailed summary of the retirement planning results.
        
        Args:
            results: Results dictionary from calculate_monthly_savings_needed()
        """
        print("=" * 60)
        print("RETIREMENT SAVINGS ANALYSIS")
        print("=" * 60)
        
        print("\nINPUT PARAMETERS:")
        print(f"Current Age: {self.current_age}")
        print(f"Retirement Age: {self.retirement_age}")
        print(f"Life Expectancy: {self.life_expectancy}")
        print(f"Current Savings: ${self.current_savings:,.2f}")
        print(f"Annual Expenses After Retirement: ${self.annual_expense_after_retirement:,.2f}")
        print(f"Expected Return Before Retirement: {self.pre_retirement_return:.1%}")
        print(f"Expected Return After Retirement: {self.post_retirement_return:.1%}")
        
        print("\nCALCULATION RESULTS:")
        print(f"Years Until Retirement: {results['years_to_retirement']}")
        print(f"Years in Retirement: {results['years_in_retirement']}")
        print(f"Total Corpus Needed at Retirement: ${results['corpus_needed']:,.2f}")
        print(f"Future Value of Current Savings: ${results['future_value_current_savings']:,.2f}")
        print(f"Additional Amount Needed: ${results['additional_needed']:,.2f}")
        
        print("\nRECOMMENDATION:")
        if results['monthly_savings_required'] <= 0:
            print("🎉 Good news! Your current savings are sufficient for retirement.")
            excess = abs(results['additional_needed'])
            print(f"You will have an excess of ${excess:,.2f} at retirement.")
        else:
            print(f"💰 Monthly Savings Required: ${results['monthly_savings_required']:,.2f}")
            annual_savings = results['monthly_savings_required'] * 12
            print(f"📅 Annual Savings Required: ${annual_savings:,.2f}")
            
            # Calculate as percentage of common income levels
            income_levels = [50000, 75000, 100000, 150000]
            print("\nAs percentage of annual income:")
            for income in income_levels:
                percentage = (annual_savings / income) * 100
                print(f"  ${income:,} income: {percentage:.1f}%")


def main():
    """Main function to run the retirement calculator."""
    calc = RetirementCalculator()
    
    # Example scenario - you can modify these values
    print("Retirement Savings Calculator")
    print("-" * 30)
    
    # Get user input or use example values
    try:
        current_age = int(input("Enter your current age (or press Enter for example): ") or 50)
        retirement_age = int(input("Enter retirement age (or press Enter for 60): ") or 60)
        life_expectancy = int(input("Enter life expectancy (or press Enter for 85): ") or 85)
        annual_expenses = float(input("Enter annual expenses after retirement (or press Enter for $400,000): ") or 400000)
        current_savings = float(input("Enter current savings (or press Enter for $5,000,000): ") or 5000000)
        pre_return = float(input("Enter expected return before retirement as percentage (or press Enter for 7%): ") or 7)
        post_return = float(input("Enter expected return after retirement as percentage (or press Enter for 4%): ") or 4)
        
    except (ValueError, KeyboardInterrupt):
        print("\nUsing example values...")
        current_age = 50
        retirement_age = 60
        life_expectancy = 85
        annual_expenses = 400000
        current_savings = 5000000
        pre_return = 7  # 7% annual return
        post_return = 4  # 4% annual return
    
    # Set parameters
    calc.set_parameters(
        current_age=current_age,
        retirement_age=retirement_age,
        life_expectancy=life_expectancy,
        annual_expense_after_retirement=annual_expenses,
        current_savings=current_savings,
        pre_retirement_return=pre_return,
        post_retirement_return=post_return
    )
    
    # Calculate results
    results = calc.calculate_monthly_savings_needed()
    
    # Display results
    calc.print_summary(results)
    
    # Create visualization
    create_plot = input("\nWould you like to see the projection charts? (y/n): ").lower().strip()
    if create_plot in ['y', 'yes', '']:
        calc.create_savings_projection(results)


if __name__ == "__main__":
    main()
