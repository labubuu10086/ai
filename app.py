import logging
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from textwrap import dedent
from typing import Iterator

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from openai import OpenAI
import requests

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
ARCHIVE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
ARCHIVE_LOCAL_DB_PATH = Path(__file__).resolve().parent / "storage" / "archives.sqlite3"

ANTI_AI_GUARD_DEFAULT = dedent(
    """
    1. 少用空泛判断句，不要用“这说明了”“某种意义上”“命运的齿轮”这类总结句替代情节。
    2. 少用“与此同时、然而、此时、不由得、仿佛、似乎、显得”等高频连接词和口头禅。
    3. 先写动作、视线、停顿、环境，再写情绪；少直接贴“愤怒、震惊、感动”等标签。
    4. 对话要有潜台词、打断、试探和误解，不要每句都完整、标准、讲道理。
    5. 每章至少有一个明确推进：信息改变、关系改变、局势改变，避免原地兜圈。
    6. 世界观信息嵌进事件里，不要整段说明书式介绍。
    7. 比喻宁少勿滥，优先具体物件和场景，不堆砌华丽辞藻。
    8. 结尾不要总用硬钩子和万能反转，要让读者因为人物处境和未完成动作想继续读。
    9. 前 3 章必须立住主问题、主角代价和读者会追问的核心悬念，不能一直铺垫不进入事件。
    10. 每 3 到 5 章至少完成一个小闭环，同时把更大的谜团往前推一步，不能重复同一种爽点或误会。
    11. 爽点来自人物选择、线索兑现和局势反噬，不靠机械打脸、机械升级、机械虐渣。
    12. 反转必须提前埋可回看的线索，避免只靠硬掰、强行藏信息或临时加设定。
    13. 不要把角色写成只有一个标签的人；每个关键角色都该有体面外壳、不体面欲望和自欺之处。
    14. 不要让所有人都说同一种“聪明话”；区分不同人物的词汇、停顿、回避方式和攻击方式。
    15. 冲突升级优先来自既有矛盾连锁反应，不靠突然出现一个更大的敌人、一个更高的设定或万能贵人。
    16. 伏笔不只埋道具和谜题，也要埋人物偏见、关系裂缝、错误判断和情绪余波。
    17. 反转应当是“重读前文会发现早就埋着”，而不是临时换题、偷换设定或故意瞒关键事实。
    18. 中段不能靠换地图、刷副本、重复误会和重复打脸制造假推进；每轮推进都要改变关系、信息或代价。
    """
).strip()

FANQIE_MARKET_BRIEF = dedent(
    """
    大众连载平台适配参考（基于 2025 年公开信息整理）：
    1. 读者覆盖广，以中青年大众阅读人群为主；平台向连载通常要求入口直给、阅读门槛低、情绪回报明确。
    2. 当前高活跃或重点赛道集中在悬疑脑洞、科幻末世、游戏体育、都市脑洞、玄幻脑洞、历史脑洞、女频悬疑、现言悬疑、女频玄幻言情、古言脑洞、现言脑洞、双强虐渣、现实情感、志怪幻想、年代等。
    3. 平台重视累计阅读、追更留存、评论和读完率，所以开篇三章的钩子、连续悬念、角色欲望和章节推动点必须足够清楚。
    4. 适配平台不等于写成模板；要严格避免恶意水文、重复爽点和流水线推进，故事必须有人物因果、阶段性回收和最终兑现。
    """
).strip()

FANQIE_SERIAL_PRINCIPLES = dedent(
    """
    平台向连载但拒绝流水线的执行原则：
    1. 开篇要尽快抛出异常事件、未解问题或危险承诺，让读者知道“为什么要继续看”。
    2. 每章都要有动作推进，不允许靠整段说明、复述、设定科普来撑字数。
    3. 每 3 到 5 章形成一个小高潮或小闭环，同时继续抬升更大的主悬念。
    4. 悬念必须可兑现：每个重要谜团至少提前埋一个可回看的线索，不做纯硬反转。
    5. 保持大众可读性，但不能牺牲人物复杂度、关系变化和故事完整度。
    """
).strip()

CHARACTER_COMPLEXITY_RULES = dedent(
    """
    人物塑造优化原则：
    1. 每个关键角色都要同时具备：体面外壳、不体面欲望、现实顾虑、自我欺骗。
    2. 主角不是道德满分的标准答案；对手也不是只会作恶的功能反派；配角不能只是递线索和递情绪的工具人。
    3. 人物行为要由利益、羞耻、恐惧、执念、习惯共同驱动，不要只用“爱/恨/正义感”单线解释。
    4. 角色之间的张力优先来自立场错位、秘密不对称、旧账未清和情感负债，而不是嘴上吵得凶。
    5. 每个关键角色至少有一个容易写崩的点，并明确如何避免脸谱化。
    6. 对话、沉默、撒谎、发火和示弱时的表现必须区分开，避免全员同声线。
    """
).strip()

ANTI_CLICHE_PLOT_RULES = dedent(
    """
    反俗套推进原则：
    1. 冲突升级优先来自既有矛盾的连锁反应，不靠临时加更大反派、更高设定或万能救场。
    2. 不要靠“明明能说清却偏不说”的低级误会拖剧情。
    3. 不要靠降智、巧合、无代价开挂、突然掉落证据或临时补设定解决问题。
    4. 每个重大转折至少同时改变两项：局势、关系、信息、代价中的任意两项。
    5. 中段不能换皮重复同一种桥段；每轮推进都要有新的选择困境和新的后果。
    6. 结局兑现要回到人物最初的欲望和代价，不要只靠牺牲、失忆、梦醒或天降真相糊过去。
    """
).strip()

FORESHADOW_REVERSAL_RULES = dedent(
    """
    伏笔与反转优化原则：
    1. 伏笔至少分三类来设计：事实伏笔、人物伏笔、关系伏笔；不要全是线索道具。
    2. 假线索必须服务于人物误判，而不是单纯骗读者。
    3. 反转的本质应是“已知信息被重新解释”，不是突然公布没人可能提前知道的新答案。
    4. 每个重要反转都要改变人物判断、关系位置或行动方案，而不只是制造一句“原来如此”。
    5. 伏笔埋设时要兼顾显性信息和隐性情绪余波，让回收时既有逻辑快感，也有人物后劲。
    6. 如果某个反转无法在前文埋下可回看细节，就宁可不用。
    """
).strip()


def get_setting(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name, fallback)
    if value is None:
        return None
    value = value.strip()
    return value or None


def get_float_setting(name: str, fallback: float) -> float:
    value = get_setting(name)
    if value is None:
        return fallback
    try:
        return float(value)
    except ValueError:
        return fallback


