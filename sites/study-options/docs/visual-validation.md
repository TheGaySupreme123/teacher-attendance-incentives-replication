# Visual validation — 22 September 2026

- Source counts reconstructed from verified aggregate outputs: nonwriter control290/858, program365/940; writer control89/201, program138/196. Rates33.8%,38.8%,44.3%,70.4%. Each pie's complement and denominator are explicit; equal-sized pies do not imply equal sample size.
- Original published-outcome replication anchor8.4percentage points uses2197children, distinct from2195linkedchildren. Direct interaction21.1points remains a difference between treatment effects.
- Source quality flags give85code-only,117short-history-only,28both,1965neither; sum2195, union230. No overlap double-counting and no claim that absence of these two flags certifies data quality.
- CI plots preserve exact source endpoints and use a common -10to50 percentage-point domain. No interval is clipped. Zero line is explicit. Data bounds are not drawn as confidence intervals.
- All five visual modes render without undefined/NaN values. Desktop1440 and mobile390 reviewed with screenshots; mobile page width390, no unintended document overflow. Four pie labels and exact denominators verified in renderedDOM.
- Browser Back/Forward restores chart mode through URL parameters; Bars/Pies control works. New page tools read aggregate chart data and select visual views. All essential values are visible without hover.
- SVG/DOM charts use no runtime external dependencies or network data fetches. No raw individual records uploaded. Existing detailed tables and caveats remain available below the visual explorer.
