"""
Prompts package — re-exports all prompt strings for backward compatibility.
"""
from prompts.decomposer import decomposer_instructions, decomposer_corrector_instructions
from prompts.queries import (
    fact_checking_queries_instructions,
    opinion_analysis_queries_instructions,
    interpretive_analysis_queries_instructions,
)
