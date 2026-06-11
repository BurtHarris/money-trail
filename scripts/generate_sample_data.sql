-- Generate sample FEC individual contributions data as parquet
-- This creates a minimal but valid sample matching the FEC bulk download format
-- Output: data/duckdb/sample_indiv_2024.parquet

-- Create sample individual contributions data
CREATE TABLE sample_indiv_2024 AS
SELECT 
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
  transaction_dt,
  transaction_amt,
  other_id,
  tran_id,
  file_num,
  memo_cd,
  memo_text,
  sub_id
FROM (
  VALUES
    ('C00123456', 'N', 'M1', 'G', '1234567', '15', 'IND', 'SMITH, JOHN', 'NEW YORK', 'NY', '10001', 'ACME CORP', 'MANAGER', '01152024', '500.00', '', 'SA11AI.1000', '123456', '', '', '1'),
    ('C00789012', 'N', 'M2', 'P', '1234568', '15', 'IND', 'DOE, JANE', 'SAN FRANCISCO', 'CA', '94102', 'TECH SOLUTIONS LLC', 'ENGINEER', '02202024', '1000.00', '', 'SA11AI.1001', '123456', 'X', 'Memo item', '2'),
    ('C00345678', 'A', 'M1', 'G', '1234569', '15', 'IND', 'WILLIAMS, ROBERT', 'CHICAGO', 'IL', '60601', 'MIDWEST HOLDINGS', 'EXECUTIVE', '03102024', '250.50', '', 'SA11AII.1000', '123457', '', '', '3'),
    ('C00901234', 'N', 'M3', '', '1234570', '15', 'IND', 'JOHNSON, MARIA', 'DALLAS', 'TX', '75201', 'RETAIL PLUS', 'CONSULTANT', '04052024', '2700.00', '', 'SA11AI.1002', '123456', '', '', '4')
) AS t(cmte_id, amndt_ind, rpt_tp, transaction_pgi, image_num, transaction_tp, entity_tp, name, city, state, zip_code, employer, occupation, transaction_dt, transaction_amt, other_id, tran_id, file_num, memo_cd, memo_text, sub_id);

-- Export to parquet file
COPY sample_indiv_2024 TO 'sample_indiv_2024.parquet' (FORMAT PARQUET);

-- Display success message
SELECT 'Sample parquet file generated: sample_indiv_2024.parquet' as status;
