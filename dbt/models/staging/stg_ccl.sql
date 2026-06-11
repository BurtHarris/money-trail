-- Candidate-committee linkage staging model
-- Cleans and aliases raw FEC linkage data

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cand_id,
      try_cast(
        case
          when length(trim(cand_election_yr)) = 4 then trim(cand_election_yr)
          else null
        end as smallint
      ) as cand_election_yr,
      try_cast(
        case
          when length(trim(fec_election_yr)) = 4 then trim(fec_election_yr)
          else null
        end as smallint
      ) as fec_election_yr,
      cmte_id,
      cmte_tp,
      cmte_dsgn,
      try_cast(nullif(trim(linkage_id), '') as bigint) as linkage_id,
      {{ cycle }} as cycle
    from raw.ccl_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
