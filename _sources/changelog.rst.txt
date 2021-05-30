Changelog
=========

Unreleased
----------

Nothing yet.

v1.19 (2021-05-18)
------------------

The `conversion` and `interval` options have been removed. Their functionality
can be achieved with the new `default-page` option. The editor components have
been completely reworked, include autocompletion in more places and are now
based on version 6 of CodeMirror. An option `invert-income-liabilities-equity`
has been added to invert the numbers of those accounts on the income statement
and the balance sheet. This release also adds a Bulgarian translation and
features various smaller improvements and fixes as usual.

v1.18 (2021-01-16)
------------------

This release contains couple of small improvements and various bug fixes.

v1.17 (2020-11-15)
------------------

This release adds a document preview to the import page, as well as support
for Python 3.9. It also fixes a couple of bugs.

v1.16 (2020-10-18)
------------------

This release brings area charts as an alternative option to view the various
line charts in Fava and a Catalan translation for Fava. There is also now an
option to set the indentation of inserted Beancount entries. As usual this
release also includes various minor fixes and improvements.

v1.15 (2020-05-30)
------------------

This release accumulates various minor fixes and improvements, for example the
setting of filters from payees and metadata in the Journal report.

v1.14 (2020-02-16)
------------------

This is mainly a bugfix release to fix compatibility with one of the main
dependencies (werkzeug). Also, a `default-conversion` option was added, which
allows setting a default conversion.

v1.13 (2020-02-01)
------------------

Fava can now display charts for BQL queries - if they have exactly two columns
with the first being a date or string and the second an inventory, then a line
chart or treemap chart is shown on the query page.

v1.12 (2019-12-03)
------------------

Apart from plenty of bug fixes, this release mainly contains improvements to
the forms to add transactions: postings can now be dragged and the full cost
syntax of Beancount should supported.

v1.11 (2019-08-20)
------------------

The import page of Fava has been reworked - it now supports moving files to the
documents folder and the import process should be a bit more interactive. This
release also contains various fixes and a new `collapse-pattern` option to
collapse accounts in account trees based on regular expressions (and replaces
the use of the `fava-collapse-account` metadata entry).

Other changes:

- Command line flags can be specified by setting environment variables.
- A Taiwanese translation has been added.

v1.10 (2019-01-31)
------------------

This release contains mostly smaller changes and fixes. In particular, the net
worth chart will now follow the selected conversion.

v1.9 (2018-10-08)
-----------------

In this release, the click behaviour has been updated to allow filtering for
payees. The entry input forms now allow inputting prices and costs.  As
always, bugs have been fixed.

v1.8 (2018-07-25)
-----------------

The journal design has been updated and should now have a clearer structure.
Starting with this version, there will not be any more GUI releases of Fava.
The GUI broke frequently and does not seem to worth the maintenance burden.

Other changes:

- When downloading documents, the original filename will be used.
- `any()` and `all()` functions have been added to the filter syntax to allow
  filtering entries by properties of their postings.
- As always, bugs have been fixed.

v1.7 (2018-03-09)
-----------------

The entry filters have been reworked in this release and should now support for
more flexible filtering of the entries. See the help page on how the new syntax
works.  Also, when completing the payee in the transaction form, the postings
of the last transaction for this payee will be auto-filled.

Other changes:

- The fava-option to hide the charts has been removed. This is now tracked in
  the page URL.
- As always, bugs have been fixed.

v1.6 (2017-10-06)
-----------------

This is a release with various small changes and mainly some speed
improvements to the Balance Sheet and the net worth calculation. Also, if 'At
Value' is selected, the current unrealized gain is shown in parentheses in the
Balance Sheet.

Other changes:

- The currently filtered entries can now be exported from the Journal page.
- The CLI now has a ``--version`` flag.

v1.5 (2017-07-23)
-----------------

Fava now has an interface to edit single entries. Clicking on the entry date in
the Journal will open an overlay that shows the entry context and allows
editing just the lines of that entry.

Other changes:

- The source editor now has a menu that gives access to editor commands like
  "fold all".
- Entries with matching tags or links can now be excluded with ``-#tag``.
- The keyboard shortcuts are now displayed in-place.
- The ``incognito`` option has been removed and replaced with a ``--incognito``
  command line switch.
- As always, several bugs have been fixed.

v1.4 (2017-05-14)
-----------------

Fava now provides an interface for Beancount's import system that allows you to
import transactions from your bank for example.

