# prompt-eng-hackathon

## Table of contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Structured Output](#structured-output)



## Installation
Clone the repository and create the `.venv`:
```shell
git clone https://github.com/pozzanders/prompt-eng-hackathon.git
cd prompt-eng-hackathon
python -m venv .venv
```

### 1. Activate the virtual environment

NOTE: if you get an error when trying to activate the virtual environment, try first to run the following command in Powershell:
```
Set-ExecutionPolicy -Scope "CurrentUser" -ExecutionPolicy "Unrestricted" 
```

#### Linux
```shell
source venv/bin/activate
```
#### Windows (cmd)
```shell
.venv\Scripts\activate
```
#### Windows (PowerShell)
```shell
.\venv\Scripts\Activate.ps1
```

### 2. Install the dependencies
We have prepared some basica packages to run the code, which you can install by running in a terminal the following:
```shell
pip install -r requirements.txt
```

Lastly, create a file `.env` as a copy of the template `env-temp`
and substitute `<TOKEN>` with the OpenAI API key _(provided by Isabella via Keeper)_.


## Getting Started
To launch the application we make use of streamlit. The entry file is the [main.py](src/main.py) file:
```shell
streamlit run src/main.py
```
Now you can open your favorite browser, type `localhost:8501` in the search bar, and start chatting with the LLM!

#### Modifications
The following file(s) will contain your main work:
- [guardrails.py](src/guardrails.py)
- [schema.py](src/schema.py)
- [templates.py](src/schema.py)
- [chatbot.py](src/chatbot.py)
- [parameters.py](src/parameters.py)

The following files should **NOT** be modified by you:
- [backend.py](src/backend.py)
- [main.py](src/main.py)

### Implementing your own guardrails
The file [guardrails.py](src/guardrails.py) is where you will create your custom guardrails. In this file you will 
find two classes, `InputGuardRail` and `OutputGuardRail`. As the names already suggest, the InputGuardRail is invoked
on any user **input** while the OutputGuardRail is invoked on any chatbot **output**. Both classes only have two functions,
the `__init__` function and the `check` function. The `check` function is used in the [backend.py](src/backend.py) file
which should not be modified by you. Both functions are explained further below, with the help of some existing
guardrail examples which you can find in the [example_guardrails.py](src/example_guardrails.py) file.



#### \_\_init__()
This function takes no arguments and is used to initialize attributes if any. As this is just small program for
a hackathon hardcoding parameters is just fine. For example, the `InputGuardRail_example2` (in [examples](src/example_guardrails.py)) initializes
an OpenAI client to a chatbot (which is **different** from the main chatbot) that can be used for validation:
```python
class InputGuardRail_example2:
    def __init__(self):
        self.classifier = ProfanityClassifierBot()
```
The `ProfanityClassifierBot` ([chatbot.py](src/chatbot.py)) is a simple implementation that checks any given text for
profanity. It is explained further [below](#structured-ouput) in detail.
In the **init** function you can initialize all the tools that you need for your guardrail.

#### check(str)
This function takes one input, namely the prompt (str) on which the guardrail is invoked.
**Note:** While there is only _one_ class (and also only one object of that class) of each guardrail, your
custom logic in the `check` function can implement several (inner) 'guardrails'! In other words, the code in
[backend.py](src/backend.py) will only have one object of `InputGuardRail` and only one object of `OutputGuardRail`.
Their `check` functions are invoked once: once for the user input (using the `InputGuardRail`) and once
for the LLM output (using the `OutputGuardRail`). However, your code for the `check` function can implement several
steps that do a certain validation on the given prompt (and for each validation step you essentially create
a 'guardrail' inside the `check` function). These validation steps can be independent of each other.

An Example (very simple profanity filter, not very useful in practice):
```python
def check(text: str):
    if "asshole" in text:  # One 'guardrail'
        text = text.replace("asshole", "nice person")
    if "stupid" in text:   # Another 'guardrail'
        text = text.replace("stupid", "smart")
    # etc ...
    # Rest is truncated
```

The check function also has to return an object of the `GuardRailResponse` class (found in [schema.py](src/schema.py)):
```python
from pydantic import BaseModel

class GuardRailResponse(BaseModel):
    triggered: bool
    rewritten: str
    fallback: Optional[str] # Optional means it can be either a string or None.
    reason: str
```
The fields of that class are:
1) **triggered:** If the guard rail triggered (for example there was profanity in the text).
2) **rewritten:** The rewritten text. Often, rewriting is not necessary. In that case use empty string (`""`).
3) **fallback:** A fallback message to be displayed in the UI chat. Can be `None`.
4) **reason:** The reason of the trigger. If not triggered then empty string should be given.

