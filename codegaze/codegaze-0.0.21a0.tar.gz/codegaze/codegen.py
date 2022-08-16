from abc import abstractmethod

from abc import ABC, abstractmethod
from typing import Any
from codegaze.datamodel import CompletionResult
import openai
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class CodeGenerator(object):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Generate code"""
        pass


class OpenAICodeGenerator(CodeGenerator):
    def __init__(self, name: str, model: str = "codex-davinci-001"):
        super().__init__(name)
        self.engine = model

    def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        best_of: int = 1,
        frequency_penalty: int = 0,
        n: int = 10,
        suffix: str = None,
        presence_penalty: int = 0,
        temperature: float = 0.2,
    ) -> list[Any]:
        engine = self.engine
        prompt = prompt
        if suffix is not None:
            engine = "code-davinci-002"
        response: list[Any] = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            # top_p=1,
            # logprobs=1,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            suffix=suffix,
            n=n,
        )
        completions = [
            CompletionResult(text=x.text, logprobs=x.logprobs) for x in response.choices
        ]
        return completions


class HFCodeGenerator(CodeGenerator):
    # TODO get log probs https://huggingface.co/blog/how-to-generate
    """Generate code with Huggingface Models"""

    def __init__(self, name: str, model: str = "Salesforce/codegen-350M-multi"):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(model)
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        best_of: int = 1,
        frequency_penalty: int = 0,
        n: int = 10,
        suffix: str = None,
        presence_penalty: int = 0,
        temperature: float = 0.2,
    ):

        prompt_tokens = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        generations = self.model.generate(
            prompt_tokens.input_ids,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            num_return_sequences=n,
            attention_mask=prompt_tokens.attention_mask,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_tokens = [
            self.tokenizer.decode(
                generation, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[len(prompt) :]
            for generation in generations
        ]

        completions = [CompletionResult(text=x, logprobs=[]) for x in generated_tokens]
        return completions
