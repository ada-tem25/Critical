"""
Prompts package — re-exports all prompt strings for backward compatibility.
"""
from prompts.decomposer import decomposer_instructions, decomposer_corrector_instructions
from prompts.rhetoric import rhetoric_detector_instructions, rhetoric_reviewer_instructions
from prompts.queries import (
    generate_queries_l2_instructions,
    generate_queries_l3_instructions,
    generate_queries_l4_instructions,
)
from prompts.synthesizing import synthesizer_l2_instructions
from prompts.reflection import reflection_agent_instructions