def ensure_archive_table() -> None:
    ARCHIVE_LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ARCHIVE_LOCAL_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS archives (
                archive_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def validate_archive_id(raw_archive_id: str) -> str:
    archive_id = raw_archive_id.strip()
    if not ARCHIVE_ID_PATTERN.match(archive_id):
        raise ValueError("存档编号格式不合法，请使用 8 到 64 位字母、数字、下划线或短横线。")
    return archive_id


def save_archive_snapshot(archive_id: str, payload: dict) -> None:
    ensure_archive_table()
    body = json.dumps(payload, ensure_ascii=False)

    ARCHIVE_LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ARCHIVE_LOCAL_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO archives (archive_id, payload, created_at, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(archive_id)
            DO UPDATE SET payload = excluded.payload, updated_at = CURRENT_TIMESTAMP
            """,
            (archive_id, body),
        )
        conn.commit()


def load_archive_snapshot(archive_id: str) -> dict | None:
    ensure_archive_table()

    if not ARCHIVE_LOCAL_DB_PATH.exists():
        return None
    with sqlite3.connect(ARCHIVE_LOCAL_DB_PATH) as conn:
        row = conn.execute("SELECT payload, updated_at FROM archives WHERE archive_id = ?", (archive_id,)).fetchone()
    if not row:
        return None
    payload = json.loads(row[0])
    payload["_updated_at"] = str(row[1])
    return payload


def get_model_config(prefix: str) -> dict[str, str | None]:
    base_url = get_setting(f"{prefix}_BASE_URL")
    api_key = get_setting(f"{prefix}_API_KEY")
    model = get_setting(f"{prefix}_MODEL")

    if prefix == "GEN2":
        base_url = base_url or get_setting("GEN1_BASE_URL", "https://api.openai.com/v1")
        api_key = api_key or get_setting("GEN1_API_KEY")
        model = model or get_setting("GEN1_MODEL")
    else:
        base_url = base_url or "https://api.openai.com/v1"

    return {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
    }


def get_runtime_model_config(prefix: str, data: dict | None = None) -> dict[str, str | None]:
    config = get_model_config(prefix)
    if not isinstance(data, dict):
        return config

    raw_profile = data.get("api_profile")
    if not isinstance(raw_profile, dict):
        return config

    base_url = get_text(raw_profile, "base_url")
    api_key = get_text(raw_profile, "api_key")
    model = get_text(raw_profile, "model")

    if base_url:
        config["base_url"] = base_url
    if api_key:
        config["api_key"] = api_key
    if model:
        config["model"] = model

    return config


def validate_config(config: dict[str, str | None], prefix: str) -> str | None:
    missing = []
    if not config["api_key"]:
        missing.append(f"{prefix}_API_KEY")
    if not config["model"]:
        missing.append(f"{prefix}_MODEL")

    if missing:
        return "请在页面 API 菜单里填写密钥和模型，或在环境变量中设置：" + ", ".join(missing)
    return None


def create_client(config: dict[str, str | None]) -> OpenAI:
    return OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"],
        timeout=get_float_setting("OPENAI_TIMEOUT_SECONDS", 90.0),
        max_retries=0,
    )


def get_http_timeout() -> tuple[float, float]:
    total = get_float_setting("OPENAI_TIMEOUT_SECONDS", 90.0)
    connect_timeout = min(15.0, max(5.0, total / 3))
    read_timeout = max(20.0, total)
    return (connect_timeout, read_timeout)


def build_chat_completions_url(base_url: str | None) -> str:
    normalized = (base_url or "https://api.openai.com/v1").rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def build_chat_request_payload(
    config: dict[str, str | None],
    messages: list[dict[str, str]],
    temperature: float | None,
    stream: bool,
) -> dict:
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": stream,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    return payload


def build_chat_request_headers(config: dict[str, str | None]) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }
    return headers


def format_provider_error(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        body = response.text.strip() or "<empty>"
    return f"Error code: {response.status_code}-{body}"


def extract_text_from_message_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "".join(parts)
    return ""


def extract_completion_text(response_json: dict) -> str:
    choices = response_json.get("choices") or []
    parts = []
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message") or {}
        content = extract_text_from_message_content(message.get("content"))
        if content:
            parts.append(content)
    return "".join(parts).strip()


def iter_stream_text(response: requests.Response) -> Iterator[str]:
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue

        line = raw_line.strip()
        if not line or line.startswith(":"):
            continue

        if line.startswith("data:"):
            line = line[5:].strip()

        if line == "[DONE]":
            break

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        choices = payload.get("choices") or []
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta") or {}
            content = extract_text_from_message_content(delta.get("content"))
            if content:
                yield content
                continue
            message = choice.get("message") or {}
            content = extract_text_from_message_content(message.get("content"))
            if content:
                yield content


def get_text(data: dict, key: str, fallback: str = "") -> str:
    value = data.get(key, fallback)
    if value is None:
        return fallback
    if isinstance(value, list):
        return "\n".join(str(item) for item in value).strip()
    return str(value).strip()


def clip_text(text: str, limit: int = 12000, mode: str = "tail") -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    if mode == "head":
        return text[:limit] + "\n\n[后文已截断，以控制上下文长度]"
    return "[前文已截断，仅保留最近内容以维持连续性]\n\n" + text[-limit:]


def extract_character_anchors(text: str) -> str:
    anchors = []
    current_name = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_name = line[3:].strip()
            if current_name:
                anchors.append(f"姓名：{current_name}")
            continue
        if current_name and line.startswith("- ") and any(
            key in line for key in ["定位：", "表面身份：", "核心秘密：", "对话习惯：", "与主线关系："]
        ):
            anchors.append(f"{current_name} -> {line[2:].strip()}")

    if not anchors:
        return "无明确现有人物锚点。"

    return "\n".join(f"- {item}" for item in anchors[:12])


def build_project_brief(data: dict) -> str:
    idea = get_text(data, "idea")
    genre = get_text(data, "genre", "未指定")
    fanqie_track = get_text(
        data,
        "fanqie_track",
        "未指定，可参考悬疑脑洞 / 都市脑洞 / 科幻末世 / 现言悬疑 / 女频悬疑 / 玄幻言情等",
    )
    hook_core = get_text(data, "hook_core", "未指定，请主动补齐“读者会追问什么”。")
    target_length = get_text(data, "target_length", "未指定")
    chapter_count = get_text(data, "chapter_count", "未指定")
    readership = get_text(data, "readership", "大众连载读者")
    tone = get_text(data, "tone", "未指定")
    taboo = get_text(data, "taboo", "无")

    return dedent(
        f"""
        平台目标：
        以大众连载平台为主要场景，追求强悬念、强追更、可读性强，但拒绝流水线式推进。

        核心想法：
        {idea}

        类型：
        {genre}

        连载赛道：
        {fanqie_track}

        第一钩子 / 核心悬念：
        {hook_core}

        目标总字数：
        {target_length}

        预估章节数：
        {chapter_count}

        目标读者：
        {readership}

        想要的整体气质：
        {tone}

        明确不想要的套路：
        {taboo}
        """
    ).strip()


def error_response(message: str, status: int = 400) -> Response:
    return Response(message, status=status, mimetype="text/plain; charset=utf-8")


def should_retry(exc: Exception) -> bool:
    message = str(exc).lower()
    retry_markers = [
        "429",
        "rate limit",
        "rate increased too quickly",
        "temporarily unavailable",
        "timeout",
        "connection",
        "overloaded",
    ]
    return any(marker in message for marker in retry_markers)


def should_fallback_from_stream_error(exc: Exception) -> bool:
    message = str(exc).lower()
    fallback_markers = [
        "prompt_tokens",
        "cannot read properties of undefined",
        "reading 'prompt_tokens'",
        "reading “prompt_tokens”",
        "usage",
        "stream",
    ]
    return any(marker in message for marker in fallback_markers)


def parse_sectioned_text(raw: str) -> dict[str, str]:
    pattern = re.compile(r"^###([A-Z_]+)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(raw))
    if not matches:
        return {}

    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        sections[key] = raw[start:end].strip()
    return sections


def build_sectioned_text(sections: dict[str, str], order: list[str]) -> str:
    chunks = []
    used = set()

    for key in order:
        if key in sections and sections[key].strip():
            chunks.append(f"###{key}\n{sections[key].strip()}")
            used.add(key)

    for key, value in sections.items():
        if key in used or not value.strip():
            continue
        chunks.append(f"###{key}\n{value.strip()}")

    return "\n\n".join(chunks).strip()


def normalize_dense_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", text or "")


def has_text_overlap(left: str, right: str) -> bool:
    left_dense = normalize_dense_text(left)
    right_dense = normalize_dense_text(right)
    if not left_dense or not right_dense:
        return False

    if left_dense[:6] and left_dense[:6] in right_dense:
        return True
    if right_dense[:6] and right_dense[:6] in left_dense:
        return True

    left_bigrams = {left_dense[i : i + 2] for i in range(max(len(left_dense) - 1, 0))}
    right_bigrams = {right_dense[i : i + 2] for i in range(max(len(right_dense) - 1, 0))}
    left_bigrams.discard("")
    right_bigrams.discard("")
    return bool(left_bigrams & right_bigrams)


def build_hook_core_fallback(idea: str) -> str:
    idea = clip_text(idea.strip().rstrip("。！？!?"), 80, "head")
    return f"{idea}；主角必须在下一次异常成真前查清源头，否则代价会落到自己或身边人身上。"


def normalize_autofill_output(raw: str, data: dict) -> str:
    sections = parse_sectioned_text(raw)
    if not sections:
        return raw

    idea = get_text(data, "idea")
    hook_core = sections.get("HOOK_CORE", "")
    if idea and (not hook_core or not has_text_overlap(idea, hook_core)):
        sections["HOOK_CORE"] = build_hook_core_fallback(idea)

    chapter_count_text = sections.get("CHAPTER_COUNT", "").strip()
    match = re.search(r"\d+", chapter_count_text)
    if match:
        chapter_count = int(match.group())
        chapter_count = min(90, max(45, chapter_count))
        sections["CHAPTER_COUNT"] = str(chapter_count)
    else:
        sections["CHAPTER_COUNT"] = "60"

    target_length_text = sections.get("TARGET_LENGTH", "").strip()
    target_match = re.search(r"(\d+)\s*万", target_length_text)
    if target_match:
        wan_value = int(target_match.group(1))
        if wan_value < 15 or wan_value > 30:
            sections["TARGET_LENGTH"] = "20万字"
    elif not target_length_text:
        sections["TARGET_LENGTH"] = "20万字"

    if not sections.get("GENRE", "").strip():
        sections["GENRE"] = get_text(data, "genre", "悬疑脑洞") or "悬疑脑洞"
    if not sections.get("FANQIE_TRACK", "").strip():
        sections["FANQIE_TRACK"] = get_text(data, "fanqie_track", "其他 / 混合赛道") or "其他 / 混合赛道"

    return build_sectioned_text(
        sections,
        [
            "GENRE",
            "FANQIE_TRACK",
            "READERSHIP",
            "TARGET_LENGTH",
            "CHAPTER_COUNT",
            "HOOK_CORE",
            "TONE",
            "TABOO",
            "ANSWERS_DRAFT",
        ],
    )


def open_completion(
    prefix: str,
    messages: list[dict[str, str]],
    temperature: float | None = None,
    data: dict | None = None,
):
    config = get_runtime_model_config(prefix, data)
    error = validate_config(config, prefix)
    if error:
        raise ValueError(error)

    last_error = None
    for attempt in range(3):
        try:
            response = requests.post(
                build_chat_completions_url(config["base_url"]),
                headers=build_chat_request_headers(config),
                json=build_chat_request_payload(config, messages, temperature, True),
                timeout=get_http_timeout(),
                stream=True,
            )
            if response.status_code >= 400:
                response.close()
                raise RuntimeError(format_provider_error(response))
            return response
        except requests.RequestException as exc:
            last_error = exc
            app.logger.warning("Open completion failed on attempt %s: %s", attempt + 1, exc)
            if attempt < 2 and should_retry(exc):
                time.sleep(3 * (attempt + 1))
                continue
            break
        except RuntimeError as exc:
            last_error = exc
            app.logger.warning("Open completion failed on attempt %s: %s", attempt + 1, exc)
            if attempt < 2 and should_retry(exc):
                time.sleep(3 * (attempt + 1))
                continue
            break

    raise RuntimeError(f"Error calling {prefix}: {last_error}")


def open_completion_text(
    prefix: str,
    messages: list[dict[str, str]],
    temperature: float | None = None,
    data: dict | None = None,
) -> str:
    config = get_runtime_model_config(prefix, data)
    error = validate_config(config, prefix)
    if error:
        raise ValueError(error)

    last_error = None
    for attempt in range(3):
        try:
            response = requests.post(
                build_chat_completions_url(config["base_url"]),
                headers=build_chat_request_headers(config),
                json=build_chat_request_payload(config, messages, temperature, False),
                timeout=get_http_timeout(),
            )
            if response.status_code >= 400:
                raise RuntimeError(format_provider_error(response))
            return extract_completion_text(response.json())
        except requests.RequestException as exc:
            last_error = exc
            app.logger.warning("Open completion text failed on attempt %s: %s", attempt + 1, exc)
            if attempt < 2 and should_retry(exc):
                time.sleep(3 * (attempt + 1))
                continue
            break
        except RuntimeError as exc:
            last_error = exc
            app.logger.warning("Open completion text failed on attempt %s: %s", attempt + 1, exc)
            if attempt < 2 and should_retry(exc):
                time.sleep(3 * (attempt + 1))
                continue
            break

    raise RuntimeError(f"Error calling {prefix}: {last_error}")


def make_stream_response(
    prefix: str,
    messages: list[dict[str, str]],
    temperature: float | None = None,
    data: dict | None = None,
) -> Response:
    try:
        completion = open_completion(prefix, messages, temperature, data)
    except ValueError as exc:
        app.logger.error(str(exc))
        return error_response(str(exc))
    except RuntimeError as exc:
        if should_fallback_from_stream_error(exc):
            app.logger.warning("Streaming failed for %s, falling back to non-streaming: %s", prefix, exc)
            return make_text_response(prefix, messages, temperature, data)
        app.logger.error(str(exc))
        return error_response(str(exc), status=502)

    def generate() -> Iterator[str]:
        yielded_any = False
        try:
            for delta in iter_stream_text(completion):
                if delta:
                    yielded_any = True
                    yield delta
        except Exception as exc:
            if not yielded_any and should_fallback_from_stream_error(exc):
                app.logger.warning("Stream interrupted before output for %s, retrying non-streaming: %s", prefix, exc)
                try:
                    fallback_text = open_completion_text(prefix, messages, temperature, data)
                    if fallback_text:
                        yield fallback_text
                        return
                except Exception as fallback_exc:
                    app.logger.error("Non-stream fallback failed for %s: %s", prefix, fallback_exc)
            message = f"Stream interrupted: {exc}"
            app.logger.error(message)
            yield message
        finally:
            try:
                completion.close()
            except Exception:
                pass

    return Response(generate(), mimetype="text/plain")


def make_text_response(
    prefix: str,
    messages: list[dict[str, str]],
    temperature: float | None = None,
    data: dict | None = None,
    postprocess=None,
) -> Response:
    try:
        text = open_completion_text(prefix, messages, temperature, data)
    except ValueError as exc:
        app.logger.error(str(exc))
        return error_response(str(exc))
    except RuntimeError as exc:
        app.logger.error(str(exc))
        return error_response(str(exc), status=502)

    if callable(postprocess):
        text = postprocess(text)

    return Response(text, mimetype="text/plain")


def build_questions_messages(data: dict) -> list[dict[str, str]]:
    project_brief = build_project_brief(data)

    system_prompt = dedent(
        f"""
        你是熟悉 2025 年大众连载平台读者偏好的网文策划编辑，擅长把模糊念头压缩成可写、可连载、可持续推进的故事方案。
        你的底线不是“模板化起量”，而是“既能追更，也能讲完整故事”。
        {FANQIE_MARKET_BRIEF}
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        你的任务不是直接写大纲，而是先问出最影响成稿质量的关键问题。
        问题必须具体、尖锐、有取舍价值，避免空泛。
        多追问：主角真正想要什么、真正害怕什么、最不体面的选择会是什么、第一钩子是什么、前三章怎么让人追更、悬念怎么分层兑现、哪些地方最容易写脸谱化角色、俗套推进和假反转。

        输出要求：
        1. 只输出 6 到 8 个编号问题。
        2. 每个问题后补一行“为什么要问：”。
        3. 不要直接替用户回答，不要输出大纲。
        4. 语言像编辑和作者对稿，不像客服问卷。
        5. 问题优先覆盖：赛道落位、核心悬念、主线代价、人物复杂度、前 3 章抓手、中段防水文、伏笔与反转、结局兑现。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请围绕下面这个平台向长篇项目，提出最值得先确认的关键问题。

        项目摘要：
        {project_brief}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]



def build_autofill_messages(data: dict) -> list[dict[str, str]]:
    project_brief = build_project_brief(data)
    raw_idea = get_text(data, "idea")
    existing_answers = get_text(data, "answers", "暂无")
    existing_genre = get_text(data, "genre", "未指定")
    existing_track = get_text(data, "fanqie_track", "未指定")
    existing_readership = get_text(data, "readership", "未指定")
    existing_target_length = get_text(data, "target_length", "未指定")
    existing_chapter_count = get_text(data, "chapter_count", "未指定")
    existing_hook = get_text(data, "hook_core", "未指定")
    existing_tone = get_text(data, "tone", "未指定")
    existing_taboo = get_text(data, "taboo", "未指定")

    system_prompt = dedent(
        f"""
        你是“懒人化开书助手”，目标是在作者只给了一个念头时，尽量替作者补齐能直接开写的默认配置，减少手动输入。
        你不是来提问的，而是来给出可直接落到表单里的默认值。
        {FANQIE_MARKET_BRIEF}
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        执行规则：
        1. 不要追问，不要解释推理过程，只输出能直接填写到表单里的结果。
        2. 尽量顺着作者已有方向补全，除非已有字段明显空泛。
        3. 默认值必须具体、可用，避免“待定”“可再议”“看情况”。
        4. “作者补充回答草稿”要帮作者省掉第一轮手动输入，覆盖主角欲望、代价、前三章抓手、中段防水文、结局兑现。
        5. 风格允许大众可读，但不能滑向流水线和模板化。
        6. 不要把作者已经给出的核心异常、职业、关系或场景重写成另一套完全不同的故事；优先沿用用户原始想法里的具体意象。
        7. 如果作者没有明确要求超长篇，默认目标总字数控制在 15万到30万字，默认章节数控制在 45到90 章之间，不要动不动给出几百章。
        8. 第一钩子必须直接贴着作者当前想法里的异常事件来写，不能凭空替换成另一种世界观或另一件关键道具。
        9. “作者补充回答草稿”里必须主动补出：主角的偏差/执念、一个不体面但合理的选择、最容易俗套的桥段该怎么绕开、至少一条人物或关系伏笔。
        10. 如果原始想法里已经出现了具体职业、核心物件、异常现象、地点或关系，请优先沿用这些元素，不要自作主张换题。

        请严格按下面结构输出，不要增加别的标题：
        ###GENRE
        [一句]
        ###FANQIE_TRACK
        [一句]
        ###READERSHIP
        [一句]
        ###TARGET_LENGTH
        [一句]
        ###CHAPTER_COUNT
        [只写数字]
        ###HOOK_CORE
        [一句]
        ###TONE
        [一句]
        ###TABOO
        [一句]
        ###ANSWERS_DRAFT
        [5到7条短条目，直接给作者当补充回答草稿]
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请基于下面项目，输出一份“懒人默认配置”。

        原始核心想法原句（严禁改题，只能顺着补细节）：
        {raw_idea}

        项目摘要：
        {project_brief}

        作者现有信息：
        - 类型：{existing_genre}
        - 连载赛道：{existing_track}
        - 目标读者：{existing_readership}
        - 目标总字数：{existing_target_length}
        - 预估章节数：{existing_chapter_count}
        - 第一钩子：{existing_hook}
        - 整体气质：{existing_tone}
        - 不要的套路：{existing_taboo}
        - 作者补充回答：{existing_answers}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def build_story_bible_messages(data: dict) -> list[dict[str, str]]:
    project_brief = build_project_brief(data)
    answers = clip_text(get_text(data, "answers"), 5000, "head")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是“平台连载策划 + 悬念型长篇编辑 + 去 AI 味医生”的组合体。
        你要把作者零散的想法和补充回答，整合成一份可直接用于写作的大纲前文档。
        {FANQIE_MARKET_BRIEF}
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        核心原则：
        1. 先把冲突、动机、代价、独特卖点钉牢。
        2. 所有设定都要服务于戏剧推进，而不是堆设定。
        3. 明确指出最容易写出套路化、AI 味、流水账和平台流水线味的地方。
        4. 尽量让人物做事带偏差、代价和个人癖性，避免“标准答案型角色”。
        5. 既要保证平台可读性，也要保证悬念的兑现路线和故事整体闭环。
        6. 反转必须建立在已埋伏笔和人物误判之上，不能靠临时换题。

        输出结构：
        # 一句话卖点
        # 连载赛道落位
        # 故事基线
        # 主角档案
        # 对抗力量
        # 关键配角
        # 人物反差与脆弱点
        # 世界规则或行业规则
        # 情绪与关系主线
        # 追更悬念链
        # 伏笔、假线索与反转路线
        # 开篇前三章抓手
        # 中段防水文方案
        # 容易写出AI味或流水线味的风险点
        # 写作禁忌
        # 结局兑现方向
        总篇幅尽量控制在 2500 到 4200 字内，宁可更凝练，也不要无限展开。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请根据下面的信息，整合出一份适合平台向连载、但明确拒绝流水线写法的“故事圣经”。

        项目摘要：
        {project_brief}

        作者补充回答：
        {answers or "暂无补充回答，请你根据想法做合理补全，但必须把关键空白点指出来。"}

        去AI味护栏：
        {anti_ai_guard}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_character_bible_messages(data: dict) -> list[dict[str, str]]:
    story_bible = clip_text(get_text(data, "story_bible"), 7000, "head")
    outline = clip_text(get_text(data, "outline", "暂无大纲，可结合故事圣经先做人物卡。"), 5000, "head")
    existing_character_notes = clip_text(get_text(data, "character_bible", "无"), 2500, "head")
    character_anchors = extract_character_anchors(existing_character_notes)
    tone = get_text(data, "tone", "未指定")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是平台向长篇连载的人物统筹编辑。
        目标不是简单列人物介绍，而是做一套真正能拿来写长篇的“人物作战手册”。
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        你输出的人物卡必须帮助作者解决这些问题：
        1. 角色为什么会做出不体面但合理的选择。
        2. 每个人说话、撒谎、沉默、发火时的表现差异。
        3. 关系如何随着利益、秘密、愧疚、吸引而变化。
        4. 怎样避免角色写着写着都变成一个人。
        5. 保证角色一眼可辨，适合大众阅读，但绝不能写成扁平工具人。

        强制规则：
        1. 必须严格贴合“故事圣经”“当前大纲”和“已有人物补充或草稿”，不得擅自改成别的行业、别的主线或别的故事类型。
        2. 如果“已有人物补充或草稿”里已经给出姓名、身份、秘密、习惯或关系，必须优先保留并扩写，不能无视，更不能改名重做。
        3. 不要输出“材料为占位符”“以下可替换”“自行套用”等模板化前言，直接进入人物系统正文。
        4. 如果材料较少，可以补足缺失角色，但新增角色也必须围绕现有故事冲突，不要另起炉灶。
        5. 最终文本里必须原样保留“必须保留的现有人物锚点”中已经出现的姓名和关键信息。

        输出结构：
        # 主角卡
        # 核心对手卡
        # 关键配角卡
        # 关系张力图
        # 人物误判与自欺表
        # 对话声线表
        # 人物写作禁手

        每张人物卡尽量包含：
        - 体面外壳
        - 眼前目标
        - 深层恐惧
        - 不愿承认的欲望
        - 自我欺骗
        - 核心秘密
        - 行动习惯
        - 对话习惯
        - 最容易写崩的地方
        总篇幅尽量控制在 2600 到 4200 字内，优先写能直接指导落笔的部分。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请基于下面材料，为这部长篇小说生成一套人物卡系统。

        故事圣经：
        {story_bible}

        当前大纲：
        {outline}

        已有人物补充或草稿：
        {existing_character_notes}

        必须保留的现有人物锚点：
        {character_anchors}

        整体气质：
        {tone}

        去AI味护栏：
        {anti_ai_guard}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_foreshadow_messages(data: dict) -> list[dict[str, str]]:
    story_bible = clip_text(get_text(data, "story_bible"), 6000, "head")
    outline = clip_text(get_text(data, "outline"), 7000, "head")
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 5000, "head")

    system_prompt = dedent(
        f"""
        你是擅长长篇结构设计的伏笔统筹编辑，尤其擅长做“能拉追更、又能兑现”的悬念链。
        你要做的不是堆神秘感，而是建立一张可追踪、可回收、可升级的伏笔表。
        {FORESHADOW_REVERSAL_RULES}
        {CHARACTER_COMPLEXITY_RULES}

        输出要求：
        1. 优先列真正影响剧情推进、人物关系、信息揭露的伏笔，不要列无关的小彩蛋。
        2. 用 Markdown 表格输出。
        3. 表头固定为：伏笔名 | 首次埋设 | 读者先看到什么 | 真相或回收方向 | 回收时机 | 当前状态 | 写作提醒
        4. 表格后再补一段“最容易失联的伏笔”。
        5. 如果大纲里有明显没回收的线，直接指出。
        6. 至少三分之一的伏笔应属于人物、关系、错误判断或情绪余波，而不是纯线索道具。
        7. “读者先看到什么”里要写清表象和误导层；“真相或回收方向”里要写清重解释的落点。
        8. 优先输出 10 到 16 条最关键的伏笔，不要把边角线头全摊开。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请为下面的小说项目建立伏笔表。

        故事圣经：
        {story_bible}

        当前大纲：
        {outline}

        人物卡：
        {character_bible}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_outline_messages(data: dict) -> list[dict[str, str]]:
    story_bible = clip_text(get_text(data, "story_bible"), 8000, "head")
    target_length = get_text(data, "target_length", "未指定")
    chapter_count = get_text(data, "chapter_count", "12")
    tone = get_text(data, "tone", "未指定")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是偏商业向、但对文字质感和悬念兑现要求很高的平台长篇总策划。
        任务是把故事圣经压成可执行大纲，不要写成介绍，不要写成空泛总结。
        {FANQIE_MARKET_BRIEF}
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        你的大纲必须满足：
        1. 开篇第 1 章尽快抛出异常事件、未解问题或危险承诺。
        2. 前 3 章立住主冲突、主角代价，并形成至少一个小闭环。
        3. 主角每个阶段都在做有代价的选择。
        4. 冲突升级靠人物行为和局势变化，不靠“突然出现一个更大的敌人”。
        5. 每 3 到 5 章形成一个小高潮或小闭环，同时推进更大的悬念。
        6. 每章都有推进，不允许原地解释设定，也不允许重复同一种打脸、升级、误会。
        7. 章节卡里必须落到具体动作、场景、关系变化、信息变化和读者会继续追问的问题。
        8. 输出时主动规避 AI 常见毛病：均匀节奏、每章都像总结、情绪全靠标签、对话过分礼貌、解释过多。
        9. 每个重要转折都要让人物暴露偏差、自欺或代价，而不是只把剧情往前推一格。
        10. 反转必须回收前文埋过的细节，并让人物关系或行动方案发生改变。

        输出结构：
        # 作品定位
        # 读者追更承诺
        # 故事总弧线
        # 人物弧线与关系错位
        # 开篇前三章
        # 节奏规划
        # 分幕大纲
        # 章节卡
        章节卡必须逐章编号，并包含：
        - 本章目标
        - 冲突来源
        - 关键场景
        - 局势变化
        - 关系推进
        - 人物错判或自欺
        - 必须出现的具体细节
        - 结尾推动点
        - 写作时要避免的套路
        # 伏笔、假线索与回收表
        # 去AI味执行清单
        如果预计章节数大于 30，请优先细写前 12 章与关键转折，后续章节用分幕和章节簇概述，不要一次性把几十章都展开到极细。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请基于下面的故事圣经，写出一份可以直接开写的长篇小说大纲。

        故事圣经：
        {story_bible}

        目标总字数：
        {target_length}

        预估章节数：
        {chapter_count}

        整体气质：
        {tone}

        去AI味护栏：
        {anti_ai_guard}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_chapter_messages(data: dict) -> list[dict[str, str]]:
    outline = clip_text(get_text(data, "outline"), 9000, "head")
    chapter_beat = clip_text(get_text(data, "chapter_beat"), 3500, "head")
    previous_summary = get_text(data, "previous_summary", "无")
    chapter_word_count = get_text(data, "chapter_word_count", "3000")
    tone = get_text(data, "tone", "未指定")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 6000, "head")
    foreshadow_table = clip_text(get_text(data, "foreshadow_table", "暂无伏笔表。"), 5000, "head")
    plot_memory = clip_text(get_text(data, "plot_memory", "暂无关键剧情记忆。"), 4000, "head")
    foreshadow_memory = clip_text(get_text(data, "foreshadow_memory", "暂无伏笔记忆库。"), 4000, "head")
    chapter_memory = clip_text(get_text(data, "chapter_memory", "暂无连续记忆。"), 3500, "head")
    continuity_notes = clip_text(get_text(data, "continuity_notes", "暂无记忆提醒。"), 2500, "head")

    system_prompt = dedent(
        f"""
        你是成熟的中文小说作者，擅长把章节卡写成真正能读的正文，尤其擅长“平台向但不流水线”的悬念型长篇。
        你的文字目标不是“像AI写得很顺”，而是“像有手感的作者在写现场”。
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}

        绝对执行：
        1. 开场尽快进入事件、异常或冲突，不要先解释半天。
        2. 用场景推进，不用总结合集推进。
        3. 情绪通过动作、停顿、视线、环境、对话落差体现，不用反复贴标签。
        4. 对话必须带潜台词，不要每个人都像在做汇报。
        5. 不要写“他知道这一刻意味着什么”“命运的齿轮开始转动”这类套路句。
        6. 不要把大纲直接翻译成正文；要让同一事件带出细节、误差、阻滞、人物习惯。
        7. 不要在正文里解释主题，不要输出括号说明，不要给读者上课。
        8. 本章既要给读者阶段性满足，也要自然留下继续追更的牵引，不能只靠硬拗反转。
        9. 输出完整正文，不要额外附加说明、标题分析、写作提示。
        10. 每个重要场景都尽量暴露人物的一点私心、偏差、羞耻或自欺，避免角色只为剧情服务。
        11. 反转或推进优先来自已埋细节、错误判断和关系变化，不要靠临时天降新信息。
        12. 伏笔要自然嵌在动作、场景、口头禅、习惯和关系裂缝里，不要硬塞提示牌。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请根据下面的信息写一章正文。

        总体大纲：
        {outline}

        当前章节卡：
        {chapter_beat}

        人物卡：
        {character_bible}

        伏笔表：
        {foreshadow_table}

        关键剧情记忆：
        {plot_memory}

        伏笔记忆库：
        {foreshadow_memory}

        连续记忆：
        {chapter_memory}

        记忆提醒：
        {continuity_notes}

        上一章摘要：
        {previous_summary}

        目标字数：
        约 {chapter_word_count} 字

        整体气质：
        {tone}

        去AI味护栏：
        {anti_ai_guard}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def build_memory_messages(data: dict) -> list[dict[str, str]]:
    story_bible = clip_text(get_text(data, "story_bible", "暂无故事圣经。"), 6000, "head")
    outline = clip_text(get_text(data, "outline", "暂无大纲。"), 12000, "head")
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 6000, "head")
    foreshadow_table = clip_text(get_text(data, "foreshadow_table", "暂无伏笔表。"), 8000, "head")
    plot_memory = get_text(data, "plot_memory", "暂无关键剧情记忆。")
    foreshadow_memory = get_text(data, "foreshadow_memory", "暂无伏笔记忆库。")
    chapter_memory = get_text(data, "chapter_memory", "暂无连续记忆。")
    continuity_notes = get_text(data, "continuity_notes", "暂无记忆提醒。")
    chapter_archive = clip_text(get_text(data, "chapter_archive", "无"), 12000, "tail")
    chapter_beat = get_text(data, "chapter_beat", "无")
    previous_summary = get_text(data, "previous_summary", "无")
    draft = clip_text(get_text(data, "draft", "无"), 8000, "tail")

    system_prompt = dedent(
        f"""
        你是长篇连载项目的“记忆管理编辑”，负责把设定、大纲、已写正文和伏笔线头压成下一轮写作能直接调用的结构化记忆库。
        目标是减少作者自己手动维护剧情、伏笔和连续性的负担。
        {CHARACTER_COMPLEXITY_RULES}
        {FORESHADOW_REVERSAL_RULES}

        执行规则：
        1. 只保留真正影响后续写作的事实、变化、代价和线头，不写空泛感想。
        2. 关键剧情记忆优先记录：已经发生了什么、局势怎么变了、人物关系变到哪一步、哪些秘密/伤势/承诺/道具仍在生效。
        3. 伏笔记忆必须可追踪，要写清伏笔名、首次埋设、当前线索、预期回收方向、紧迫度和当前状态。
        4. 如果材料中存在设定冲突、快失联的伏笔、人物当前误判、自欺、关系裂缝或应该继续提及的细节，统一放进提醒区。
        5. 输出是给作者和后续模型调用的工作记忆，不是写总结文章。

        请严格按下面结构输出，不要增加别的标题：
        ###PLOT_MEMORY
        [8到12条项目符号，记录关键剧情推进、关系变化、秘密、承诺、道具、时间节点、人物当前偏差]
        ###FORESHADOW_MEMORY
        [Markdown 表格；表头固定为：伏笔 | 首埋位置 | 当前掌握线索 | 预期回收 | 紧迫度 | 状态 | 提醒]
        ###CONTINUITY_MEMORY
        [300-500字，写清最近推进、人物关系变化、当前仍在生效的伤势/秘密/承诺/道具、情绪基调、当前最危险的误判]
        ###PREVIOUS_SUMMARY
        [120-180字，专门给下一章调用的上一章摘要]
        ###MEMORY_ALERTS
        [列出最容易断线的剧情、伏笔、人物状态、错误判断、关系裂缝和必须延续的细节]
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请根据下面的材料刷新结构化记忆库。

        故事圣经：
        {story_bible}

        总体大纲：
        {outline}

        人物卡：
        {character_bible}

        伏笔表：
        {foreshadow_table}

        已有关键剧情记忆：
        {plot_memory}

        已有伏笔记忆库：
        {foreshadow_memory}

        已有连续记忆：
        {chapter_memory}

        已有记忆提醒：
        {continuity_notes}

        连载档案（最近内容）：
        {chapter_archive}

        当前章节卡：
        {chapter_beat}

        上一章摘要：
        {previous_summary}

        当前正文：
        {draft}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def build_continue_messages(data: dict) -> list[dict[str, str]]:
    outline = clip_text(get_text(data, "outline"), 9000, "head")
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 6000, "head")
    foreshadow_table = clip_text(get_text(data, "foreshadow_table", "暂无伏笔表。"), 5000, "head")
    plot_memory = clip_text(get_text(data, "plot_memory", "暂无关键剧情记忆。"), 4000, "head")
    foreshadow_memory = clip_text(get_text(data, "foreshadow_memory", "暂无伏笔记忆库。"), 4000, "head")
    chapter_memory = clip_text(get_text(data, "chapter_memory", "暂无连续记忆。"), 3500, "head")
    continuity_notes = clip_text(get_text(data, "continuity_notes", "暂无记忆提醒。"), 2500, "head")
    chapter_archive = clip_text(get_text(data, "chapter_archive", "无"), 9000, "tail")
    chapter_beat = clip_text(get_text(data, "chapter_beat", "无"), 3000, "head")
    draft = clip_text(get_text(data, "draft", "无"), 6000, "tail")
    previous_summary = get_text(data, "previous_summary", "无")
    chapter_word_count = get_text(data, "chapter_word_count", "3000")
    tone = get_text(data, "tone", "未指定")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是长篇连载的“统筹作者 + 连续性编辑”。
        你要先判断当前已经写到哪里，再从大纲里接出下一章，并直接写出下一章正文。
        {FANQIE_SERIAL_PRINCIPLES}
        {CHARACTER_COMPLEXITY_RULES}
        {ANTI_CLICHE_PLOT_RULES}
        {FORESHADOW_REVERSAL_RULES}
        你的续写要满足：
        1. 下一章必须承接上一章的余波和当前最大悬念，不要像重开新故事。
        2. 章节卡和正文都要和大纲、人物卡、伏笔表一致。
        3. 如果当前章节还没写到大纲应有的结尾推动点，先视为这一章已完成，再顺着它写下一章，不要重写本章。
        4. 下一章既要给局部满足，也要推进更大的谜团，不能原地兜圈。
        5. 输出的下一章必须继续规避 AI 味和流水线味：不要总结构句、不要万能解释、不要礼貌型对话、不要换皮重复桥段。
        6. 下一章要让人物暴露新的偏差、羞耻或误判，不要只让剧情机关自己运转。
        7. 下一章的推进和反转必须优先回收现有伏笔、假线索和关系裂缝，不要靠天降新设定。

        请严格按以下结构输出，不要多写别的标题：
        ###NEXT_BEAT
        [完整的下一章章节卡，沿用“第X章 标题”格式，并包含目标/冲突/场景/变化/关系/人物错判/伏笔推进/细节/结尾推动点/避免套路]
        ###NEXT_DRAFT
        [下一章正文]
        ###UPDATED_PLOT_MEMORY
        [沿用关键剧情记忆格式，保留仍然生效的事实并补上本章推进]
        ###UPDATED_FORESHADOW_MEMORY
        [沿用伏笔记忆库格式，保留仍然有效的伏笔并更新新增/推进/回收]
        ###UPDATED_CONTINUITY_MEMORY
        [给后续续写用的连续记忆，300-500字]
        ###NEXT_PREVIOUS_SUMMARY
        [对刚生成这一章的120-180字摘要]
        ###MEMORY_ALERTS
        [本章后最容易断线的剧情、伏笔、人物状态和必须继续提及的提醒]
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请在这部长篇里自动续写下一章。

        总体大纲：
        {outline}

        人物卡：
        {character_bible}

        伏笔表：
        {foreshadow_table}

        关键剧情记忆：
        {plot_memory}

        伏笔记忆库：
        {foreshadow_memory}

        当前连续记忆：
        {chapter_memory}

        当前记忆提醒：
        {continuity_notes}

        连载档案（最近内容）：
        {chapter_archive}

        当前章节卡：
        {chapter_beat}

        当前正文：
        {draft}

        上一章摘要：
        {previous_summary}

        下一章目标字数：
        约 {chapter_word_count} 字

        整体气质：
        {tone}

        去AI味护栏：
        {anti_ai_guard}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def build_polish_messages(data: dict) -> list[dict[str, str]]:
    draft = clip_text(get_text(data, "draft"), 9000, "tail")
    outline = clip_text(get_text(data, "outline", "无"), 7000, "head")
    chapter_beat = clip_text(get_text(data, "chapter_beat", "无"), 3000, "head")
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 5000, "head")
    plot_memory = clip_text(get_text(data, "plot_memory", "暂无关键剧情记忆。"), 3000, "head")
    foreshadow_memory = clip_text(get_text(data, "foreshadow_memory", "暂无伏笔记忆库。"), 3000, "head")
    chapter_memory = clip_text(get_text(data, "chapter_memory", "暂无连续记忆。"), 2500, "head")
    continuity_notes = clip_text(get_text(data, "continuity_notes", "暂无记忆提醒。"), 2000, "head")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是专门负责“去AI味”和“保留剧情事实”的小说改稿编辑。
        你的任务是把现有正文改得更像作者写的，而不是另起炉灶。
        {CHARACTER_COMPLEXITY_RULES}
        {FORESHADOW_REVERSAL_RULES}

        执行规则：
        1. 不改变核心剧情事实、人物关系、事件顺序。
        2. 删掉空泛解释、模板化抒情、平均句式、重复情绪词和流水线桥段口吻。
        3. 把能落地的句子落到动作、声音、物件、空间、语气上。
        4. 对话去掉“标准答案感”，保留一点人和人之间的别扭、试探、遮掩。
        5. 把脸谱化人物改得更具体：保留其私心、羞耻、犹豫和不体面的选择痕迹。
        6. 让悬念线索更可追踪，但不要凭空新加关键剧情。
        7. 如果原文的推进显得俗套，优先通过语气、细节、人物反应和伏笔显影去救，不要改剧情骨架。
        8. 只输出润色后的正文，不要加任何说明。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请在不改剧情事实的前提下，润色下面这段正文，重点去掉AI味。

        总体大纲：
        {outline}

        当前章节卡：
        {chapter_beat}

        人物卡：
        {character_bible}

        关键剧情记忆：
        {plot_memory}

        伏笔记忆库：
        {foreshadow_memory}

        连续记忆：
        {chapter_memory}

        记忆提醒：
        {continuity_notes}

        去AI味护栏：
        {anti_ai_guard}

        待润色正文：
        {draft}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def build_batch_polish_messages(data: dict) -> list[dict[str, str]]:
    chapter_archive = clip_text(get_text(data, "chapter_archive"), 12000, "tail")
    character_bible = clip_text(get_text(data, "character_bible", "暂无人物卡。"), 5000, "head")
    anti_ai_guard = get_text(data, "anti_ai_guard", ANTI_AI_GUARD_DEFAULT)

    system_prompt = dedent(
        f"""
        你是长篇小说的整章统稿编辑，负责批量去AI味。
        你会面对多章连在一起的文本，要求你统一声线、清掉模板感，但绝不破坏事实和章节顺序。
        {CHARACTER_COMPLEXITY_RULES}
        {FORESHADOW_REVERSAL_RULES}

        执行规则：
        1. 保留原有章节标题、编号和分隔格式。
        2. 不擅自增删主要剧情，只做语言层面的去AI味与连贯性修正。
        3. 同一人物的说话方式要统一，同一条情绪线要有余波。
        4. 删除空泛总结、套路转折词、过于均匀的句式和重复爽点口吻。
        5. 把脸谱化人物往具体的人身上拉：保留其私心、弱点、惯性和说话纹理。
        6. 如果原文里已有好句，不要全部磨平。
        7. 让悬念链更清楚：哪些问题被推进了，哪些问题仍悬着，要让读者感觉得到；伏笔不要在统稿时被磨掉。
        8. 只输出润色后的完整文本，不要附加说明。
        """
    ).strip()

    user_prompt = dedent(
        f"""
        请对下面的连载档案做整章批量去AI味润色。

        人物卡：
        {character_bible}

        去AI味护栏：
        {anti_ai_guard}

        连载档案：
        {chapter_archive}
        """
    ).strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


