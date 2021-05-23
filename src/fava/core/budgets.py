"""Parsing and computing budgets."""
import datetime
from collections import Counter
from collections import defaultdict
from itertools import chain
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import Union

from beancount.core.number import Decimal

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.util.date import days_in_daterange
from fava.util.date import get_next_interval
from fava.util.date import Interval
from fava.util.date import number_of_days_in_period


class Budget(NamedTuple):
    """A budget entry."""

    account: str
    date_start: datetime.date
    period: Interval
    number: Decimal
    currency: str
    periodic: bool = True


BudgetDict = Dict[str, List[Budget]]


class BudgetError(BeancountError):
    """Error with a budget."""


class BudgetModule(FavaModule):
    """Parses budget entries."""

    def __init__(self, ledger) -> None:
        super().__init__(ledger)
        self.budget_entries: BudgetDict = {}

    def load_file(self) -> None:
        self.budget_entries, errors = parse_budgets(
            self.ledger.all_entries_by_type.Custom
        )
        self.ledger.errors.extend(errors)

    def calculate(
        self,
        accounts: Union[str, Tuple[str]],
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Dict[str, Decimal]:
        """Calculate the budget for an account in an interval."""
        return calculate_budget(
            self.budget_entries, accounts, begin_date, end_date
        )

    def calculate_children(
        self,
        accounts: Union[str, Tuple[str]],
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Dict[str, Decimal]:
        """Calculate the budget for an account including its children."""
        return calculate_budget_children(
            self.budget_entries, accounts, begin_date, end_date
        )

    def __bool__(self) -> bool:
        return bool(self.budget_entries)


def parse_budgets(
    custom_entries,
) -> Tuple[BudgetDict, List[BudgetError]]:
    """Parse budget directives from custom entries.

    Args:
        custom_entries: the Custom entries to parse budgets from.

    Returns:
        A dict of accounts to lists of budgets.

    Example:
        2015-04-09 custom "budget" Expenses:Books "monthly" 20.00 EUR
    """

    budgets: BudgetDict = defaultdict(list)
    errors = []

    interval_map = {
        "daily": Interval.DAY,
        "weekly": Interval.WEEK,
        "monthly": Interval.MONTH,
        "quarterly": Interval.QUARTER,
        "yearly": Interval.YEAR,
    }

    daterange_map = {
        "day": Interval.DAY,
        "week": Interval.WEEK,
        "month": Interval.MONTH,
        "quarter": Interval.QUARTER,
        "year": Interval.YEAR,
    }

    for entry in (entry for entry in custom_entries if entry.type == "budget"):
        try:
            if str(entry.values[1].value) in interval_map:
                interval = interval_map.get(str(entry.values[1].value))
                periodic = True
            else:
                interval = daterange_map.get(str(entry.values[1].value))
                periodic = False
            if not interval:
                errors.append(
                    BudgetError(
                        entry.meta,
                        "Invalid interval for budget entry",
                        entry,
                    )
                )
                continue
            budget = Budget(
                entry.values[0].value,
                entry.date,
                interval,
                entry.values[2].value.number,
                entry.values[2].value.currency,
                periodic,
            )
            budgets[budget.account].append(budget)
        except (IndexError, TypeError):
            errors.append(
                BudgetError(entry.meta, "Failed to parse budget entry", entry)
            )

    return budgets, errors


def _matching_budgets(budgets, accounts, date_active):
    """Find matching budgets.

    Returns:
        The budget that is active on the specified date for the
        specified account.
    """
    matching_budgets = {}

    for budget in budgets[accounts]:
        if budget.date_start <= date_active:
            if budget.periodic:
                if budget.currency in matching_budgets:
                    if matching_budgets[budget.currency][0].periodic:
                        matching_budgets[budget.currency][0] = budget
                    else:
                        matching_budgets[budget.currency].insert(0, budget)
                else:
                    matching_budgets[budget.currency] = [budget]
            elif date_active < get_next_interval(
                budget.date_start, budget.period
            ):
                if budget.currency in matching_budgets:
                    matching_budgets[budget.currency].append(budget)
                else:
                    matching_budgets[budget.currency] = [budget]
        else:
            break

    return matching_budgets


def calculate_budget(
    budgets: BudgetDict,
    accounts: Union[str, Tuple[str]],
    date_from: datetime.date,
    date_to: datetime.date,
) -> Dict[str, Decimal]:
    """Calculate budget for an account.

    Args:
        budgets: A list of :class:`Budget` entries.
        accounts: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    if accounts not in budgets:
        return {}

    currency_dict: Dict[str, Decimal] = defaultdict(Decimal)

    for single_day in days_in_daterange(date_from, date_to):
        matches = _matching_budgets(budgets, accounts, single_day)
        for budget in chain(*matches.values()):
            currency_dict[
                budget.currency
            ] += budget.number / number_of_days_in_period(
                budget.period, single_day
            )
    return currency_dict


def calculate_budget_children(
    budgets: BudgetDict,
    accounts: Union[str, Tuple[str]],
    date_from: datetime.date,
    date_to: datetime.date,
) -> Dict[str, Decimal]:
    """Calculate budget for an account including budgets of its children.

    Args:
        budgets: A list of :class:`Budget` entries.
        accounts: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    currency_dict: Dict[str, Decimal] = Counter()  # type: ignore

    for account in budgets.keys():
        if account.startswith(accounts):
            currency_dict.update(
                calculate_budget(budgets, account, date_from, date_to)
            )
    return currency_dict
