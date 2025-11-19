from blueprints.ai.blueprint_ai_adapter import suggest_blueprint_variables


def test_adapter_returns_defaults():
    result = suggest_blueprint_variables("proxmox-homelab", [{"memory_gb": 32}])
    assert result["proxmox_node_count"] == "1"


def test_adapter_uses_mock_provider(monkeypatch):
    def fake_provider(name: str):
        class _Provider:
            def generate_blueprint_suggestions(self, context):
                return f"AI for {context['topology']}"

        return _Provider()

    monkeypatch.setattr("blueprints.ai.blueprint_ai_adapter.get_provider", fake_provider)
    result = suggest_blueprint_variables("micro-saas", [], provider="mock")
    assert "AI for micro-saas" in result["ai_summary"]
