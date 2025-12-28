from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class PromptBuilder:
    """
    PromptBuilder: configurable builder for creating role-based prompts for AI assistants.
    Easily extendable with new roles/templates.
    """
    topic: Optional[str] = None
    user_name: Optional[str] = None      # e.g. "English" or "Bangla"
    tone: str = "friendly"          # e.g. "friendly", "formal", "encouraging"
    avoid_direct_answer: bool = True
    extras: Dict[str, str] = field(default_factory=dict)

    # Role templates (lowercase keys). Add or override templates with add_role_template().
    role_templates: Dict[str, str] = field(default_factory=lambda: {
        "tutor": (
            "You are a tutor named Cyrus. You are an AI assistant whose job is to help students learn. "
            "{avoid_direct}\n"
            "Tone: {tone}.\n"
            "Topic: {topic}."
        ),
        "coding_assistant": (
            "You are a coding assistant. Explain programming concepts, give hints, and guide the user. "
            "Avoid giving full solutions when avoid_direct is True.\n"
            "Topic/context: {topic}."
        ),
        "career_helper": (
            "You are a career advisor. Provide professional guidance, CV/interview tips, and skill-gap analysis.\n"
            "User query: {topic}."
        ),
        "interviewer": (
            "You are a mock interviewer. Ask relevant interview questions and provide feedback to improve answers.\n"
            "Position/topic: {topic}."
        ),
        "language_teacher": (
            "You are a language teacher. Provide step-by-step practice, point out mistakes, and offer corrections. "
            "Avoid giving all answers directly if avoid_direct is True.\n"
            "Topic: {topic}."
        ),
        "math_tutor": (
            "You are a math tutor. Guide the student step-by-step with questions and hints so they can derive the solution themselves.\n"
            "Problem: {topic}."
        ),
    })

    def _avoid_direct_text(self) -> str:
        """Return the avoid-direct-answer instruction text."""
        if self.avoid_direct_answer:
            return ("Do not provide the direct solution. Encourage the student to think and solve by giving "
                    "questions and hints.")
        return "Direct answers are allowed."

    def build(self, role: str, custom_instructions: Optional[str] = None) -> str:
        """
        Build and return the final prompt for the given role.
        Raises ValueError if the role is unknown.
        """
        role_key = role.lower()
        if role_key not in self.role_templates:
            raise ValueError(f"Unknown role: {role}. Available roles: {list(self.role_templates.keys())}")

        template = self.role_templates[role_key]
        final_prompt = template.format(
            avoid_direct=self._avoid_direct_text(),
            tone=self.tone,
            topic=self.topic or "<no topic provided>"
        )

        if self.extras:
            extras_text = "\n\nAdditional context:"
            for k, v in self.extras.items():
                extras_text += f"\n- {k}: {v}"
            final_prompt += extras_text

        if custom_instructions:
            final_prompt += "\n\nCustom instructions:\n" + custom_instructions

        if self.user_name:
            header = f"Student: {self.user_name}\n"
            final_prompt = header + final_prompt

        return final_prompt

    def add_role_template(self, role_name: str, template_text: str, overwrite: bool = False) -> None:
        """
        Add a new role template. If overwrite=False and role exists, raises KeyError.
        """
        key = role_name.lower()
        if not overwrite and key in self.role_templates:
            raise KeyError(f"Role '{role_name}' already exists. Use overwrite=True to replace.")
        self.role_templates[key] = template_text

    def set_extra(self, key: str, value: str) -> None:
        """Add or update an extra context field."""
        self.extras[key] = value

    def clear_extras(self) -> None:
        """Clear all extras."""
        self.extras.clear()




# Example 1: Tutor prompt
pb = PromptBuilder(
    topic="How to calculate the area of a circle.")
print(pb.build("tutor"))


