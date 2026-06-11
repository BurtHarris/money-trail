-- Operating expenditures staging model
-- Cleans and aliases raw FEC operating expenditure data

{{ config(materialized='view') }}

{% set cycles = [2024, 2022, 2020] %}

with all_cycles as (
  {% for cycle in cycles %}
    select
      cmte_id,
      amndt_ind,
      rpt_yr,
      rpt_tp,
      image_num,
      line_num,
      form_tp_cd,
      sched_tp_cd,
      name,
      city,
      state,
      zip_code,
      try_strptime(nullif(trim(transaction_dt), ''), '%m%d%Y')::date as transaction_dt,
      try_cast(nullif(trim(transaction_amt), '') as decimal(14,2)) as transaction_amt,
      transaction_pgi,
      purpose,
      category,
      category_desc,
      memo_cd,
      memo_text,
      entity_tp,
      try_cast(nullif(trim(sub_id), '') as bigint) as sub_id,
      try_cast(nullif(trim(file_num), '') as bigint) as file_num,
      tran_id,
      back_ref_tran_id,
      {{ cycle }} as cycle
    from raw.oppexp_{{ cycle }}
    {% if not loop.last %}union all{% endif %}
  {% endfor %}
)

select * from all_cycles
