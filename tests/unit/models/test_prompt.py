"""Tests for Prompt models."""

from vectraxis.models.prompt import Prompt, PromptCreate, PromptUpdate


class TestPromptModel:
    def test_defaults(self):
        p = Prompt(name="test", user_prompt_template="{{input}}")
        assert p.id  # auto-generated
        assert p.description == ""
        assert p.system_prompt == ""
        assert p.model == ""
        assert p.agent_type == "analysis"
        assert p.output_json_schema is None
        assert p.temperature == 0.7
        assert p.max_tokens == 1024
        assert p.variables == []
        assert p.tags == []
        assert p.version == 1

    def test_custom_values(self):
        p = Prompt(
            name="custom",
            user_prompt_template="Do {{task}}",
            system_prompt="You are helpful.",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2048,
            variables=["task"],
            tags=["production"],
        )
        assert p.model == "gpt-4o"
        assert p.temperature == 0.3
        assert p.variables == ["task"]

    def test_output_json_schema(self):
        schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        p = Prompt(
            name="structured",
            user_prompt_template="test",
            output_json_schema=schema,
        )
        assert p.output_json_schema == schema

    def test_from_attributes(self):
        assert Prompt.model_config.get("from_attributes") is True


class TestPromptCreate:
    def test_minimal(self):
        pc = PromptCreate(name="test", user_prompt_template="{{input}}")
        assert pc.name == "test"
        assert pc.temperature == 0.7

    def test_with_tags(self):
        pc = PromptCreate(
            name="test",
            user_prompt_template="{{input}}",
            tags=["a", "b"],
        )
        assert pc.tags == ["a", "b"]


class TestPromptUpdate:
    def test_all_none_by_default(self):
        pu = PromptUpdate()
        assert pu.name is None
        assert pu.temperature is None

    def test_partial_update(self):
        pu = PromptUpdate(name="new-name", temperature=0.5)
        data = pu.model_dump(exclude_none=True)
        assert data == {"name": "new-name", "temperature": 0.5}
