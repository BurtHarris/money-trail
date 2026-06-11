#!/usr/bin/env python3
"""
Generate sample FEC individual contributions parquet file for testing and documentation.

This script creates a minimal but valid sample of FEC indiv data matching the schema
used by the money-trail pipeline. The sample includes a few realistic records that
demonstrate the data structure and enable local testing without requiring full FEC downloads.
"""

import os
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq


def generate_sample_indiv_data():
    """
    Generate sample individual contributions data matching FEC bulk download format.
    
    Returns:
        pyarrow.Table: Sample data with FEC column names (as-is from raw download)
    """
    
    # FEC column names (as they appear in raw downloads)
    columns = {
        'cmte_id': pa.array(['C00123456', 'C00789012', 'C00345678', 'C00901234']),
        'amndt_ind': pa.array(['N', 'N', 'A', 'N']),
        'rpt_tp': pa.array(['M1', 'M2', 'M1', 'M3']),
        'transaction_pgi': pa.array(['G', 'P', 'G', '']),
        'image_num': pa.array(['1234567', '1234568', '1234569', '1234570']),
        'transaction_tp': pa.array(['15', '15', '15', '15']),  # 15 = individual contribution
        'entity_tp': pa.array(['IND', 'IND', 'IND', 'IND']),   # Individual
        'name': pa.array(['SMITH, JOHN', 'DOE, JANE', 'WILLIAMS, ROBERT', 'JOHNSON, MARIA']),
        'city': pa.array(['NEW YORK', 'SAN FRANCISCO', 'CHICAGO', 'DALLAS']),
        'state': pa.array(['NY', 'CA', 'IL', 'TX']),
        'zip_code': pa.array(['10001', '94102-5678', '60601', '75201']),
        'employer': pa.array(['ACME CORP', 'TECH SOLUTIONS LLC', 'MIDWEST HOLDINGS', 'RETAIL PLUS']),
        'occupation': pa.array(['MANAGER', 'ENGINEER', 'EXECUTIVE', 'CONSULTANT']),
        'transaction_dt': pa.array(['01152024', '02202024', '03102024', '04052024']),  # MMDDYYYY format
        'transaction_amt': pa.array(['500.00', '1000.00', '250.50', '2700.00']),
        'other_id': pa.array(['', '', '', '']),
        'tran_id': pa.array(['SA11AI.1000', 'SA11AI.1001', 'SA11AII.1000', 'SA11AI.1002']),
        'file_num': pa.array(['123456', '123456', '123457', '123456']),
        'memo_cd': pa.array(['', 'X', '', '']),
        'memo_text': pa.array(['', 'Memo item', '', '']),
        'sub_id': pa.array(['1', '2', '3', '4']),
    }
    
    return pa.table(columns)


def main():
    """Generate and write sample parquet file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data', 'duckdb')
    output_file = os.path.join(data_dir, 'sample_indiv_2024.parquet')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate sample data
    print("Generating sample FEC individual contributions data...")
    table = generate_sample_indiv_data()
    
    # Write to parquet
    pq.write_table(table, output_file)
    
    print(f"✓ Sample parquet file created: {output_file}")
    print(f"  Schema: {len(table.column_names)} columns, {len(table)} rows")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    return 0


if __name__ == '__main__':
    exit(main())
