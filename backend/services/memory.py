from typing import Dict, List, Optional

try:
    from langchain.memory import ConversationBufferMemory
except ModuleNotFoundError:
    ConversationBufferMemory = None

from utils.logger import get_logger

logger = get_logger("backend.memory")

DEFAULT_SESSION_ID = "global"


class _SimpleMessage:
    def __init__(self, message_type: str, content: str) -> None:
        self.type = message_type
        self.content = content


class _SimpleChatMemory:
    def __init__(self) -> None:
        self.messages: List[_SimpleMessage] = []


class _SimpleConversationMemory:
    def __init__(self) -> None:
        self.chat_memory = _SimpleChatMemory()

    def load_memory_variables(self, _: Dict) -> Dict[str, str]:
        lines = []
        for message in self.chat_memory.messages:
            speaker = "User" if message.type == "human" else "Assistant"
            lines.append(f"{speaker}: {message.content}")
        return {"history": "\n".join(lines)}

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        self.chat_memory.messages.append(_SimpleMessage("human", inputs.get("input", "")))
        self.chat_memory.messages.append(_SimpleMessage("ai", outputs.get("output", "")))

    def clear(self) -> None:
        self.chat_memory.messages.clear()


class ShoppingMemoryService:
    def __init__(self) -> None:
        self.memories: Dict[str, object] = {}

    def _get_memory(self, session_id: Optional[str] = None):
        key = session_id or DEFAULT_SESSION_ID
        if key not in self.memories:
            if ConversationBufferMemory is None:
                logger.warning("LangChain is not installed. Using local fallback chat memory.")
                self.memories[key] = _SimpleConversationMemory()
            else:
                self.memories[key] = ConversationBufferMemory(
                    memory_key="history",
                    input_key="input",
                    output_key="output",
                    return_messages=False,
                )
        return self.memories[key]

    def get_history(self, session_id: Optional[str] = None) -> str:
        memory = self._get_memory(session_id)
        if memory is None:
            return ""

        variables = memory.load_memory_variables({})
        history = variables.get("history", "")
        return history.strip() if isinstance(history, str) else str(history)

    def get_previous_queries(self, session_id: Optional[str] = None) -> List[str]:
        memory = self._get_memory(session_id)
        if memory is None:
            return []

        messages = getattr(memory.chat_memory, "messages", [])
        queries: List[str] = []
        for message in messages:
            if getattr(message, "type", None) == "human":
                content = getattr(message, "content", "").strip()
                if content:
                    queries.append(content)
        return queries

    def build_contextual_query(self, query: str, session_id: Optional[str] = None) -> str:
        history = self.get_history(session_id)
        if not history:
            return query

        return (
            "Use the previous shopping conversation to resolve follow-up wording, "
            "filters, pronouns, and category references.\n\n"
            f"Conversation history:\n{history}\n\n"
            f"Current user query:\n{query}\n\n"
            "Expanded shopping query for retrieval and recommendation:"
        )

    def save_turn(self, query: str, answer: str, session_id: Optional[str] = None) -> None:
        memory = self._get_memory(session_id)
        if memory is None:
            return

        memory.save_context({"input": query}, {"output": answer})

    def clear(self, session_id: Optional[str] = None) -> None:
        key = session_id or DEFAULT_SESSION_ID
        memory = self.memories.get(key)
        if memory is not None:
            memory.clear()
        self.memories.pop(key, None)


memory_service = ShoppingMemoryService()
