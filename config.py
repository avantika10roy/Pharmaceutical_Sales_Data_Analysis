import streamlit as st
class Config:
    RAW_DATA       = 'data/pharma-data.csv'
    PROCESSED_DATA = 'data/preprocessed_data.csv'
    COLOR_PALETTE  = 'Alphabet'

    CSS            = """
                        <style>
                            .stat-box {
                                background-color: #f9f9f9;
                                border-radius: 12px;
                                padding: 20px;
                                text-align: center;
                                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
                                transition: transform 0.2s ease, box-shadow 0.2s ease;
                                cursor: pointer;
                            }

                            .stat-box:hover {
                                transform: translateY(-5px);
                                box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.1);
                                background-color: #f0f0ff;
                            }

                            .stat-box h3 {
                                margin: 0;
                                font-size: 2rem;
                                color: #4A90E2;
                            }

                            .stat-box small {
                                font-size: 0.85rem;
                                color: #666;
                            }
                        </style>
                    """