Fava can now show your balances at market value or convert them to a single
currency if your file contains the necessary price information.

We now also provide a compiled GUI version of Fava for Linux and macOS. This
version might still be a bit buggy so any feedback/help on it is very welcome.

Other changes:

- The ``insert-entry`` option can be used to control where transactions are
  inserted.
- The transaction form now accepts tags and links in the narration field.
- Budgets are now accumulated over all children where appropriate.
- As always, several bugs have been fixed.

Thanks to :user:`TZdyrski` and :user:`Akuukis` for their contributions.

v1.3 (2017-03-15)
-----------------

The translations of Fava are now on `POEditor.com
<https://poeditor.com/projects/view?id=90283>`__, which has helped us get
translations in five more languages: Chinese (simplified), Dutch, French,
Portuguese, and Spanish. A big thank you to the new translators!

The transaction form has been improved, it now supports adding metadata and the
suggestions will be ranked by how often and recently they occur (using
exponential decay).

The Query page supports all commands of the ``bean-query`` shell and shares its
history of recently used queries.

Fava has gained a basic extension mechanism. Extensions allow you to run hooks
at various points, e.g., after adding a transaction. They are specified using
the ``extensions`` option and for an example, see the ``fava.ext.auto_commit``
extension.

Other changes:

- The default sort order in journals has been reversed so that the most recent
  entries come first.
- The new ``incognito`` option can be used to obscure all numbers.
- As always, several bugs have been fixed.

Thanks to :user:`johannesharms` and :user:`xentac` for their contributions.

v1.2 (2016-12-25)
-----------------

You can now add transactions from within Fava. The form supports autocompletion
for most fields.

Fava will now show a little bubble in the sidebar for the number of events in
the next week. This can be configured with the ``upcoming-events`` option.

Other changes:

- The payee filter can filter by regular expression.
- The tag filter can filter for links, too.
- There's a nice spinning indicator during asynchronous page loads.
- The Journal shows little indicators for metadata.
- As always, several bugs have been fixed.

Thanks to :user:`fokusov` for their contributions.

v1.1 (2016-11-19)
-----------------

You can now upload documents by dropping them onto transactions, which will
also add the file path as `statement` metadata to the transaction. Fava also
ships with a plugin to link these transactions with the generated documents.
See the help pages for details.

This is the first release for which we provide compiled binaries (for macOS and
Linux). These do not have any dependencies and can simply be executed from the
terminal.

Other changes:

- The bar charts on account pages now also show budgets.
- The Journal can now be sorted by date, flag and narration.
- Fava now has a Russian translation, thanks to :user:`fokusov`.
- As always, several bugs have been fixed.

Thanks to :user:`adamgibbins` and :user:`xentac` for their contributions.

v1.0 (2016-10-19)
-----------------

This is a major new release that includes too many improvements and changes to
list. Some highlights:

- The layout has been tweaked and we use some nicer fonts.
- Fava looks and works much better on smaller screens.
- Fava loads most pages asynchronously, so navigating Fava is much faster and
  responsive.

Fava's configuration is not read from a configuration file anymore but can
rather be specified using custom entries in the Beancount file. Some options
have also been removed or renamed, so check Fava's help page on the available
options when upgrading from v0.3.0.

There have been many changes under the hood to improve Fava's codebase and a
lot of bugs have been squashed.

Thanks to :user:`adamgibbins`, :user:`davidastephens`, :user:`xentac`, and
:user:`yegle` for their contributions.

v0.3.0 (2016-03-24)
-------------------

Additions

- Support for switching between multiple beancount files. :bug:`213`
- New sunburst charts. :bug:`198`
- Add "Clear filter" button when filters are active. :bug:`290`
- Simple budgeting functionality in the Account view. See help pages on how to
  use budgets. :bug:`294`
- German translation. :bug:`284`
- The Beancount is now being reloaded when it is saved in the Source Editor.
- New Journal filter controls. Thanks to :user:`yagebu`.
- Tree-tables are now displayed in a hierarchical way. Thanks to :user:`yagebu`.

Changes

- All charts are now rendered with d3.js. Thanks to :user:`yagebu`.
- The title of a page is now shown in the header to save screen space.
- Changed shortcut for Journal from ``g g`` to ``g j`` as the Journal was
  renamed from "General Journal" to "Journal".

New configuration options

- ``language``: The language to use. Valid languages are ``"en"`` and
  ``"de"`` (default: ``"en"``). :bug:`284`
