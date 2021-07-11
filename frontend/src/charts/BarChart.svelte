<script lang="ts">
  import { extent, filter, merge, sum } from "d3-array";
  import { axisBottom, axisLeft } from "d3-axis";
  import { scaleBand, scaleLinear, scaleOrdinal } from "d3-scale";
  import { stack, stackOffsetDiverging } from "d3-shape";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  import { ctx } from "../format";
  import { urlFor } from "../helpers";
  import router from "../router";

  import { axis } from "./axis";
  import { filterTicks, hclColorRange } from "./helpers";
  import { followingTooltip } from "./tooltip";

  import type { BarChart, BarChartDatumValue } from ".";

  export let data: BarChart["data"];
  export let width: number;
  export let tooltipText: BarChart["tooltipText"];

  const today = new Date();
  $: accounts = Array.from(
    new Set(
      data
        .map((x) => x.values.map((y_) => Array.from(y_.value.keys())).flat())
        .flat()
    )
  );

  const maxColumnWidth = 100;
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  const height = 250;
  $: innerHeight = height - margin.top - margin.bottom;
  $: maxWidth = data.length * maxColumnWidth;
  $: offset = margin.left + Math.max(0, width - maxWidth) / 2;
  $: innerWidth = Math.min(width - margin.left - margin.right, maxWidth);

  const netValueMarkerHeight = 6;

  // Scales
  $: x0 = scaleBand()
    .padding(0.1)
    .domain(data.map((d) => d.label))
    .range([0, innerWidth]);
  $: x1 = scaleBand()
    .domain(data[0].values.map((d) => d.name))
    .range([0, x0.bandwidth()]);
  let yMin = 0;
  let yMax = 0;
  $: [yMin = 0, yMax = 0] = extent(
    merge<BarChartDatumValue>(
      data
        .map((d) => [
          d.values.map((r) => sum(filter(r.value.values(), (v) => v > 0))),
          d.values.map((r) => sum(filter(r.value.values(), (v) => v < 0))),
        ])
        .flat()
    )
  );
  $: y = scaleLinear()
    .range([innerHeight, 0])
    .domain([Math.min(0, yMin), Math.max(0, yMax)]);
  $: colorScale = scaleOrdinal()
    .domain(accounts)
    .range(hclColorRange(accounts.length, 45, 80));

  $: barData = stack()
    .keys(accounts)
    .value((d, key) =>
      // FIXME: Multiple currencies?
      d.values[0].value.get(key)
    )
    .offset(stackOffsetDiverging)(data);

  const legend: Writable<[string, string][]> = getContext("chart-legend");
  $: legend.set(accounts.sort().map((a) => [a, colorScale(a)]));

  // Axes
  $: xAxis = axisBottom(x0)
    .tickSizeOuter(0)
    .tickValues(filterTicks(x0.domain(), innerWidth / 70));
  $: yAxis = axisLeft(y).tickSize(-innerWidth).tickFormat($ctx.short);

  let highlighted = "";
</script>

<svg {width} {height}>
  <g transform={`translate(${offset},${margin.top})`}>
    <g
      class="x axis"
      use:axis={xAxis}
      transform={`translate(0,${innerHeight})`}
    />
    <g class="y axis" use:axis={yAxis} />
    {#each barData as account}
      <g
        class="category"
        class:highlighted={account.key === highlighted || highlighted === ""}
        class:faded={account.key !== highlighted && highlighted !== ""}
      >
        {#each account as bar}
          {#if !Number.isNaN(bar[1])}
            <rect
              class:desaturate={bar.data.date > today}
              width={x1.bandwidth()}
              x={x0(bar.data.label)}
              y={bar[0] > 0 ? y(bar[1]) : y(bar[1])}
              height={Math.abs(y(bar[1]) - y(bar[0]))}
              fill={colorScale(account.key)}
              on:mouseover={() => {
                highlighted = account.key;
              }}
              on:mouseout={() => {
                highlighted = "";
              }}
              use:followingTooltip={() =>
                tooltipText($ctx, bar.data, account.key)}
              on:click={() =>
                router.navigate(urlFor(`account/${account.key}/`))}
            />
          {/if}
        {/each}
      </g>
    {/each}
    <g class="budget">
      {#each data as v}
        {#if v.values[0].budget !== 0}
          <rect
            width={x1.bandwidth()}
            x={x0(v.label)}
            y={y(Math.max(0, v.values[0].budget))}
            height={Math.abs(y(v.values[0].budget) - y(0))}
          />
        {/if}
      {/each}
    </g>
    <g class="net" class:highlighted={highlighted === "Net"}>
      {#each data as v}
        <rect
          width={x1.bandwidth()}
          x={x0(v.label)}
          y={y(v.values[0].total_value) - netValueMarkerHeight / 2}
          height={netValueMarkerHeight}
          on:mouseover={() => {
            highlighted = "Net";
          }}
          on:mouseout={() => {
            highlighted = "";
          }}
          use:followingTooltip={() => tooltipText($ctx, v, null)}
        />
      {/each}
    </g>
  </g>
</svg>

<style>
  .category.faded {
    opacity: 0.5;
  }

  rect {
    cursor: pointer;
  }

  .budget rect {
    fill: none;
    stroke: black;
    stroke-dasharray: 2;
    stroke-opacity: 0.5;
    stroke-width: 1;
  }

  .net rect {
    opacity: 0.4;
  }

  .net.highlighted rect {
    opacity: 0.8;
  }
  .desaturate {
    filter: saturate(50%);
  }
</style>
