-- Individual contributions staging model
-- Cleans and aliases raw FEC individual contributions data
-- Unions all cycles of raw_indiv_* external tables (created by Airflow from parquet files)
--
-- Normalization:
-- - ZIP codes truncated to 5 digits
-- - Amounts rounded to 2 decimals
-- - Whitespace trimmed from text fields
-- - NULL values standardized

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cmte_id,
      amndt_ind,
      rpt_tp,
      transaction_pgi,
      image_num,
      transaction_tp,
      entity_tp,
      trim(name) as name,
      trim(city) as city,
      trim(state) as state,
      left(trim(zip_code), 5) as zip_code,
      trim(employer) as employer,
      trim(occupation) as occupation,
      try_strptime(nullif(trim(transaction_dt), ''), '%m%d%Y')::date as transaction_dt,
      round(try_cast(nullif(trim(transaction_amt), '') as decimal(14,2)), 2) as transaction_amt,
      trim(other_id) as other_id,
      trim(tran_id) as tran_id,
      try_cast(nullif(trim(file_num), '') as bigint) as file_num,
      trim(memo_cd) as memo_cd,
      trim(memo_text) as memo_text,
      try_cast(nullif(trim(sub_id), '') as bigint) as sub_id,
      {{ cycle }} as cycle
    from raw.indiv_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
