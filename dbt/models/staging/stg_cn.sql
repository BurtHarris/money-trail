-- Candidate master staging model
-- Cleans and aliases raw FEC candidate master data
--
-- Normalization:
-- - ZIP codes truncated to 5 digits
-- - Election year parsed as smallint with validation
-- - Whitespace trimmed from text fields
-- - NULL values standardized

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cand_id,
      trim(cand_name) as cand_name,
      trim(cand_pty_affiliation) as cand_pty_affiliation,
      try_cast(
        case
          when length(trim(cand_election_yr)) = 4 then trim(cand_election_yr)
          else null
        end as smallint
      ) as cand_election_yr,
      trim(cand_office_st) as cand_office_st,
      trim(cand_office) as cand_office,
      trim(cand_office_district) as cand_office_district,
      trim(cand_ici) as cand_ici,
      trim(cand_status) as cand_status,
      trim(cand_pcc) as cand_pcc,
      trim(cand_st1) as cand_st1,
      trim(cand_st2) as cand_st2,
      trim(cand_city) as cand_city,
      trim(cand_st) as cand_st,
      left(trim(cand_zip), 5) as cand_zip,
      {{ cycle }} as cycle
    from raw.cn_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