Triggered guardrails change a bit the treatment of input and output messages:
- **Input & Output:** Fallbacks will always take precedence if they are not `None`, i.e., they contain a message (str). In this case
  the fallback message is written to the UI chat, and **no** message will be retained in the LLM chat history.
  **Note:** We make a distinction here between '_UI chat_' and '_LLM chat history_'. The LLM chat history
  contains all messages that are always sent to the LLM chatbot (in the [backend.py](src/backend.py)) each time
  the LLM chatbot is queried. The UI chat contains all messages, visualized in the browser.
- **Input:** If there is no fallback then the _original_ input will be displayed in the UI chat but the _rewritten_ input will
  be used in the LLM chat history.
- **Output:** If there is no fallback then the _rewritten_ output will be displayed in the UI chat, and the _rewritten_ output will
  be used in the LLM chat history.
- **Input & Output:** If there is no fallback then the message will have a red triangle appended with a tooltip displaying
  the reason for the trigger.

Whether you decide to exclude a sentence from the history (by providing a fallback) will have an impact on the LLM behaviour. Sometimes
it is good to block a prompt completely, and sometimes it is better to rewrite it. There are many reasons to rewrite a prompt.
For example, you want to make sure you provide a well-structured input text to your chatbot, or you want to anonymize personal
information in the output.

Let's complete the above `check` example to show you how to return an object of the class `GuardRailResponse`:
```python
# Not the prettiest implementation
def check(text: str):
    triggered = False
    if "asshole" in text:
        text = text.replace("asshole", "nice person")
        triggered = True
    if "stupid" in text:
        text = text.replace("stupid", "smart")
        triggered = True
    if triggered:
        return GuardRailResponse(
            triggered=True, 
            rewritten=text, 
            fallback=None,
            reason="Contains swearwords."
        )
    else:
        return GuardRailResponse(
            triggered=False, 
            rewritten="", # Can be empty string only if it didn't trigger
            fallback=None,
            reason="",
        )
```

#### Backend LLM parameters
In the file [parameters.py](src/parameters.py) you can modify the `TEMPERATURE` and `SYSTEM_MESSAGE` of your backend chatbot.
- **TEMPERATURE**: Determines the 'creativity' of your LLM chatbot. Acceptable values are 0.0 to 2.0.
  0.0 means **no** creativity.
- **SYSTEM_MESSAGE**: This is a special type of message that lets you define the behaviour of
  your LLM chatbot. For example, it can contain a set of rules that the LLM chatbot must follow.


### Structured Output
The class `ProfanityClassifierBot` in [chatbot.py](src/chatbot.py) is an example implementation
of how to use an LLM as a guardrail. Note that this chatbot (`ProfanityClassifierBot`) is a different bot than the 'LLM chatbot'
mentioned in the previous sections, although they might use the same GPT model in the API.
To make this approach reliable we use a feature called [**structured output**](https://platform.openai.com/docs/guides/structured-outputs).
Essentially, we are enforcing the `ProfanityClassifierBot` to return its answer in a given format, namely a Json structure.
To make the definitions of such a structure easy we also use `pydantic`'s `BaseModel` class to define our own
class. Two classes are already implemented in [schema.py](src/schema.py):
```python
from typing import Optional
from pydantic import BaseModel

class GuardRailResponse(BaseModel):
    triggered: bool
    rewritten: str
    fallback: Optional[str]
    reason: str

class BinaryClassificationResponse(BaseModel):
    result: bool
    reason: str
```
Let's look at `BinaryClassificationResponse`. What this represents is a dictionary with two fields, one that has
a boolean and one that has a string as their respective values. An example:
```python
{
    "result": False, 
    "reason": "This sentence does not contain any profanity"
}
```
With this we can always expect this dictionary format from the `ProfanityClassifierBot` class.
The relevant pieces of code in [chatbot.py](src/chatbot.py):
```python
class ProfanityClassifierBot:
    # ...

    def classify(self, user_text: str) -> BaseModel:
        # ...
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt}
            ],
            response_format=BinaryClassificationResponse, # The desired Format used here
            temperature=0.0
        )
        # ...
```
The `BinaryClassificationResponse` already covers a wide range of applications (mainly validations).
If you implemented a custom format, and you want to use it then you have to modify the relevant line:
```python
    # ...
    response_format=BinaryClassificationResponse, # Replace this with your custom schema
    # ...
```

Lastly, it is also good to mention in the prompt that you send to the `ProfanityClassifierBot` what format you expect.
The function `format_profanity_classification_template` in [templates.py](src/templates.py) gives you an example.
Feel free to reuse it.

A note on implementations. If you plan on implementing your own formats (schemas) and prompts, you can place these
in [schema.py](src/schema.py) and [templates.py](src/templates.py), respectively. This keeps your code tidy :).