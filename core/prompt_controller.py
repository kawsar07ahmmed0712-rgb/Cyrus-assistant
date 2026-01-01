# core/prompt_controller.py
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

@dataclass
class PromptBuilder:
    """
    Beast-level PromptBuilder.
    - dynamic placeholders
    - context injection
    - instruction presets and safety wrappers
    - summarization helpers
    """
    topic: Optional[str] = None
    user_name: Optional[str] = None
    tone: str = "friendly"
    avoid_direct_answer: bool = False
    extras: Dict[str, str] = field(default_factory=dict)
    context_messages: List[Dict[str, Any]] = field(default_factory=list)
    safety_instructions: Optional[str] = None
    output_format: Optional[str] = None 
    max_context_messages: int = 50

    role_templates: Dict[str, str] = field(default_factory=lambda: {
        "tutor": (
            "You are Cyrus, an expert tutor who helps students learn by guiding them step-by-step.\n"
            "{avoid_direct}\n"
            "Tone: {tone}\n"
            "Topic: {topic}\n"
            "{context}\n"
            "{extras}\n"
        ),
        "coding_assistant": (
            "You are a highly experienced coding assistant. Give clear explanations, examples and code snippets when helpful.\n"
            "{avoid_direct}\n"
            "Tone: {tone}\n"
            "Topic: {topic}\n"
            "{context}\n"
            "{extras}\n"
        ),
        "career_helper": (
            "You are a career advisor. Offer practical, concise career guidance, CV tips, and interview preparation.\n"
            "Topic: {topic}\n"
            "{context}\n"
            "{extras}\n"
        ),
        "interviewer": (
            "You are a mock interviewer. Ask interview-style questions, give feedback and scoring guidance.\n"
            "Position/topic: {topic}\n"
            "{context}\n"
        ),
        "language_teacher": (
            "You are a language teacher. Provide corrections, exercises and progressive skill-building steps.\n"
            "{avoid_direct}\n"
            "Topic: {topic}\n"
            "{context}\n"
        ),
        "math_tutor": (
            "You are a math tutor. Ask guiding questions, show intermediate steps if requested, and verify answers.\n"
            "{avoid_direct}\n"
            "Problem: {topic}\n"
            "{context}\n"
        ),
        "summarizer": (
            "You are an expert summarizer. Read the conversation and produce a short concise summary.\n"
            "{context}\n"
        ),
        "writer": (
            "You are a professional writer. Produce clear, polished, and audience-appropriate text.\n"
            "Topic: {topic}\n"
            "{context}\n"
        ),
    })

    def _avoid_direct_text(self) -> str:
        if self.avoid_direct_answer:
            return ("Instruction: Do not provide direct final solutions unless the user asks for them. "
                    "Favor hints, guiding questions and scaffolded steps.")
        return "Instruction: Direct answers are allowed when appropriate."

    def _build_context_text(self) -> str:
        if not self.context_messages:
            return ""
        msgs = self.context_messages[-self.max_context_messages:]
        lines = ["Conversation history (newest last):"]
        for m in msgs:
            role = str(m.get("role", "user")).capitalize()
            content = str(m.get("content", "")).strip()
            if len(content) > 1200:
                content = content[:1180] + "…"
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _build_extras_text(self) -> str:
        if not self.extras:
            return ""
        lines = ["Extra context:"]
        for k, v in self.extras.items():
            lines.append(f"- {k}: {v}")
        return "\n".join(lines)

    def build(self, role: str, custom_instructions: Optional[str] = None) -> str:
        role_key = role.lower()
        if role_key not in self.role_templates:
            raise ValueError(f"Unknown role '{role}'. Allowed: {list(self.role_templates.keys())}")

        template = self.role_templates[role_key]

        prompt = template.format(
            avoid_direct=self._avoid_direct_text(),
            tone=self.tone,
            topic=self.topic or "<no topic provided>",
            context=self._build_context_text(),
            extras=self._build_extras_text()
        )
        if self.user_name:
            prompt = f"User: {self.user_name}\n" + prompt

        if self.output_format:
            prompt += f"\nDesired format: {self.output_format}\n"

        if self.safety_instructions:
            prompt += f"\nSafety rules: {self.safety_instructions}\n"

        if custom_instructions:
            prompt += f"\nCustom instructions: {custom_instructions}\n"

        prompt += (
            "\nDeliverable:\n"
            "1) A concise direct answer (2-6 sentences) labeled 'Answer:'\n"
            "2) An 'Expanded' section with examples, code, or step-by-step guidance if relevant.\n"
            "If avoid_direct is ON, place the concise answer as a brief hint and put detailed steps in Expanded after user asks for full solution.\n"
        )

        return prompt

    def add_role_template(self, role_name: str, template_text: str, overwrite: bool = False):
        key = role_name.lower()
        if key in self.role_templates and not overwrite:
            raise KeyError(f"Role '{role_name}' exists. Use overwrite=True to replace.")
        self.role_templates[key] = template_text

    def set_extra(self, key: str, value: str):
        self.extras[key] = value

    def clear_extras(self):
        self.extras.clear()

    def add_context_messages(self, messages: List[Dict[str, Any]]):
        if not messages:
            return
        existing = self.context_messages or []
        combined = existing + messages
        self.context_messages = combined[-self.max_context_messages:]

    def clear_context(self):
        self.context_messages.clear()

    def build_for_definition(self, role: str = "coding_assistant", custom: Optional[str] = None) -> str:
        self.avoid_direct_answer = False
        self.output_format = "short_first_then_expanded"
        return self.build(role, custom)

    def build_for_tutor(self, role: str = "tutor", custom: Optional[str] = None) -> str:
        self.avoid_direct_answer = True
        self.output_format = "hint_then_steps_on_request"
        return self.build(role, custom)

    @staticmethod
    def summarization_prompt(messages: List[Dict[str, Any]], length: str = "short") -> str:
        snippet = []
        for m in messages[-30:]:
            role = str(m.get("role", "user")).upper()
            content = str(m.get("content", "")).strip()
            snippet.append(f"{role}: {content}")
        joined = "\n".join(snippet)
        return (
            f"Summarize the following conversation into a short {length} summary (2-4 sentences) and list 3 action-items.\n\n"
            f"{joined}\n\n"
            "Output format:\nSummary:\n- <one or two lines>\nAction items:\n1)\n2)\n3)\n"
        )
