# PromptTuner Development Notes

## StructuredOutputAgent Implementation

### Key Learnings

#### OpenAI Agents SDK with Third-Party APIs
- **Problem**: OpenAI Agents SDK doesn't directly accept custom `client` parameter in `Agent()` constructor
- **Solution**: Configure third-party APIs (like DeepSeek) using environment variables:
  ```python
  os.environ["OPENAI_API_KEY"] = api_key
  os.environ["OPENAI_BASE_URL"] = base_url  # For third-party providers
  ```

#### DeepSeek API Integration
- **Base URL**: `https://api.deepseek.com` (OpenAI-compatible)
- **Model**: Use `deepseek-chat` for DeepSeek API
- **Compatibility**: Fully compatible with OpenAI SDK - just change base URL and API key
- **Environment Variables**: 
  - `DEEPSEEK_API_KEY`
  - `DEEPSEEK_BASE_URL`

#### Agent Configuration Pattern
```python
# Correct way to configure third-party API with Agents SDK
class StructuredOutputAgent:
    def __init__(self, api_key=None, base_url=None, model=None):
        # Set environment variables for agents SDK
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        if base_url:
            os.environ["OPENAI_BASE_URL"] = base_url
            
        # Auto-select model based on provider
        if not model:
            if base_url and "deepseek" in base_url.lower():
                model = "deepseek-chat"
            else:
                model = "gpt-4o-mini"
        
        self.agent = Agent(
            name="StructuredExtractor",
            instructions="...",
            model=model  # Specify model explicitly
        )
```

#### Pydantic Integration
- Use `model_json_schema()` to get schema for LLM prompts
- Use `model_validate()` to validate extracted JSON
- JSON extraction from LLM responses requires robust parsing (handle surrounding text)

#### Testing Strategy
- Always check for valid (non-demo) API keys before live testing
- Implement fallback testing that validates structure without API calls
- Test JSON extraction and Pydantic validation separately

### Best Practices
1. **Environment Variable Priority**: DeepSeek → OpenAI for better cost efficiency
2. **Model Selection**: Auto-detect provider and set appropriate model
3. **Error Handling**: Validate inputs and provide clear error messages
4. **Testing**: Structure validation without requiring live API calls
5. **Documentation**: Include usage examples and configuration requirements

#### Tracing Configuration
- **Global Disable**: Use `set_tracing_disabled(True)` from `agents` module
- **Environment Variable**: Set `OPENAI_AGENTS_DISABLE_TRACING=1` 
- **Per-Run Disable**: Use `RunConfig(tracing_disabled=True)` for individual runs
- **Sensitive Data**: Use `RunConfig(trace_include_sensitive_data=False)` to exclude sensitive data
- **Official Docs**: https://openai.github.io/openai-agents-python/tracing/

### External Documentation Insights

#### OpenAI Agents SDK (2025)
- **Official Docs**: https://openai.github.io/openai-agents-python/
- **Key Components**: Agent, Runner, InputGuardrail, GuardrailFunctionOutput
- **Multi-Provider Support**: Compatible with 100+ LLMs through OpenAI-compatible endpoints
- **Production Features**: Built-in tracing, async execution, automatic conversation history
- **Tracing Docs**: https://openai.github.io/openai-agents-python/tracing/

#### Third-Party Model Integration Methods (2025)

##### 1. OpenAI-Compatible API Configuration
- **Global Client Setup**: Use `set_default_openai_client()` for system-wide configuration
- **Custom Client Example**:
  ```python
  from openai import AsyncOpenAI
  from agents import set_default_openai_client
  
  custom_client = AsyncOpenAI(
      base_url="https://api.deepseek.com",
      api_key="your-api-key"
  )
  set_default_openai_client(custom_client)
  ```

##### 2. Per-Agent Model Configuration
- **Direct Model Specification**: Configure models individually per agent
- **Mixed Model Workflows**: Use different models for different agents within same workflow
- **DeepSeek Example**:
  ```python
  deepseek_client = AsyncOpenAI(
      base_url="https://api.deepseek.com",
      api_key=deepseek_api_key
  )
  
  agent = Agent(
      name="DeepSeek Agent",
      instructions="Your instructions here",
      model=OpenAIChatCompletionsModel(
          model="deepseek-chat",
          openai_client=deepseek_client,
      ),
  )
  ```

#### Third-Party API Integration Patterns
- **DeepSeek Compatibility**: Full OpenAI API compatibility via base URL change
- **Configuration Method**: Multiple approaches (environment variables, client injection)
- **Model Mapping**: Provider-specific model names (`deepseek-chat`, `gpt-4o-mini`)
- **Industry Trend**: Most providers now offer OpenAI-compatible endpoints

#### Critical API Compatibility Issue (New Learning)
- **Problem**: OpenAI Agents SDK defaults to Responses API, but third-party providers like DeepSeek only support Chat Completions API
- **Symptom**: 404 errors when using third-party providers with default SDK configuration
- **Solution**: Must explicitly switch to Chat Completions API for third-party providers:
  ```python
  from agents import set_default_openai_api
  
  # Required for third-party providers
  if base_url:  # Third-party provider detected
      set_default_openai_api("chat_completions")
  ```
- **Impact**: Without this fix, all third-party integrations will fail with 404 errors

#### Advanced Configuration Options
- **API Selection**: Switch between Responses API and Chat Completions API
- **Tracing Configuration**: 
  - Disable: `set_tracing_disabled(True)`
  - Custom API key: `set_tracing_export_api_key()`
- **Logging Controls**: Environment variables to disable sensitive data logging
- **Model-Specific Settings**: Configure temperature, extra_args via ModelSettings

#### Provider-Specific Notes
- **DeepSeek Models**: `deepseek-chat`, `deepseek-reasoner`
- **Base URLs**: `https://api.deepseek.com` or `https://api.deepseek.com/v1`
- **Feature Limitations**: Not all providers support structured outputs, multimodal inputs
- **Best Practice**: Use single model shape per workflow for consistent feature support

#### Structured Output Best Practices
- **Schema Generation**: Leverage Pydantic's `model_json_schema()` for LLM prompts
- **Response Parsing**: Robust JSON extraction handling LLM explanation text
- **Validation Pipeline**: Parse → Validate → Instantiate Pydantic model
- **Error Recovery**: Graceful handling of malformed JSON and validation failures

### Project Structure
- Main implementation: `src/promptuner/structured_output_parse.py`
- Dependencies: `pydantic`, `openai-agents`, `python-dotenv`
- Testing: Built-in `if __name__ == "__main__"` block with fallback testing
- Configuration: Environment variables in `.env` (DeepSeek/OpenAI support)
- Tracing: Globally disabled via `set_tracing_disabled(True)`