@app.route("/")
@app.route("/studio")
def studio():
    return render_template("novel_workshop.html", anti_ai_guard=ANTI_AI_GUARD_DEFAULT)


@app.route("/healthz")
def healthz():
    return jsonify(
        {
            "ok": True,
            "archive_backend": "local",
        }
    )


@app.route("/api/archive/save", methods=["POST"])
def archive_save():
    data = request.get_json(silent=True) or {}
    try:
        archive_id = validate_archive_id(get_text(data, "archive_id"))
    except ValueError as exc:
        return error_response(str(exc))

    payload = data.get("payload")
    if not isinstance(payload, dict) or not payload:
        return error_response("请先提供要保存的存档内容。")

    try:
        save_archive_snapshot(archive_id, payload)
    except RuntimeError as exc:
        app.logger.error(str(exc))
        return error_response(str(exc), status=500)
    except Exception as exc:
        app.logger.error("Archive save failed: %s", exc)
        return error_response("存档保存失败，请稍后重试。", status=500)

    return jsonify({"ok": True, "archive_id": archive_id})


@app.route("/api/archive/load", methods=["POST"])
def archive_load():
    data = request.get_json(silent=True) or {}
    try:
        archive_id = validate_archive_id(get_text(data, "archive_id"))
    except ValueError as exc:
        return error_response(str(exc))

    try:
        payload = load_archive_snapshot(archive_id)
    except RuntimeError as exc:
        app.logger.error(str(exc))
        return error_response(str(exc), status=500)
    except Exception as exc:
        app.logger.error("Archive load failed: %s", exc)
        return error_response("存档读取失败，请稍后重试。", status=500)

    if not payload:
        return error_response("没有找到这个存档，请确认存档编号是否正确。", status=404)

    return jsonify({"ok": True, "archive_id": archive_id, "payload": payload})


