from __future__ import annotations
from displaylib.template.type_hints import NodeType
from displaylib.ascii import networking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class PairUid: # Component (mixin class)
    root: App
    peer_uid: str = None # type: ignore

    # def __new__(cls: type[NodeType], *args, **kwargs) -> NodeType:
    #     instance = super().__new__(cls, *args, **kwargs)
    #     req = networking.Request("PAIR_UID", [instance.uid])
    #     instance.root.send(req) # type: ignore
    #     return instance # type: ignore
