/**
 * This module contains the main code to render Fava's charts.
 *
 * The charts heavily use d3 libraries.
 */

import type { HierarchyNode } from "d3-hierarchy";
import { hierarchy as d3Hierarchy } from "d3-hierarchy";
import { get } from "svelte/store";

import type { FormatterContext } from "../format";
import { currentDateFormat, dateFormat } from "../format";
import { getScriptTagJSON } from "../lib/dom";
import type { TreeNode } from "../lib/tree";
import { stratify } from "../lib/tree";
import type { Validator } from "../lib/validation";
import {
  array,
  date,
  defaultValue,
  lazy,
  number,
  object,
  record,
  string,
  tuple,
  unknown,
} from "../lib/validation";
import { operatingCurrenciesWithConversion } from "../stores";

export interface AccountHierarchyDatum {
  account: string;
  balance: Partial<Record<string, number>>;
  dummy?: boolean;
}
type AccountHierarchy = TreeNode<AccountHierarchyDatum>;
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;

/**
 * Add internal nodes as fake leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
function addInternalNodesAsLeaves(node: AccountHierarchy): void {
  if (node.children.length) {
    node.children.forEach(addInternalNodesAsLeaves);
    node.children.push({ ...node, children: [], dummy: true });
    node.balance = {};
  }
}

export interface ScatterPlotDatum {
  date: Date;
  type: string;
  description: string;
}

export interface LineChartDatum {
  name: string;
  date: Date;
  value: number;
}

export type LineChartData = {
  name: string;
  values: LineChartDatum[];
};

export interface BarChartDatumValue {
  name: string;
  value: Record<string, number>;
  total_value: number;
  budget: number;
}

export interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

export interface HierarchyChart {
  type: "hierarchy";
  data: Map<string, AccountHierarchyNode>;
  tooltipText?: undefined;
}

export interface BarChart {
  type: "barchart";
  data: BarChartDatum[];
  tooltipText: (
    c: FormatterContext,
    d: BarChartDatum,
    account: string
  ) => string;
}

export interface LineChart {
  type: "linechart";
  data: LineChartData[];
  tooltipText: (c: FormatterContext, d: LineChartDatum) => string;
}

export interface ScatterPlot {
  type: "scatterplot";
  data: ScatterPlotDatum[];
  tooltipText?: undefined;
}

type ChartTypes = HierarchyChart | BarChart | ScatterPlot | LineChart;

export function balances(json: unknown): LineChart {
  const validator = array(
    object({
      date,
      balance: record(number),
    })
  );
  const parsedData = validator(json);
  const groups = new Map<string, LineChartDatum[]>();
  for (const { date: date_, balance } of parsedData) {
    Object.entries(balance).forEach(([currency, value]) => {
      const group = groups.get(currency);
      const datum = { date: date_, value, name: currency };
      if (group) {
        group.push(datum);
      } else {
        groups.set(currency, [datum]);
      }
    });
  }
  const data = [...groups.entries()].map(([name, values]) => ({
    name,
    values,
  }));

  return {
    data,
    type: "linechart",
    tooltipText: (c, d) =>
      `${c.currency(d.value)} ${d.name}<em>${dateFormat.day(d.date)}</em>`,
  };
}

export function commodities(json: unknown, label: string): LineChart {
  const validator = object({
    quote: string,
    base: string,
    prices: array(tuple([date, number])),
  });
  const { base, quote, prices } = validator(json);
  const values = prices.map((d) => ({ name: label, date: d[0], value: d[1] }));
  return {
    data: [{ name: label, values }],
    type: "linechart",
    tooltipText(c, d) {
      return `1 ${base} = ${c.currency(d.value)} ${quote}<em>${dateFormat.day(
        d.date
      )}</em>`;
    },
  };
}

export function bar(json: unknown): BarChart {
  const validator = array(
    object({
      date,
      budgets: record(number),
      balance: record(record(number)),
      total_balance: record(number),
    })
  );
  const parsedData = validator(json);
  const currentDateFmt = get(currentDateFormat);
  const data = parsedData.map((d) => ({
    values: get(operatingCurrenciesWithConversion).map((name: string) => ({
      name,
      value: new Map(
        Object.entries(d.balance).map(([k, v]) => [k, v[name] || 0])
      ),
      total_value: d.total_balance[name] || 0,
      budget: d.budgets[name] || 0,
    })),
    date: d.date,
    label: currentDateFmt(d.date),
  }));
  return {
    data,
    tooltipText: (c, d, account) => {
      let text = "";
      d.values.forEach((a) => {
        text += `${c.currency(
          account === null ? a.total_value : a.value.get(account)
        )} ${a.name}`;
        if (a.budget) {
          text += ` / ${c.currency(a.budget)} ${a.name}`;
        }
        text += "<br>";
      });
      text += `<em>${d.label}</em>`;
      text += `<span>${account === null ? "Net" : account}</span>`;
      return text;
    },
    type: "barchart",
  };
}

export function scatterplot(json: unknown): ScatterPlot {
  const validator = array(object({ type: string, date, description: string }));
  return { type: "scatterplot", data: validator(json) };
}

export function hierarchy(json: unknown): HierarchyChart {
  const hierarchyValidator: Validator<AccountHierarchy> = object({
    account: string,
    balance: record(number),
    children: lazy(() => array(hierarchyValidator)),
  });
  const validator = object({ root: hierarchyValidator, modifier: number });
  const { root, modifier } = validator(json);
  addInternalNodesAsLeaves(root);
  const data = new Map<string, AccountHierarchyNode>();

  get(operatingCurrenciesWithConversion).forEach((currency: string) => {
    const currencyHierarchy = d3Hierarchy(root)
      .sum((d) => (d.balance[currency] || 0) * modifier)
      .sort((a, b) => (b.value || 0) - (a.value || 0));
    if (currencyHierarchy.value) {
      data.set(currency, currencyHierarchy);
    }
  });

  return { type: "hierarchy", data };
}

const parsers: Partial<
  Record<string, (json: unknown, label: string) => ChartTypes>
> = {
  balances,
  commodities,
  bar,
  hierarchy,
  scatterplot,
};

export type NamedChartTypes = ChartTypes & {
  name?: string;
};

export function parseChartData(): NamedChartTypes[] {
  const json = getScriptTagJSON("#chart-data");
  const validator = array(
    object({
      label: string,
      type: string,
      data: unknown,
    })
  );
  const chartData = validator(json);
  const result: NamedChartTypes[] = [];
  chartData.forEach((chart) => {
    const parser = parsers[chart.type];
    if (parser) {
      result.push({
        name: chart.label,
        ...parser(chart.data, chart.label),
      });
    }
  });
  return result;
}

export function parseGroupedQueryChart(
  json: unknown,
  currencies: string[]
): HierarchyChart | null {
  const validator = array(object({ group: string, balance: record(number) }));
  const grouped = defaultValue(validator, null)(json);
  if (!grouped) {
    return null;
  }
  const root = stratify(
    grouped,
    (d) => d.group,
    (account, d) => ({ account, balance: d?.balance ?? {} })
  );
  root.account = "(root)";

  const data = new Map<string, AccountHierarchyNode>();
  currencies.forEach((currency: string) => {
    const currencyHierarchy: AccountHierarchyNode = d3Hierarchy(root)
      .sum((d) => d.balance[currency] || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0));
    if (currencyHierarchy.value !== undefined) {
      data.set(currency, currencyHierarchy);
    }
  });

  return { type: "hierarchy", data };
}

/**
 * Parse one of the query result charts.
 * @param json - The chart data to parse.
 */
export function parseQueryChart(
  json: unknown,
  operating_currencies: string[]
): ChartTypes | null {
  const tree = parseGroupedQueryChart(json, operating_currencies);
  if (tree) {
    return tree;
  }
  const dated = defaultValue(array(unknown), null)(json);
  if (dated) {
    try {
      return balances(dated);
    } catch (error) {
      // pass
    }
  }
  return null;
}