@app.route("/api/novel/autofill", methods=["POST"])
def novel_autofill():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "idea"):
        return error_response("请先输入你的核心想法。")
    return make_text_response(
        "GEN1",
        build_autofill_messages(data),
        temperature=0.25,
        data=data,
        postprocess=lambda raw: normalize_autofill_output(raw, data),
    )


@app.route("/api/novel/questions", methods=["POST"])
def novel_questions():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "idea"):
        return error_response("请先输入你的核心想法。")
    return make_stream_response("GEN1", build_questions_messages(data), temperature=0.6, data=data)


@app.route("/api/novel/story-bible", methods=["POST"])
def novel_story_bible():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "idea"):
        return error_response("请先输入你的核心想法。")
    return make_stream_response("GEN1", build_story_bible_messages(data), temperature=0.68, data=data)


@app.route("/api/novel/characters", methods=["POST"])
def novel_characters():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "story_bible"):
        return error_response("请先生成或填写故事圣经，再做人物卡。")
    return make_stream_response("GEN1", build_character_bible_messages(data), temperature=0.48, data=data)


@app.route("/api/novel/foreshadow", methods=["POST"])
def novel_foreshadow():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "outline"):
        return error_response("请先生成大纲，再整理伏笔表。")
    return make_stream_response("GEN1", build_foreshadow_messages(data), temperature=0.58, data=data)


