"""Streamlit entrypoint.

Streamlit re-executes this file after every widget interaction. ``run_module``
therefore intentionally executes the UI module each time instead of importing
it once and receiving a cached module on subsequent reruns.
"""
from runpy import run_module

run_module("src.ui.streamlit_app", run_name="__main__")
