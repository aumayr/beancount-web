"""Parsing and computing budgets."""
import datetime
from collections import Counter
from collections import defaultdict
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

from beancount.core.data import Custom
from beancount.core.number import Decimal

from fava.core.module_base import FavaModule
from fava.helpers import BeancountError
from fava.util.date import days_in_daterange
from fava.util.date import Interval
from fava.util.date import number_of_days_in_period

if TYPE_CHECKING:
    from fava.core import FavaLedger


class Budget(NamedTuple):
    """A budget entry."""

    account: str
    date_start: datetime.date
    period: Interval
    number: Decimal
    currency: str


BudgetDict = Dict[str, List[Budget]]


class BudgetError(BeancountError):
    """Error with a budget."""


class BudgetModule(FavaModule):
    """Parses budget entries."""

    def __init__(self, ledger: "FavaLedger") -> None:
        super().__init__(ledger)
        self.budget_entries: BudgetDict = {}

    def load_file(self) -> None:
        self.budget_entries, errors = parse_budgets(
            self.ledger.all_entries_by_type.Custom
        )
        self.ledger.errors.extend(errors)

    def calculate(
        self,
        account: str,
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Dict[str, Decimal]:
        """Calculate the budget for an account in an interval."""
        return calculate_budget(
            self.budget_entries, account, begin_date, end_date
        )

    def calculate_children(
        self,
        account: Union[str, Tuple[str]],
        begin_date: datetime.date,
        end_date: datetime.date,
    ) -> Dict[str, Decimal]:
        """Calculate the budget for an account including its children."""
        return calculate_budget_children(
            self.budget_entries, account, begin_date, end_date
        )

    def __bool__(self) -> bool:
        return bool(self.budget_entries)


def parse_budgets(
    custom_entries: List[Custom],
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

    for entry in (entry for entry in custom_entries if entry.type == "budget"):
        try:
            interval = interval_map.get(str(entry.values[1].value))
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
            )
            budgets[budget.account].append(budget)
        except (IndexError, TypeError):
            errors.append(
                BudgetError(entry.meta, "Failed to parse budget entry", entry)
            )

    return budgets, errors


def _matching_budgets(
    budgets: BudgetDict, accounts: str, date_active: datetime.date
) -> Dict[str, Budget]:
    """Find matching budgets.

    Returns:
        The budget that is active on the specified date for the
        specified account.
    """
    last_seen_budgets = {}
    for budget in budgets[accounts]:
        if budget.date_start <= date_active:
            last_seen_budgets[budget.currency] = budget
        else:
            break
    return last_seen_budgets


def calculate_budget(
    budgets: BudgetDict,
    account: str,
    date_from: datetime.date,
    date_to: datetime.date,
) -> Dict[str, Decimal]:
    """Calculate budget for an account.

    Args:
        budgets: A list of :class:`Budget` entries.
        account: An account name.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    if account not in budgets:
        return {}

    currency_dict: Dict[str, Decimal] = defaultdict(Decimal)

    for single_day in days_in_daterange(date_from, date_to):
        matches = _matching_budgets(budgets, account, single_day)
        for budget in matches.values():
            currency_dict[
                budget.currency
            ] += budget.number / number_of_days_in_period(
                budget.period, single_day
            )
    return currency_dict


def calculate_budget_children(
    budgets: BudgetDict,
    account: Union[str, Tuple[str]],
    date_from: datetime.date,
    date_to: datetime.date,
) -> Dict[str, Decimal]:
    """Calculate budget for an account including budgets of its children.

    Args:
        budgets: A list of :class:`Budget` entries.
        account: A list of account names.
        date_from: Starting date.
        date_to: End date (exclusive).

    Returns:
        A dictionary of currency to Decimal with the budget for the
        specified account and period.
    """
    currency_dict: Dict[str, Decimal] = Counter()  # type: ignore

    for child in budgets.keys():
        if child.startswith(account):
            currency_dict.update(
                calculate_budget(budgets, child, date_from, date_to)
            )
    return currency_dict
