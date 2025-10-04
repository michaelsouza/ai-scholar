---
title: Quickstart
subtitle: Get started with OpenRouter
slug: quickstart
headline: OpenRouter Quickstart Guide | Developer Documentation
canonical-url: 'https://openrouter.ai/docs/quickstart'
'og:site_name': OpenRouter Documentation
'og:title': OpenRouter Quickstart Guide
'og:description': >-
  Get started with OpenRouter's unified API for hundreds of AI models. Learn how
  to integrate using OpenAI SDK, direct API calls, or third-party frameworks.
'og:image':
  type: url
  value: >-
    https://openrouter.ai/dynamic-og?pathname=quickstart&title=Quick%20Start&description=Start%20using%20OpenRouter%20API%20in%20minutes%20with%20any%20SDK
'og:image:width': 1200
'og:image:height': 630
'twitter:card': summary_large_image
'twitter:site': '@OpenRouterAI'
noindex: false
nofollow: false
---

OpenRouter provides a unified API that gives you access to hundreds of AI models through a single endpoint, while automatically handling fallbacks and selecting the most cost-effective options. Get started with just a few lines of code using your preferred SDK or framework.

<Tip>
  Looking for information about free models and rate limits? Please see the [FAQ](/docs/faq#how-are-rate-limits-calculated)
</Tip>

In the examples below, the OpenRouter-specific headers are optional. Setting them allows your app to appear on the OpenRouter leaderboards. For detailed information about app attribution, see our [App Attribution guide](/docs/features/app-attribution).

## Using the OpenAI SDK

<CodeGroup>

```python title="Python"
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  model="openai/gpt-4o",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)

print(completion.choices[0].message.content)
```

```typescript title="TypeScript"
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: '<OPENROUTER_API_KEY>',
  defaultHeaders: {
    'HTTP-Referer': '<YOUR_SITE_URL>', // Optional. Site URL for rankings on openrouter.ai.
    'X-Title': '<YOUR_SITE_NAME>', // Optional. Site title for rankings on openrouter.ai.
  },
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: 'openai/gpt-4o',
    messages: [
      {
        role: 'user',
        content: 'What is the meaning of life?',
      },
    ],
  });

  console.log(completion.choices[0].message);
}

main();
```

</CodeGroup>

## Using the OpenRouter API directly

<Tip>
  You can use the interactive [Request Builder](/request-builder) to generate OpenRouter API requests in the language of your choice.
</Tip>

<CodeGroup>

```python title="Python"
import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer <OPENROUTER_API_KEY>",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "openai/gpt-4o", # Optional
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ]
  })
)
```

```typescript title="TypeScript"
fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    Authorization: 'Bearer <OPENROUTER_API_KEY>',
    'HTTP-Referer': '<YOUR_SITE_URL>', // Optional. Site URL for rankings on openrouter.ai.
    'X-Title': '<YOUR_SITE_NAME>', // Optional. Site title for rankings on openrouter.ai.
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'openai/gpt-4o',
    messages: [
      {
        role: 'user',
        content: 'What is the meaning of life?',
      },
    ],
  }),
});
```

```shell title="Shell"
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
}'
```

</CodeGroup>

The API also supports [streaming](/docs/api-reference/streaming).

## Using third-party SDKs

For information about using third-party SDKs and frameworks with OpenRouter, please [see our frameworks documentation.](/docs/community/frameworks-overview)

---
title: Parameters
headline: API Parameters | Configure OpenRouter API Requests
canonical-url: 'https://openrouter.ai/docs/api-reference/parameters'
'og:site_name': OpenRouter Documentation
'og:title': API Parameters - Complete Guide to Request Configuration
'og:description': >-
  Learn about all available parameters for OpenRouter API requests. Configure
  temperature, max tokens, top_p, and other model-specific settings.
'og:image':
  type: url
  value: >-
    https://openrouter.ai/dynamic-og?title=API%20Parameters&description=Complete%20guide%20to%20request%20configuration
'og:image:width': 1200
'og:image:height': 630
'twitter:card': summary_large_image
'twitter:site': '@OpenRouterAI'
noindex: false
nofollow: false
---

Sampling parameters shape the token generation process of the model. You may send any parameters from the following list, as well as others, to OpenRouter.

OpenRouter will default to the values listed below if certain parameters are absent from your request (for example, `temperature` to 1.0). We will also transmit some provider-specific parameters, such as `safe_prompt` for Mistral or `raw_mode` for Hyperbolic directly to the respective providers if specified.

Please refer to the model’s provider section to confirm which parameters are supported. For detailed guidance on managing provider-specific parameters, [click here](/docs/features/provider-routing#requiring-providers-to-support-all-parameters-beta).

## Temperature

- Key: `temperature`

- Optional, **float**, 0.0 to 2.0

- Default: 1.0

- Explainer Video: [Watch](https://youtu.be/ezgqHnWvua8)

This setting influences the variety in the model's responses. Lower values lead to more predictable and typical responses, while higher values encourage more diverse and less common responses. At 0, the model always gives the same response for a given input.

## Top P

- Key: `top_p`

- Optional, **float**, 0.0 to 1.0

- Default: 1.0

- Explainer Video: [Watch](https://youtu.be/wQP-im_HInk)

This setting limits the model's choices to a percentage of likely tokens: only the top tokens whose probabilities add up to P. A lower value makes the model's responses more predictable, while the default setting allows for a full range of token choices. Think of it like a dynamic Top-K.

## Top K

- Key: `top_k`

- Optional, **integer**, 0 or above

- Default: 0

- Explainer Video: [Watch](https://youtu.be/EbZv6-N8Xlk)

This limits the model's choice of tokens at each step, making it choose from a smaller set. A value of 1 means the model will always pick the most likely next token, leading to predictable results. By default this setting is disabled, making the model to consider all choices.

## Frequency Penalty

- Key: `frequency_penalty`

- Optional, **float**, -2.0 to 2.0

- Default: 0.0

- Explainer Video: [Watch](https://youtu.be/p4gl6fqI0_w)

This setting aims to control the repetition of tokens based on how often they appear in the input. It tries to use less frequently those tokens that appear more in the input, proportional to how frequently they occur. Token penalty scales with the number of occurrences. Negative values will encourage token reuse.

## Presence Penalty

- Key: `presence_penalty`

- Optional, **float**, -2.0 to 2.0

- Default: 0.0

- Explainer Video: [Watch](https://youtu.be/MwHG5HL-P74)

Adjusts how often the model repeats specific tokens already used in the input. Higher values make such repetition less likely, while negative values do the opposite. Token penalty does not scale with the number of occurrences. Negative values will encourage token reuse.

## Repetition Penalty

- Key: `repetition_penalty`

- Optional, **float**, 0.0 to 2.0

- Default: 1.0

- Explainer Video: [Watch](https://youtu.be/LHjGAnLm3DM)

Helps to reduce the repetition of tokens from the input. A higher value makes the model less likely to repeat tokens, but too high a value can make the output less coherent (often with run-on sentences that lack small words). Token penalty scales based on original token's probability.

## Min P

- Key: `min_p`

- Optional, **float**, 0.0 to 1.0

- Default: 0.0

Represents the minimum probability for a token to be
  considered, relative to the probability of the most likely token. (The value changes depending on the confidence level of the most probable token.) If your Min-P is set to 0.1, that means it will only allow for tokens that are at least 1/10th as probable as the best possible option.

## Top A

- Key: `top_a`

- Optional, **float**, 0.0 to 1.0

- Default: 0.0

Consider only the top tokens with "sufficiently high" probabilities based on the probability of the most likely token. Think of it like a dynamic Top-P. A lower Top-A value focuses the choices based on the highest probability token but with a narrower scope. A higher Top-A value does not necessarily affect the creativity of the output, but rather refines the filtering process based on the maximum probability.

## Seed

- Key: `seed`

- Optional, **integer**

If specified, the inferencing will sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed for some models.

## Max Tokens

- Key: `max_tokens`

- Optional, **integer**, 1 or above

This sets the upper limit for the number of tokens the model can generate in response. It won't produce more than this limit. The maximum value is the context length minus the prompt length.

## Logit Bias

- Key: `logit_bias`

- Optional, **map**

Accepts a JSON object that maps tokens (specified by their token ID in the tokenizer) to an associated bias value from -100 to 100. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.

## Logprobs

- Key: `logprobs`

- Optional, **boolean**

Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned.

## Top Logprobs

- Key: `top_logprobs`

- Optional, **integer**

An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability. logprobs must be set to true if this parameter is used.

## Response Format

- Key: `response_format`

- Optional, **map**

Forces the model to produce specific output format. Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the message the model generates is valid JSON.

  **Note**: when using JSON mode, you should also instruct the model to produce JSON yourself via a system or user message.

## Structured Outputs

- Key: `structured_outputs`

- Optional, **boolean**

If the model can return structured outputs using response_format json_schema.

## Stop

- Key: `stop`

- Optional, **array**

Stop generation immediately if the model encounter any token specified in the stop array.

## Tools

- Key: `tools`

- Optional, **array**

Tool calling parameter, following OpenAI's tool calling request shape. For non-OpenAI providers, it will be transformed accordingly. [Click here to learn more about tool calling](/docs/requests#tool-calls)

## Tool Choice

- Key: `tool_choice`

- Optional, **array**

Controls which (if any) tool is called by the model. 'none' means the model will not call any tool and instead generates a message. 'auto' means the model can pick between generating a message or calling one or more tools. 'required' means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

## Parallel Tool Calls

- Key: `parallel_tool_calls`

- Optional, **boolean**

- Default: **true**

Whether to enable parallel function calling during tool use. If true, the model can call multiple functions simultaneously. If false, functions will be called sequentially. Only applies when tools are provided.

## Verbosity

- Key: `verbosity`

- Optional, **enum** (low, medium, high)

- Default: **medium**

Controls the verbosity and length of the model response. Lower values produce more concise responses, while higher values produce more detailed and comprehensive responses.
