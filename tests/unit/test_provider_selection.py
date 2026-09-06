import specialists.base as base


def test_build_llm_model_prefers_configured_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GROQ_API_KEY", "gk_test")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini_test")

    monkeypatch.setattr(base.settings, "llm_provider", "gemini", raising=False)
    monkeypatch.setattr(base.settings, "groq_api_key", "gk_test", raising=False)
    monkeypatch.setattr(base.settings, "gemini_api_key", "gemini_test", raising=False)

    captured = {}

    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyModel:
        def __init__(self, model, openai_client):
            captured["model"] = model
            captured["client"] = openai_client

    monkeypatch.setattr(base, "AsyncOpenAI", lambda **kwargs: DummyClient(**kwargs))
    monkeypatch.setattr(base, "OpenAIChatCompletionsModel", DummyModel)

    model = base._build_llm_model()

    assert isinstance(model, DummyModel)
    assert captured["model"] == "gemini-2.0-flash"
