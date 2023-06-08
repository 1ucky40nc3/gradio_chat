from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Optional
)

from dataclasses import dataclass

Update = dict
ChatHistory = List[Tuple[str, str]]


@dataclass
class Setting:
    id: str
    file: str
    data: Dict[str, Any]


@dataclass
class Frontend:
    setting_id: str
    chat_id: Optional[str]


@dataclass
class Chat:
    id: str
    history: ChatHistory
