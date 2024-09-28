"""OpenAI module"""

from openai import AzureOpenAI


class OpenAi:
    """OpenAi class"""

    def __init__(
        self,
        endpoint,
        key,
        model="gpt-4o",
    ):
        self.endpoint = endpoint
        self.key = key
        self.model = model

    def open_ai_run(
        self,
        prompt: str,
        system: str = None,
        temperature: int = 0,
        max_tokens: int = 1000,
    ):
        """OpenAI run method"""

        client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.key,
            api_version="2024-02-01",
        )

        messages = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        completion = client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=messages,
            max_tokens=max_tokens,
        )

        return completion.choices[0].message.content
