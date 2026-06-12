-- Committee-to-committee transfers staging model
-- Cleans and aliases raw FEC committee-to-committee transfer data

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
      name,
      city,
      state,
      zip_code,
      employer,
      occupation,
      try_strptime(nullif(trim(transaction_dt), ''), '%m%d%Y')::date as transaction_dt,
      try_cast(nullif(trim(transaction_amt), '') as decimal(14,2)) as transaction_amt,
      other_id,
      tran_id,
      try_cast(nullif(trim(file_num), '') as bigint) as file_num,
      memo_cd,
      memo_text,
      try_cast(nullif(trim(sub_id), '') as bigint) as sub_id,
      {{ cycle }} as cycle
    from raw.oth_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
