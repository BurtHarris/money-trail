-- Committee master staging model
-- Cleans and aliases raw FEC committee master data
--
-- Normalization:
-- - ZIP codes truncated to 5 digits
-- - Whitespace trimmed from text fields
-- - NULL values standardized

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cmte_id,
      trim(cmte_nm) as cmte_nm,
      trim(tres_nm) as tres_nm,
      trim(cmte_st1) as cmte_st1,
      trim(cmte_st2) as cmte_st2,
      trim(cmte_city) as cmte_city,
      trim(cmte_st) as cmte_st,
      left(trim(cmte_zip), 5) as cmte_zip,
      trim(cmte_dsgn) as cmte_dsgn,
      trim(cmte_tp) as cmte_tp,
      trim(cmte_pty_affiliation) as cmte_pty_affiliation,
      trim(cmte_filing_freq) as cmte_filing_freq,
      trim(org_tp) as org_tp,
      trim(connected_org_nm) as connected_org_nm,
      cand_id,
      {{ cycle }} as cycle
    from raw.cm_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
