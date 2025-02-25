from typing import Any, Dict, Iterator, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

import requests, json

class OpenGPTXLLM(LLM):
    """A custom chat model that echoes the first `n` characters of the input.

    When contributing an implementation to LangChain, carefully document
    the model including the initialization parameters, include
    an example of how to initialize the model and include any relevant
    links to the underlying models documentation or API.

    Example:

        .. code-block:: python

            model = CustomChatModel(n=2)
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """
    def __init_subclass__(cls) -> None:

        return super().__init_subclass__()
    #n: int
    #"""The number of characters from the last message of the prompt to be echoed."""

    def _call_with_score(self, prompt: str)->str:

        prompt = prompt.replace( ",", " " )
        prompt = prompt.replace( "\n", " " )
        #prompt = prompt.replace( '*', ' ' )
        prompt = prompt.replace( "'", " " )
        #print(prompt)
        url = 'https://demo.iais.fraunhofer.de/llm-playground/generate?model_name=OpenGPT-X-24EU-2.5T-Instruct-17'
        y = """{"prompt":{"placeholder_values":{},"history":[],"prompt_template":{"instruction":"","placeholder_variables":[],"few_shot_separator":"\\n***\\n","few_shot_enumerator":"Dialog {i}:\\n","user_delimiter":"User","system_delimiter":"System","context_delimiter":"Context","few_shot_as_system":false,"few_shots":[],"template":[{"role":"user","text":" """+prompt+""" "},{"role":"system","text":""}]}},"decoding":{"max_new_tokens":1024,"temperature":0.001,"stop_sequences":["#"]}}"""
        #print(y)
        payload =json.loads(y, strict=False)
        headers = {"accept": "*/*","content-type": "application/json"}

        response =  requests.post(url, json=payload, headers=headers)
        response_prompt = response.content
        return response_prompt

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """


        response_prompt = self._call_with_score(prompt=prompt)
        result = response_prompt
        try:
            result = json.loads(response_prompt)['texts'][0]
            result = result.replace('</s>','')
            return result
        except:
            raise AttributeError("response value has not  'texts' section. Here is its content: " , str(response_prompt) , "and the prompt was:", str(prompt))
            
        return result

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt.

        This method should be overridden by subclasses that support streaming.

        If not implemented, the default behavior of calls to stream will be to
        fallback to the non-streaming version of the model and return
        the output as a single chunk.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of these substrings.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            An iterator of GenerationChunks.
        """
        for char in prompt[: self.n]:
            chunk = GenerationChunk(text=char)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

            yield chunk

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "CustomChatModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom"
    
