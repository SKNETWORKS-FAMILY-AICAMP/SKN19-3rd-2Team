# app/state.py

from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Literal, Optional
from langgraph.graph import MessagesState
from langchain_core.pydantic_v1 import BaseModel, Field


class PatentResult(TypedDict, total=False):
    app_num: str                  # 출원번호
    title: str                    # 발명의 명칭
    abstract: str                 # 초록 (요약본이면 더 좋음)
    ipc_codes: List[str]          # 주요 IPC 코드들
    score: float                  # 유사도 점수 (0~1)
    # 필요하면 여기에 더 필드 추가 가능 (예: applicant, year 등)


class PatentSearchRecord(TypedDict, total=False):
    id: str                       # "ps_1", "ps_2" 같은 식별자
    query: str                    # 검색에 사용한 정제된 질의 (키워드/문장)
    top_k: int                    # 요청한 결과 개수
    results: List[PatentResult]   # 검색 결과 리스트


class IPCCodeInput(BaseModel):
    codes: List[str] = Field(
        description="조회할 IPC 코드들의 리스트 (예: ['G06Q11/50', 'H04N01/20', 'A01B'])",
        min_items=1
    )

# IPC 검색관련 입출력 폼
class IPCDetailInfo(BaseModel):
    ids: str = Field(description="국제특허분류(IPC) 코드")
    description: str = Field(description="해당 IPC 코드의 상세 기술 설명 및 정의")
    type: str = Field(description="해당 IPC 코드의 계층 (예: s, c, u등) s는 section, c는 main class, u는 sub class, m은 main group, 이후 숫자들은 sub group")
    ancestors : str = Field(description="해당 코드의 상위 조상 코드들 (예:A > A01 > A01B > A01B1/00)")

class IPCSimpleInfo(BaseModel):
    ids: str = Field(description="국제특허분류(IPC) 코드")
    description: str = Field(description="해당 IPC 코드의 상세 기술 설명 및 정의")

class IPCKeywordInput(BaseModel):
    tech_texts: List[str] = Field(
        description="검색을 원하는 아이디어에 대해 핵심 독립적 기술단위로 분해한 영어 키워드들의 리스트 (예: ['Organic Light Emitting Display','Display Panel Opening Area','Pixel Electrode Contact Structure'])",
        min_items=1
    )
    top_k: int = Field(description="최종적으로 몇개의 main코드의 설명을 가져올지")

class IPCMainDescription(BaseModel):
    mains: List[IPCSimpleInfo] = Field(description = '입력된 키워드들에 대해 가장 가까운 의미를 나타내는 것으로 Vector DB에서 검색된 것들과 설명')
    subs: List[IPCSimpleInfo] = Field(description = "검색되어 나온 코드들 중 mains의 키워드들과 연관이 있는 키워드들에 대한 설명 ")


class MetaState(TypedDict, total=False):
    turn_index: int               # 몇 번째 턴인지
    last_used_tools: List[str]    # 이번 턴에 어떤 툴 썼는지 (["search_patent", ...])
    session_id: Optional[str]     # 나중에 세션 추적용

class OtherNoteRecord(TypedDict, total=False):
    id: str
    summary: str      # 사용자의 기타 질문 요약
    detail: str       # 조금 더 긴 설명이나 메모


class State(MessagesState):
    """
    LangGraph에서 사용할 전역 상태 정의.
    MessagesState를 상속하면 자동으로 `messages` 필드가 들어있음.
    """
    short_summary: Optional[str]
    patent_history: List[PatentSearchRecord]
    ipc_history: List[IPCRequestRecord]
    other_notes: List[OtherNoteRecord]
    meta: MetaState

# messages:
# LangGraph 기본 → user/assistant 전체 대화 저장

# short_summary:
# 오랫동안 대화하면 MemoryNode가 요약해서 여기 넣음

# patent_history:
# 여러 번의 특허 검색 기록
# 마지막은 patent_history[-1]로 접근

# ipc_history:
# 여러 번의 IPC 요청/설명 기록

# other_notes:
# “이번 턴에서 답해야 하는 기타 사항 요약” 정도로 사용 가능

# meta:
# 턴 인덱스, 최근 사용 툴, 세션 ID 등 운영/디버깅