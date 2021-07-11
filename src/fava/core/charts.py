"""Provide data suitable for Fava's charts. """
from datetime import date
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Pattern
from typing import Tuple
from typing import Union

from beancount.core import realization
from beancount.core.amount import Amount
from beancount.core.data import iter_entry_dates
from beancount.core.data import Posting
from beancount.core.data import Transaction
from beancount.core.inventory import Inventory
from beancount.core.number import Decimal
from beancount.core.position import Position
from simplejson import JSONEncoder

from fava.core._compat import FLAG_UNREALIZED
from fava.core.conversion import cost_or_value
from fava.core.conversion import units
from fava.core.module_base import FavaModule
from fava.core.tree import SerialisedTreeNode
from fava.core.tree import Tree
from fava.helpers import FavaAPIException
from fava.util import listify
from fava.util import pairwise
from fava.util.date import Interval
from fava.util.typing import TypedDict


ONE_DAY = timedelta(days=1)


def inv_to_dict(inventory: Inventory) -> Dict[str, Decimal]:
    """Convert an inventory to a simple cost->number dict."""
    return {
        pos.units.currency: pos.units.number
        for pos in inventory
        if pos.units.number is not None
    }


Inventory.for_json = inv_to_dict  # type: ignore


class FavaJSONEncoder(JSONEncoder):
    """Allow encoding some Beancount date structures."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Allow use of a `for_json` method to serialise dict subclasses.
        kwargs["for_json"] = True
        # Sort dict keys (Flask also does this by default).
        kwargs["sort_keys"] = True
        super().__init__(*args, **kwargs)

    def default(self, o: Any) -> Any:  # pylint: disable=method-hidden
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, Amount, Position)):
            return str(o)
        if isinstance(o, (set, frozenset)):
            return list(o)
        if isinstance(o, Pattern):
            return o.pattern
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


ENCODER = FavaJSONEncoder()


def dumps(arg: Any) -> Any:
    """Encode to JSON."""
    return ENCODER.encode(arg)


class DateAndBalance(TypedDict):
    """Balance at a date."""

    date: date
    balance: Union[Dict[str, Decimal], Inventory]


class DateAndBalanceWithBudget(TypedDict):
    """Balance at a date with a budget."""

    date: date
    balance: Dict[str, Inventory]
    budgets: Dict[str, Decimal]
    total_balance: Inventory


class ChartModule(FavaModule):
    """Return data for the various charts in Fava."""

    def hierarchy(
        self,
        account_name: str,
        conversion: str,
        begin: Optional[date] = None,
        end: Optional[date] = None,
    ) -> SerialisedTreeNode:
        """An account tree."""
        if begin is not None and end is not None:
            tree = Tree(iter_entry_dates(self.ledger.entries, begin, end))
        else:
            tree = self.ledger.root_tree
        return tree.get(account_name).serialise(
            conversion, self.ledger.price_map, end - ONE_DAY if end else None
        )

    @listify
    def prices(
        self,
    ) -> Generator[Tuple[str, str, List[Tuple[date, Decimal]]], None, None]:
        """The prices for all commodity pairs.

        Returns:
            A list of tuples (base, quote, prices) where prices
            is a list of prices.
        """
        for base, quote in self.ledger.commodity_pairs():
            prices = self.ledger.prices(base, quote)
            if prices:
                yield base, quote, prices

    @staticmethod
    def augment_inventory(
        inventories: Dict[str, Inventory], account: str, posting: Posting
    ) -> None:
        """Adds posting to inventory under specified account name.

        Args:
            inventories: Dictionary of inventories keyed by account name.
            account: A single account, used to identify an inventory.
            posting: A posting to add to the specified inventory.
        """
        inventory = inventories.get(account)
        if inventory is None:
            inventory = Inventory()
        inventory.add_position(posting)
        inventories[account] = inventory

    # pylint: disable=too-many-locals
    @listify
    def interval_totals(
        self,
        interval: Interval,
        accounts: Union[str, Tuple[str]],
        conversion: str,
        invert: bool = False,
        descend: bool = False,
    ) -> Generator[DateAndBalanceWithBudget, None, None]:
        """Renders totals for account (or accounts) in the intervals.

        Args:
            interval: An interval.
            accounts: A single account (str) or a tuple of accounts.
            conversion: The conversion to use.
        """
        if isinstance(accounts, str):
            accounts = (accounts,)

        for begin, end in pairwise(self.ledger.interval_ends(interval)):
            inventories: Dict[str, Inventory] = {}
            total_inventory = Inventory()
            entries = iter_entry_dates(self.ledger.entries, begin, end)
            for entry in [e for e in entries if isinstance(e, Transaction)]:
                for posting in entry.postings:
                    for account in accounts:
                        if (
                            not descend and posting.account.startswith(account)
                        ) or posting.account == account:
                            self.augment_inventory(
                                inventories, account, posting
                            )
                            total_inventory.add_position(posting)
                        elif posting.account.startswith(account):
                            levels = account.count(":") + 2
                            child_account = ":".join(
                                posting.account.split(":")[:levels]
                            )
                            self.augment_inventory(
                                inventories, child_account, posting
                            )
                            total_inventory.add_position(posting)

            balances = {}
            total_balance: Inventory = cost_or_value(
                total_inventory,
                conversion,
                self.ledger.price_map,
                end - ONE_DAY,
            )

            for account, inventory in inventories.items():
                balances[account] = cost_or_value(
                    inventory, conversion, self.ledger.price_map, end - ONE_DAY
                )

            budgets = self.ledger.budgets.calculate_children(
                accounts, begin, end
            )

            if invert:
                # pylint: disable=invalid-unary-operand-type
                total_balance = -total_balance
                budgets = {k: -v for k, v in budgets.items()}

            yield {
                "date": begin,
                "balance": balances,
                "total_balance": total_balance,
                "budgets": budgets,
            }

    @listify
    def linechart(
        self, account_name: str, conversion: str
    ) -> Generator[DateAndBalance, None, None]:
        """The balance of an account.

        Args:
            account_name: A string.
            conversion: The conversion to use.

        Returns:
            A list of dicts for all dates on which the balance of the given
            account has changed containing the balance (in units) of the
            account at that date.
        """
        real_account = realization.get_or_create(
            self.ledger.root_account, account_name
        )
        postings = realization.get_postings(real_account)
        journal = realization.iterate_with_balance(postings)

        # When the balance for a commodity just went to zero, it will be
        # missing from the 'balance' so keep track of currencies that last had
        # a balance.
        last_currencies = None

        price_map = self.ledger.price_map
        for entry, _, change, balance_inventory in journal:
            if change.is_empty():
                continue

            balance = inv_to_dict(
                cost_or_value(
                    balance_inventory, conversion, price_map, entry.date
                )
            )

            currencies = set(balance.keys())
            if last_currencies:
                for currency in last_currencies - currencies:
                    balance[currency] = 0
            last_currencies = currencies

            yield {"date": entry.date, "balance": balance}

    @listify
    def net_worth(
        self, interval: Interval, conversion: str
    ) -> Generator[DateAndBalance, None, None]:
        """Compute net worth.

        Args:
            interval: A string for the interval.
            conversion: The conversion to use.

        Returns:
            A list of dicts for all ends of the given interval containing the
            net worth (Assets + Liabilities) separately converted to all
            operating currencies.
        """
        transactions = (
            entry
            for entry in self.ledger.entries
            if (
                isinstance(entry, Transaction)
                and entry.flag != FLAG_UNREALIZED
            )
        )

        types = (
            self.ledger.options["name_assets"],
            self.ledger.options["name_liabilities"],
        )

        txn = next(transactions, None)
        inventory = Inventory()

        price_map = self.ledger.price_map
        for end_date in self.ledger.interval_ends(interval):
            while txn and txn.date < end_date:
                for posting in txn.postings:
                    if posting.account.startswith(types):
                        inventory.add_position(posting)
                txn = next(transactions, None)
            yield {
                "date": end_date,
                "balance": cost_or_value(
                    inventory, conversion, price_map, end_date - ONE_DAY
                ),
            }

    @staticmethod
    def can_plot_query(types: List[Tuple[str, Any]]) -> bool:
        """Whether we can plot the given query.

        Args:
            types: The list of types returned by the BQL query.
        """
        return (
            len(types) == 2
            and types[0][1] in {str, date}
            and types[1][1] is Inventory
        )

    def query(
        self, types: List[Tuple[str, Any]], rows: List[Tuple[Any, ...]]
    ) -> Any:
        """Chart for a query.

        Args:
            types: The list of result row types.
            rows: The result rows.
        """

        if not self.can_plot_query(types):
            raise FavaAPIException("Can not plot the given chart.")
        if types[0][1] is date:
            return [
                {"date": date, "balance": units(inv)} for date, inv in rows
            ]
        return [{"group": group, "balance": units(inv)} for group, inv in rows]