@app.route("/api/novel/outline", methods=["POST"])
def novel_outline():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "story_bible"):
        return error_response("请先生成或填写故事圣经。")
    return make_stream_response("GEN1", build_outline_messages(data), temperature=0.7, data=data)


@app.route("/api/novel/chapter", methods=["POST"])
def novel_chapter():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "outline"):
        return error_response("请先提供大纲。")
    if not get_text(data, "chapter_beat"):
        return error_response("请先填写当前章节卡。")
    return make_stream_response("GEN1", build_chapter_messages(data), temperature=0.8, data=data)


@app.route("/api/novel/memory", methods=["POST"])
def novel_memory():
    data = request.get_json(silent=True) or {}
    if not any(
        [
            get_text(data, "chapter_archive"),
            get_text(data, "draft"),
            get_text(data, "outline"),
            get_text(data, "story_bible"),
            get_text(data, "foreshadow_table"),
        ]
    ):
        return error_response("请至少提供故事圣经、大纲、伏笔表、当前正文或连载档案中的任意一项，再刷新记忆库。")
    return make_stream_response("GEN1", build_memory_messages(data), temperature=0.55, data=data)


@app.route("/api/novel/continue", methods=["POST"])
def novel_continue():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "outline"):
        return error_response("请先生成大纲，再自动续写下一章。")
    return make_stream_response("GEN1", build_continue_messages(data), temperature=0.78, data=data)


@app.route("/api/novel/polish", methods=["POST"])
def novel_polish():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "draft"):
        return error_response("请先提供要润色的正文。")
    return make_stream_response("GEN1", build_polish_messages(data), temperature=0.62, data=data)


@app.route("/api/novel/batch-polish", methods=["POST"])
def novel_batch_polish():
    data = request.get_json(silent=True) or {}
    if not get_text(data, "chapter_archive"):
        return error_response("请先准备连载档案，再做整章批量去AI味。")
    return make_stream_response("GEN1", build_batch_polish_messages(data), temperature=0.56, data=data)


if __name__ == "__main__":
    port = int(get_setting("PORT", get_setting("APP_PORT", "20000")) or "20000")
    app.run(debug=True, port=port, host="0.0.0.0")