- ``treemaps-show-negative-numbers`` was removed.

Fixes

- Commodity prices are now filtered when a Time filter is enabled. :bug:`273`
- Some improvements to the help pages.
- Many small bug fixes. Thanks to :user:`yagebu`.

v0.2.6 (2016-03-20)
-------------------

Additions

- There are now more interval options available for charts and the account
  balances report. The interval can be selected from a dropdown next to the
  charts. :bug:`175`
- Show metadata for postings in the Journal. Thanks to :user:`corani`.
  :bug:`185`
- The editor now supports org-mode style folding. Thanks to :user:`corani`.
  :bug:`209`
- Show colored dots for all the postings of a transaction in the Journal
  report. This way flagged postings can be quickly spotted. :bug:`195`
- Add keyboard shortcuts for save to source editor. :bug:`199`

Changes

- Use beancount's DisplayContext to determine the correct precision at which to
  render numbers. :bug:`188`
- Improve the way that query results are serialized to XLS etc. Thanks to
  :user:`corani`. :bug:`168`
- Show inverse rates for pairs of operating currencies on the commodities
  report. :bug:`139`
- Use Click for the CLI and check if beancount file exists on startup.
  :bug:`216`
- Hide closed accounts in tree tables. Also see new configuration option below.

New configuration options

- ``editor-strip-trailing-whitespace`` to enable trimming of trailing
  whitespace in the Source editor (default: "false").  Thanks to
  :user:`corani`. :bug:`163`
- ``show-closed-accounts`` to show closed accounts in tree tables, for example
  on the balance sheet (default: "false"). :bug:`91`
- ``show-accounts-with-zero-balance`` to show accounts with a balance of zero
  in tree tables (default: "true"). :bug:`91`
- ``show-accounts-with-zero-transactions`` to show accounts with no
  transactions in tree tables (default: "true"). :bug:`91`

Fixes

- Fixed a bug where the months would be off by one for the interval reports.
  :bug:`182`
- Fix the net worth report for more than one currency. :bug:`207`
- Some improvements to the help pages.
- Many small bug fixes.

v0.2.5 (2016-02-28)
-------------------

Bump release to remove unused draft code.

v0.2.4 (2016-02-18)
-------------------

Additions

- Added missing Holdings views compared to ``bean-web``. Thanks to
  :user:`yagebu`. :bug:`140`
- Custom queries are now shown in sidebar. Thanks to :user:`corani`. :bug:`135`
- The user settings file is now editable in the Source editor. :bug:`136`
- Added second theme. Thanks to Rubén Gómez for the stylesheet. :bug:`59`
- Added Help pages.
- Query results can now be downloaded as CSV, XLS, XLSX and ODS. :bug:`143`
- Documents can now be uploaded by dragging and dropping files over an Account
  name on the Account page and all tree-tables. :bug:`157`
- Journal can now be filtered by transaction type. Thanks to :user:`yagebu`.

Changes

- The uptodate-indicator is now shown everywhere by default, but only enabled
  for accounts that have the metadata ``fava-uptodate-indication: "True"`` set
  on their ``open``-directives. :bug:`35`
- Speedier Journal rendering. Thanks to :user:`yagebu`. :bug:`164`
- Only basenames will be shown for documents in the Journal. Thanks to
  :user:`corani`.
- Slightly reordered the sidebar menu.
- Minor UI tweaks.

New configuration options

- ``sidebar-show-queries``: The maximum number of custom queries to show in the
  sidebar (default: 5).
- ``theme``: The theme to use. Valid themes are ``"default"`` and
  ``"alternative"`` (default: ``"default"``).
- ``editor-print-margin-column``: Set the column for the print margin in the
  Source editor (default: 60). :bug:`161`
- ``uptodate-indicator-show-everywhere`` (default: "true"). See Changes above.

Removed configuration options

- ``uptodate-indicator-exclude-accounts``, see Changes above.

Fixes

- Fixed Net worth calculation. Thanks to :user:`yagebu`.
- Many small bug fixes.

v0.2.3 (2016-02-15)
-------------------

Bumped version to communicate that installing via ``pip install`` now works,
all requirements included.  Thanks to :user:`blais` and :user:`yagebu`.


Earlier Versions
----------------

It was not possible to install any of the earlier versions only using ``pip``
and you may consult the git log for earlier changes. The first commit in the
git repository was on December 4th, 2015.
