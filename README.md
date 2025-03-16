# Extendable Agent

An Agentic platform that allows you to define extensions.


## Showcase

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://extendable-agent.streamlit.app/)

https://github.com/user-attachments/assets/9a79798c-62c0-4785-be63-8e6335846ff5

![Screenshot 2025-03-16 at 03 19 38](https://github.com/user-attachments/assets/e5100ee5-3c5d-4664-a921-0587c217d316)

You can also define output schema through Pydantic data models, and then you can ask the chatbot to generate structured outputs.
```python
import datetime
from pydantic import BaseModel
from pydantic import Field


class TimeNow(BaseModel):
    """Output format when displaying time."""

    date: datetime.date = Field(..., description="The date")
    time: datetime.time = Field(..., description="The time")
```


## Installation

```bash
uv sync
```

## Usage

```bash
streamlit run app.py

```
