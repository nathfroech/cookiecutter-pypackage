"""
Global settings for project.

May be just some literals, or path-related values.
{%- if cookiecutter.use_environment_based_settings %}

All environment-based settings should be declared here too.
{%- endif %}
"""

import pathlib
{%- if cookiecutter.use_environment_based_settings %}

from dotenv import load_dotenv
from environs import Env

load_dotenv()

env = Env()
env.read_env()
{%- endif %}

BASE_DIR = pathlib.Path(__file__).resolve().parent
