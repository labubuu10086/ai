const STORAGE_KEY = "novel_workshop_state_v5";
const LEGACY_STORAGE_KEYS = ["novel_workshop_state_v5", "novel_workshop_state_v4"];
const API_PROFILES_KEY = "novel_workshop_api_profiles_v1";
const DEFAULT_API_PROFILE_ID = "__env_default__";
const CUSTOM_OPTION_VALUE = "__custom__";
const RANDOM_GENDER_VALUE = "__random__";

const fieldIds = [
    "preset-select",
    "api-profile-select",
    "api-profile-name",
    "api-base-url",
    "api-key",
    "api-model",
    "idea",
    "genre-select",
    "genre-custom",
    "fanqie-track",
    "readership",
    "target-length-select",
    "target-length-custom",
    "chapter-count",
    "hook-core",
    "tone",
    "taboo",
    "questions-output",
    "answers",
    "story-bible",
    "character-bible",
    "character-role",
    "character-gender",
    "character-name",
    "character-age",
    "character-identity",
    "character-relationship",
    "character-look",
    "character-voice",
    "character-goal",
    "character-fear",
    "character-secret",
    "character-habit",
    "foreshadow-table",
    "outline-output",
    "anti-ai-guard",
    "chapter-beat",
    "previous-summary",
    "chapter-word-count",
    "chapter-draft",
    "plot-memory",
    "foreshadow-memory",
    "chapter-memory",
    "continuity-notes",
    "chapter-archive",
    "batch-polish-output",
];

const memorySectionMap = {
    PLOT_MEMORY: "plot-memory",
    FORESHADOW_MEMORY: "foreshadow-memory",
    CONTINUITY_MEMORY: "chapter-memory",
    PREVIOUS_SUMMARY: "previous-summary",
    MEMORY_ALERTS: "continuity-notes",
};

const presetDefinitions = {
    suspense: {
        genre: "悬疑脑洞",
        fanqie_track: "悬疑脑洞",
        readership: "悬疑向连载读者：想看线索回收、持续追问和反转兑现",
        target_length: "20万字",
        chapter_count: "50",
        tone: "阴冷悬疑",
        taboo: "不要强行反转，不要恶意水文，不要重复误会拉扯",
        chapter_word_count: "3000",
    },
    urban: {
        genre: "都市脑洞",
        fanqie_track: "都市脑洞",
        readership: "脑洞向连载读者：要设定新鲜、钩子明显、节奏偏快",
        target_length: "18万字",
        chapter_count: "45",
        tone: "锋利克制",
        taboo: "不要机械打脸，不要万能系统兜底，不要纯升级复读",
        chapter_word_count: "3000",
    },
    apocalypse: {
        genre: "科幻末世",
        fanqie_track: "科幻末世",
        readership: "男频大众连载读者：喜欢快节奏、强外部冲突和明确升级感",
        target_length: "25万字",
        chapter_count: "60",
        tone: "高燃紧绷",
        taboo: "不要重复刷怪，不要纯升级复读，不要硬塞设定讲解",
        chapter_word_count: "3200",
    },
    "female-suspense": {
        genre: "现言悬疑",
        fanqie_track: "女频悬疑",
        readership: "女频大众连载读者：想看强关系、强情绪回报和持续追更点",
        target_length: "18万字",
        chapter_count: "48",
        tone: "暧昧危险",
        taboo: "不要工业糖精，不要重复误会拉扯，不要为了虐而虐",
        chapter_word_count: "2800",
    },
    romantasy: {
        genre: "玄幻言情",
        fanqie_track: "玄幻言情",
        readership: "精品向连载读者：既要好读，也在意故事完整度和后劲",
        target_length: "25万字",
        chapter_count: "60",
        tone: "热烈奇诡",
        taboo: "不要工业糖精，不要空转暧昧，不要设定堆砌代替剧情",
        chapter_word_count: "3000",
    },
};

const characterRoleOptions = ["主角", "核心对手", "关键配角", "关系角色", "神秘人物"];

const characterPoolBase = {
    surnames: ["林", "周", "沈", "陆", "许", "程", "宋", "闻", "贺", "谢", "秦", "顾", "裴", "江", "孟"],
    femaleGiven: ["见深", "知遥", "听晚", "明微", "迟雪", "映真", "照眠", "南乔", "既月", "观澜"],
    maleGiven: ["既白", "闻野", "景行", "砚舟", "怀川", "叙安", "照临", "知晏", "沉星", "越川"],
    neutralGiven: ["停云", "照夜", "长予", "归迟", "见川", "言蹊", "一岚", "观棋", "拂晓", "未迟"],
    identities: [
        "旧城档案修复师",
        "夜班急诊记录员",
        "街区网格员",
        "殡仪馆礼仪顾问",
        "二手书店老板",
        "社区调解员",
    ],
    looks: [
        "总把袖口卷得很整齐，右手虎口有旧伤",
        "站着时肩背太直，像随时准备转身离开",
        "衣着不惹眼，但鞋总擦得异常干净",
        "说话时很少直视人，笑起来却像故意安抚对方",
    ],
    voices: [
        "句子短，先否认一句，再把真正想说的补半句",
        "表面客气，真正生气时反而会笑",
        "喜欢先替别人找借口，再慢慢把话钉死",
        "平时很省字，一旦提到痛点就会不自觉说快",
    ],
    habits: [
        "说谎前会先替对方圆场",
        "紧张时会反复摸杯沿或衣角",
        "每次做决定前都会先看一眼出口",
        "听到关键字时会先沉默两秒再开口",
    ],
    identitiesByRole: {
        主角: ["事故调查记者", "民俗播客主持人", "失业后接私活的证据整理师", "夜班清障队外包员"],
        核心对手: ["连锁机构负责人", "旧案核心知情人", "地方资源操盘手", "热门项目投资人"],
        关键配角: ["法医助理", "社区保安队长", "实习律师", "旧货市场消息贩子"],
        关系角色: ["主角前任", "失联多年的同学", "关系紧绷的亲属", "曾一起扛事的搭档"],
        神秘人物: ["匿名投稿人", "总在现场附近出现的陌生住户", "不肯留名的线人", "身份成谜的临时租客"],
    },
    goals: {
        主角: ["赶在更坏的事发生前查清第一条线索", "保住眼下的饭碗，同时把真正的幕后人逼出来", "证明自己没有疯，也没有看错危险信号"],
        核心对手: ["把局势重新压回自己能控制的范围", "让主角继续误判真正的危险方向", "在代价失控前切断所有知情人的联系"],
        关键配角: ["先保住自己或家人的安全，再决定站哪边", "借这次事件换一个翻身机会", "瞒住自己最怕被知道的那段过去"],
        关系角色: ["确认主角到底还值不值得信", "把旧账算清，同时避免局面彻底翻脸", "在帮主角和自保之间找到暂时平衡"],
        神秘人物: ["把关键信息分阶段放出来，逼人走到自己想要的位置", "确认主角是不是值得继续押注", "借别人之手完成自己不方便做的事"],
    },
    fears: {
        主角: ["最怕自己终于找到真相时，已经来不及救人", "最怕再一次因为迟疑，让无辜的人替自己背代价", "最怕自己其实正在被人故意牵着走"],
        核心对手: ["最怕自己维持多年的秩序被一个意外戳穿", "最怕旧案重新翻出来，把自己最不体面的选择暴露给所有人", "最怕主角发现真正的因果链不是现在这条"],
        关键配角: ["最怕被当成可以随时牺牲的边角料", "最怕自己一旦说真话，最重要的人会先遭殃", "最怕事情发展到无法回头时，自己已经站错队"],
        关系角色: ["最怕再重演一次当年那种失控", "最怕自己嘴上说不在乎，身体却还是先护着主角", "最怕和主角之间只剩利用价值"],
        神秘人物: ["最怕还没把人逼到位，自己先露底", "最怕最关键的那个人没有按计划成长起来", "最怕自己以为的补救，其实只是把旧错再做一遍"],
    },
    secrets: {
        主角: ["曾经在一次关键事件里删掉过对自己不利的证据", "真正吸引主角追查到底的，不只是正义，还有一笔只属于自己的旧账", "主角和第一起异常事件并不是第一次产生联系"],
        核心对手: ["对手并不是整件事的源头，但确实为了自保改写过一段真相", "对手一直在追查另一个更高层的危险，却不能让任何人先知道", "对手当年做过一个看似正确、实际害死人的决定"],
        关键配角: ["配角手里一直留着一份能翻盘的原始记录", "配角曾经为了活下去出卖过一个人", "配角知道谁会是下一次爆炸点，却不敢直接说破"],
        关系角色: ["关系角色其实一直在替主角瞒一件足以翻脸的事", "关系角色是当年那场事故里最早逃走的人之一", "关系角色嘴上在拦主角，暗地里却早已开始布局"],
        神秘人物: ["神秘人物比主角更早知道结局会往哪边塌", "神秘人物用错了方式补救旧事，才把现在的局面推到失控边缘", "神秘人物一直在筛选谁配活到真相揭开那一刻"],
    },
    relationships: {
        主角: ["他/她是主线被卷进去的第一观察者，也是最不肯认输的那个人", "他/她知道自己不适合当英雄，但每次都被逼到只能往前", "他/她看起来在追真相，其实也在追一个迟到很多年的答案"],
        核心对手: ["表面上站在主角对面，实际上握着最完整的信息差", "看起来像最大阻力，实则是在用更冷的方式处理同一件事", "对主角既有压制也有试探，一直在判断要不要把人彻底逼走"],
        关键配角: ["是主角推进线索时最容易失去、也最容易翻盘的人", "既能帮主角过桥，也可能在关键处反手抽梯子", "最初只是旁观者，后来却被迫成为局势的一部分"],
        关系角色: ["和主角之间有旧情、旧债或旧误会，任何合作都带着情绪余波", "明知道该和主角保持距离，却总在最糟的时候先出手", "他/她最了解主角的软肋，也最知道往哪一句话上捅最疼"],
        神秘人物: ["总比别人早一步出现或离开，像在故意控制信息流速", "每次留下的都不是完整答案，而是刚好够把人逼进下一步的碎片", "看起来像偶然闯入，实际一直在主线边缘观察所有人"],
    },
};

const characterFlavorPools = {
    suspense: {
        identities: ["案卷整理员", "直播事故善后师", "心理热线接线员", "民俗调查顾问"],
        looks: ["习惯戴一次性手套翻东西，像怕留下什么", "看人时总先看鞋边和手指，而不是看脸"],
        voices: ["提到关键细节时会突然压低音量，像怕隔墙有人", "不说废话，但每句都像故意留了半格空白"],
        habits: ["进门后会先数出口和窗户", "听到异响时会立刻停下所有小动作"],
    },
    urban: {
        identities: ["品牌公关顾问", "商场招商主管", "网约车车队管理员", "高端公寓前台主管"],
        looks: ["衣着利落，手机永远电量充足", "表情管理很好，但疲惫感总藏在眼底"],
        voices: ["会把锋利的话包在体面措辞里", "说到利益时语速会稳定得可怕"],
        habits: ["每隔几分钟就下意识看一次时间", "收到消息先不回，先观察周围人的反应"],
    },
    apocalypse: {
        identities: ["临时避难点值守员", "物资盘点官", "边缘区拾荒车驾驶员", "地下电网维修工"],
        looks: ["衣服总有修补痕迹，腰间习惯挂多功能工具", "说不上狼狈，但所有东西都以逃命优先摆放"],
        voices: ["说话很直接，像省着每一口力气", "不爱安慰人，给出的都是能活下去的办法"],
        habits: ["先确认水和出口，再决定要不要坐下", "和人说话时永远让背后靠墙"],
    },
    romantasy: {
        identities: ["禁库抄录师", "失势世家继承人", "宗门外执事", "替人收债的灵契中介"],
        looks: ["身上总带着一股若有若无的药香或灰烬味", "看着矜持，手上却全是实打实的旧伤"],
        voices: ["话里听着温和，实则每句都在试探底线", "能把拒绝说得很轻，却一点退路都不给"],
        habits: ["生气时反而会把衣袖理得更平", "思考时会无意识摩挲旧玉、戒指或护符"],
    },
    historical: {
        identities: ["驿站抄报人", "账房先生", "城门胥吏", "偏僻州府讼师"],
        looks: ["衣料朴素却打理得一丝不苟", "说话前总像先在脑子里过一遍利害"],
        voices: ["惯用轻描淡写的方式说重话", "越是有把握，语气越慢"],
        habits: ["落座前先看谁坐在上风口", "一听到官面上的话，就会先把表情收干净"],
    },
};

let apiProfiles = [];

function byId(id) {
    return document.getElementById(id);
}

function getFieldValue(id) {
    const field = byId(id);
    return field ? field.value.trim() : "";
}

function setFieldValue(id, value) {
    const field = byId(id);
    if (field) {
        field.value = value;
    }
}

function hasFieldValue(id) {
    return Boolean(getFieldValue(id));
}

function getPasswordValue(id) {
    const field = byId(id);
    return field ? field.value.trim() : "";
}

function sample(list) {
    if (!Array.isArray(list) || !list.length) {
        return "";
    }
    return list[Math.floor(Math.random() * list.length)];
}

function uniqueList(values) {
    return [...new Set((values || []).filter(Boolean))];
}

function mergeArrayMap(base = {}, extra = {}) {
    const keys = new Set([...Object.keys(base), ...Object.keys(extra)]);
    const merged = {};
    keys.forEach((key) => {
        merged[key] = uniqueList([...(base[key] || []), ...(extra[key] || [])]);
    });
    return merged;
}

function buildCharacterPool(flavorKey) {
    const flavor = characterFlavorPools[flavorKey] || {};
    return {
        surnames: uniqueList([...(characterPoolBase.surnames || []), ...(flavor.surnames || [])]),
        femaleGiven: uniqueList([...(characterPoolBase.femaleGiven || []), ...(flavor.femaleGiven || [])]),
        maleGiven: uniqueList([...(characterPoolBase.maleGiven || []), ...(flavor.maleGiven || [])]),
        neutralGiven: uniqueList([...(characterPoolBase.neutralGiven || []), ...(flavor.neutralGiven || [])]),
        identities: uniqueList([...(characterPoolBase.identities || []), ...(flavor.identities || [])]),
        looks: uniqueList([...(characterPoolBase.looks || []), ...(flavor.looks || [])]),
        voices: uniqueList([...(characterPoolBase.voices || []), ...(flavor.voices || [])]),
        habits: uniqueList([...(characterPoolBase.habits || []), ...(flavor.habits || [])]),
        identitiesByRole: mergeArrayMap(characterPoolBase.identitiesByRole, flavor.identitiesByRole),
        goals: mergeArrayMap(characterPoolBase.goals, flavor.goals),
        fears: mergeArrayMap(characterPoolBase.fears, flavor.fears),
        secrets: mergeArrayMap(characterPoolBase.secrets, flavor.secrets),
        relationships: mergeArrayMap(characterPoolBase.relationships, flavor.relationships),
    };
}

function resolveChoiceValue(selectId, customId) {
    const selectValue = getFieldValue(selectId);
    if (selectValue === CUSTOM_OPTION_VALUE) {
        return getFieldValue(customId);
    }
    return selectValue;
}

function syncChoiceField(selectId, customId) {
    const select = byId(selectId);
    const custom = byId(customId);
    const isCustom = select.value === CUSTOM_OPTION_VALUE;
    custom.disabled = !isCustom;
    if (isCustom && document.activeElement === select) {
        custom.focus();
    }
}

function setChoiceValue(selectId, customId, value) {
    const select = byId(selectId);
    const custom = byId(customId);
    const normalized = (value || "").trim();
    const hasOption = [...select.options].some((option) => option.value === normalized && option.value !== CUSTOM_OPTION_VALUE);

    if (!normalized) {
        select.value = "";
        custom.value = "";
    } else if (hasOption) {
        select.value = normalized;
        custom.value = "";
    } else {
        select.value = CUSTOM_OPTION_VALUE;
        custom.value = normalized;
    }

    syncChoiceField(selectId, customId);
}

function normalizeLooseText(value) {
    return (value || "").replace(/\s+/g, "").trim();
}

function findMatchingOptionValue(selectId, value) {
    const select = byId(selectId);
    if (!select) {
        return "";
    }

    const normalized = normalizeLooseText(value);
    if (!normalized) {
        return "";
    }

    const options = [...select.options].filter((option) => option.value);
    const exact = options.find((option) => normalizeLooseText(option.value) === normalized);
    if (exact) {
        return exact.value;
    }

    const partial = options.find((option) => {
        const optionValue = normalizeLooseText(option.value);
        return optionValue.includes(normalized) || normalized.includes(optionValue);
    });

    return partial ? partial.value : "";
}

function setSelectSmart(selectId, value, { force = false, fallback = "" } = {}) {
    const select = byId(selectId);
    if (!select) {
        return;
    }

    const normalized = (value || "").trim();
    if (!normalized) {
        return;
    }

    if (!force && getFieldValue(selectId)) {
        return;
    }

    const matched = findMatchingOptionValue(selectId, normalized);
    if (matched) {
        select.value = matched;
        return;
    }

    if (fallback) {
        select.value = fallback;
    }
}

function setTextSmart(id, value, { force = false } = {}) {
    const field = byId(id);
    if (!field) {
        return;
    }

    const normalized = (value || "").trim();
    if (!normalized) {
        return;
    }

    const current = field.type === "password" ? getPasswordValue(id) : getFieldValue(id);
    if (!force && current) {
        return;
    }

    field.value = normalized;
}

function applyAutofillSections(sections, { force = false } = {}) {
    const genreValue = (sections.GENRE || "").trim();
    if (genreValue && (force || !resolveChoiceValue("genre-select", "genre-custom"))) {
        setChoiceValue("genre-select", "genre-custom", genreValue);
    }

    const targetLengthValue = (sections.TARGET_LENGTH || "").trim();
    if (targetLengthValue && (force || !resolveChoiceValue("target-length-select", "target-length-custom"))) {
        setChoiceValue("target-length-select", "target-length-custom", targetLengthValue);
    }

    setSelectSmart("fanqie-track", sections.FANQIE_TRACK, { force, fallback: "其他 / 混合赛道" });
    setSelectSmart("readership", sections.READERSHIP, { force });
    setTextSmart("chapter-count", sections.CHAPTER_COUNT, { force });
    setTextSmart("hook-core", sections.HOOK_CORE, { force });
    setTextSmart("tone", sections.TONE, { force });
    setTextSmart("taboo", sections.TABOO, { force });
    setTextSmart("answers", sections.ANSWERS_DRAFT, { force });
}

function detectCharacterFlavor() {
    const source = [
        resolveChoiceValue("genre-select", "genre-custom"),
        getFieldValue("fanqie-track"),
        getFieldValue("tone"),
        getFieldValue("idea"),
    ].join(" ");

    if (/末世|废土|感染|科幻/.test(source)) {
        return "apocalypse";
    }
    if (/玄幻|仙|古言|言情|妖|宗门|宫廷/.test(source)) {
        return "romantasy";
    }
    if (/历史|朝堂|州府|年代/.test(source)) {
        return "historical";
    }
    if (/都市|职场|现实|公寓|商场/.test(source)) {
        return "urban";
    }
    if (/悬疑|惊悚|诡|凶|罪|直播|民俗/.test(source)) {
        return "suspense";
    }
    return "default";
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickCharacterValue(pool, key, role) {
    const rolePool = pool[key]?.[role];
    return sample(rolePool?.length ? rolePool : pool[key]);
}

function generateCharacterName(gender, pool) {
    const surname = sample(pool.surnames);
    const givenPool = gender === "女"
        ? pool.femaleGiven
        : gender === "男"
            ? pool.maleGiven
            : pool.neutralGiven;
    return `${surname}${sample(givenPool)}`;
}

function generateCharacterAge(role) {
    const ranges = {
        主角: [22, 34],
        核心对手: [30, 46],
        关键配角: [24, 40],
        关系角色: [22, 38],
        神秘人物: [28, 52],
    };
    const [min, max] = ranges[role] || [24, 40];
    return String(randomInt(min, max));
}

function fillRandomCharacterDraft() {
    const role = getFieldValue("character-role") || sample(characterRoleOptions);
    const selectedGender = getFieldValue("character-gender");
    const gender = selectedGender && selectedGender !== RANDOM_GENDER_VALUE ? selectedGender : sample(["女", "男", "模糊处理"]);
    const pool = buildCharacterPool(detectCharacterFlavor());

    setFieldValue("character-role", role);
    setFieldValue("character-gender", gender);
    setFieldValue("character-name", generateCharacterName(gender, pool));
    setFieldValue("character-age", generateCharacterAge(role));
    setFieldValue("character-identity", pickCharacterValue(pool, "identitiesByRole", role) || sample(pool.identities));
    setFieldValue("character-relationship", pickCharacterValue(pool, "relationships", role));
    setFieldValue("character-look", sample(pool.looks));
    setFieldValue("character-voice", sample(pool.voices));
    setFieldValue("character-goal", pickCharacterValue(pool, "goals", role));
    setFieldValue("character-fear", pickCharacterValue(pool, "fears", role));
    setFieldValue("character-secret", pickCharacterValue(pool, "secrets", role));
    setFieldValue("character-habit", sample(pool.habits));
    saveState();
    setStatus(`已随机生成一版${role}草稿。你可以先改细节，再写入人物卡。`, "done");
}

function buildCharacterDraftBlock() {
    const name = getFieldValue("character-name");
    const role = getFieldValue("character-role");
    const genderRaw = getFieldValue("character-gender");
    const gender = genderRaw && genderRaw !== RANDOM_GENDER_VALUE ? genderRaw : "未设定";
    const age = getFieldValue("character-age") || "未设定";
    const identity = getFieldValue("character-identity");
    const relationship = getFieldValue("character-relationship");
    const look = getFieldValue("character-look");
    const voice = getFieldValue("character-voice");
    const goal = getFieldValue("character-goal");
    const fear = getFieldValue("character-fear");
    const secret = getFieldValue("character-secret");
    const habit = getFieldValue("character-habit");

    if (!(name || identity || secret)) {
        return "";
    }

    return [
        `### 手动人物草稿：${name || "未命名人物"}`,
        `- 定位：${role || "未设定"}`,
        `- 性别 / 年龄：${gender} / ${age}`,
        `- 表面身份：${identity || "未设定"}`,
        `- 与主线关系：${relationship || "未设定"}`,
        `- 外在识别点：${look || "未设定"}`,
        `- 眼前目标：${goal || "未设定"}`,
        `- 深层恐惧：${fear || "未设定"}`,
        `- 核心秘密：${secret || "未设定"}`,
        `- 行动习惯：${habit || "未设定"}`,
        `- 对话习惯：${voice || "未设定"}`,
    ].join("\n");
}

function appendCharacterDraftToBible() {
    const block = buildCharacterDraftBlock();
    if (!block) {
        setStatus("先随机生成一版人物，或者至少补上名字、身份、秘密中的一项再写入。", "error");
        return;
    }

    const target = byId("character-bible");
    const current = target.value.trim();
    const nextValue = current
        ? `${current}\n\n${block}`
        : `# 手动补充人物草稿\n\n${block}`;

    target.value = nextValue;
    saveState();
    setStatus(`${getFieldValue("character-name") || "这名人物"}已经写入人物卡区。`, "done");
}

function hasManualCharacterDrafts() {
    const current = getFieldValue("character-bible");
    return current.includes("### 手动人物草稿：") || current.includes("# 手动补充人物草稿");
}

function isCharacterBibleDraftOnly() {
    const current = getFieldValue("character-bible");
    if (!current) {
        return false;
    }
    return !/# 主角卡|# 核心对手卡|# 关键配角卡|# 关系张力图|# 对话声线表/.test(current);
}

function prepareCharacterBibleForExpansion() {
    const target = byId("character-bible");
    const current = target.value.trim();
    if (!current) {
        return false;
    }

    if (hasManualCharacterDrafts() && !current.includes("# AI 扩写人物卡")) {
        target.value = `${current}\n\n# AI 扩写人物卡\n\n`;
    } else {
        target.value = `${current}\n\n`;
    }
    saveState();
    return true;
}

function needsAutofillSeed() {
    if (!hasFieldValue("idea")) {
        return false;
    }

    return [
        resolveChoiceValue("genre-select", "genre-custom"),
        getFieldValue("fanqie-track"),
        getFieldValue("readership"),
        resolveChoiceValue("target-length-select", "target-length-custom"),
        getFieldValue("chapter-count"),
        getFieldValue("hook-core"),
        getFieldValue("tone"),
        getFieldValue("taboo"),
        getFieldValue("answers"),
    ].some((value) => !value);
}

function getRuntimeApiProfile() {
    const baseUrl = getFieldValue("api-base-url");
    const apiKey = getPasswordValue("api-key");
    const model = getFieldValue("api-model");
    const profileName = getFieldValue("api-profile-name") || getFieldValue("api-profile-select");

    if (!baseUrl && !apiKey && !model) {
        return {};
    }

    return {
        profile_name: profileName,
        base_url: baseUrl,
        api_key: apiKey,
        model,
    };
}

function getPayload() {
    return {
        api_profile: getRuntimeApiProfile(),
        idea: getFieldValue("idea"),
        genre: resolveChoiceValue("genre-select", "genre-custom"),
        fanqie_track: getFieldValue("fanqie-track"),
        readership: getFieldValue("readership"),
        target_length: resolveChoiceValue("target-length-select", "target-length-custom"),
        chapter_count: getFieldValue("chapter-count"),
        hook_core: getFieldValue("hook-core"),
        tone: getFieldValue("tone"),
        taboo: getFieldValue("taboo"),
        answers: getFieldValue("answers"),
        story_bible: getFieldValue("story-bible"),
        character_bible: getFieldValue("character-bible"),
        foreshadow_table: getFieldValue("foreshadow-table"),
        outline: getFieldValue("outline-output"),
        anti_ai_guard: getFieldValue("anti-ai-guard"),
        chapter_beat: getFieldValue("chapter-beat"),
        previous_summary: getFieldValue("previous-summary"),
        chapter_word_count: getFieldValue("chapter-word-count"),
        draft: getFieldValue("chapter-draft"),
        plot_memory: getFieldValue("plot-memory"),
        foreshadow_memory: getFieldValue("foreshadow-memory"),
        chapter_memory: getFieldValue("chapter-memory"),
        continuity_notes: getFieldValue("continuity-notes"),
        chapter_archive: getFieldValue("chapter-archive"),
    };
}

function saveState() {
    const state = {};
    fieldIds.forEach((id) => {
        const field = byId(id);
        if (field) {
            state[id] = field.value;
        }
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
    const raw = LEGACY_STORAGE_KEYS
        .map((key) => localStorage.getItem(key))
        .find((value) => value);

    if (!raw) {
        return false;
    }

    try {
        const state = JSON.parse(raw);
        fieldIds.forEach((id) => {
            const field = byId(id);
            if (field && typeof state[id] === "string") {
                field.value = state[id];
            }
        });
        return true;
    } catch (error) {
        console.error("load state failed", error);
        return false;
    }
}

function setStatus(message, mode = "done") {
    const bar = document.querySelector(".status-bar");
    const text = byId("status-text");
    bar.classList.remove("is-error", "is-working", "is-done");
    if (mode === "error") {
        bar.classList.add("is-error");
    } else if (mode === "working") {
        bar.classList.add("is-working");
    } else {
        bar.classList.add("is-done");
    }
    text.textContent = message;
}

async function readResponseText(response, onChunk) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) {
            break;
        }
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        if (onChunk) {
            onChunk(chunk, buffer);
        }
    }

    return buffer;
}

async function requestPlainText({ endpoint, payload, onChunk }) {
    const response = await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "请求失败");
    }

    return readResponseText(response, onChunk);
}

async function streamIntoTarget({ endpoint, targetId, payload, preserveExisting = false }) {
    const target = byId(targetId);
    if (!preserveExisting) {
        target.value = "";
    }

    const raw = await requestPlainText({
        endpoint,
        payload,
        onChunk: (chunk) => {
            target.value += chunk;
            target.scrollTop = target.scrollHeight;
        },
    });

    saveState();
    return raw;
}

async function streamRequest({ endpoint, targetId, payload, button, doneMessage, preserveExisting = false }) {
    const target = byId(targetId);
    if (!preserveExisting) {
        target.value = "";
    }
    saveState();
    button.disabled = true;
    setStatus("正在生成，请稍等。", "working");

    try {
        await requestPlainText({
            endpoint,
            payload,
            onChunk: (chunk) => {
                target.value += chunk;
                target.scrollTop = target.scrollHeight;
            },
        });

        saveState();
        setStatus(doneMessage, "done");
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
    } finally {
        button.disabled = false;
    }
}

function parseSections(raw) {
    const regex = /^###([A-Z_]+)\s*$/gm;
    const matches = [...raw.matchAll(regex)];
    if (!matches.length) {
        return {};
    }

    const sections = {};
    matches.forEach((match, index) => {
        const key = match[1];
        const start = match.index + match[0].length;
        const end = index + 1 < matches.length ? matches[index + 1].index : raw.length;
        sections[key] = raw.slice(start, end).trim();
    });
    return sections;
}

function applySections(sectionMap, sections) {
    Object.entries(sectionMap).forEach(([sectionName, target]) => {
        if (!(sectionName in sections)) {
            return;
        }
        const value = sections[sectionName];
        if (typeof target === "function") {
            target(value, sections);
            return;
        }
        byId(target).value = value;
    });
}

async function fetchSectioned(endpoint, payload) {
    const raw = await requestPlainText({ endpoint, payload });
    const sections = parseSections(raw);
    if (!Object.keys(sections).length) {
        throw new Error("模型没有按预期格式返回结果，请重试一次。\n\n" + raw.slice(0, 300));
    }
    return sections;
}

async function runButtonTask(buttonId, task) {
    const button = byId(buttonId);
    button.disabled = true;

    try {
        await task(button);
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
    } finally {
        button.disabled = false;
    }
}

async function ensureAutofillSeedReady() {
    if (!hasFieldValue("idea")) {
        throw new Error("请先输入你的核心想法。");
    }
    if (!needsAutofillSeed()) {
        return false;
    }

    setStatus("我先帮你把空白项补齐。", "working");
    const sections = await fetchSectioned("/api/novel/autofill", getPayload());
    applyAutofillSections(sections, { force: false });
    saveState();
    return true;
}

async function ensureStoryBibleReady() {
    if (hasFieldValue("story-bible")) {
        return false;
    }

    await ensureAutofillSeedReady();
    setStatus("缺少故事圣经，我先帮你整理一版。", "working");
    await streamIntoTarget({ endpoint: "/api/novel/story-bible", targetId: "story-bible", payload: getPayload() });
    return true;
}

async function ensureCharacterBibleReady() {
    if (hasFieldValue("character-bible") && !isCharacterBibleDraftOnly()) {
        return false;
    }

    await ensureStoryBibleReady();
    const preserveExisting = hasFieldValue("character-bible");
    if (preserveExisting) {
        prepareCharacterBibleForExpansion();
    }
    setStatus("缺少人物卡，我先帮你补一版。", "working");
    await streamIntoTarget({
        endpoint: "/api/novel/characters",
        targetId: "character-bible",
        payload: getPayload(),
        preserveExisting,
    });
    return true;
}

async function ensureOutlineReady() {
    if (hasFieldValue("outline-output")) {
        return false;
    }

    await ensureStoryBibleReady();
    setStatus("缺少大纲，我先帮你补一版。", "working");
    await streamIntoTarget({ endpoint: "/api/novel/outline", targetId: "outline-output", payload: getPayload() });
    prefillFirstChapterBeatFromOutline({ overwrite: false });
    return true;
}

async function ensureForeshadowReady() {
    if (hasFieldValue("foreshadow-table")) {
        return false;
    }

    await ensureCharacterBibleReady();
    await ensureOutlineReady();
    setStatus("缺少伏笔表，我先帮你整理。", "working");
    await streamIntoTarget({ endpoint: "/api/novel/foreshadow", targetId: "foreshadow-table", payload: getPayload() });
    return true;
}

async function ensureChapterBeatReady() {
    if (hasFieldValue("chapter-beat")) {
        return false;
    }

    await ensureOutlineReady();
    const filled = prefillFirstChapterBeatFromOutline({ overwrite: false });
    if (!filled) {
        throw new Error("大纲里还没有明确的章节卡，请先检查大纲内容。");
    }
    return true;
}

async function streamSectionedRequest({ endpoint, payload, button, doneMessage, sectionMap, beforeRequest }) {
    if (beforeRequest) {
        const shouldContinue = beforeRequest();
        if (!shouldContinue) {
            return;
        }
    }

    button.disabled = true;
    setStatus("正在生成，请稍等。", "working");

    try {
        const sections = await fetchSectioned(endpoint, payload);
        applySections(sectionMap, sections);
        saveState();
        setStatus(doneMessage, "done");
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
    } finally {
        button.disabled = false;
    }
}

function copyTarget(targetId) {
    const text = byId(targetId).value;
    if (!text.trim()) {
        setStatus("这里还没有可复制的内容。", "error");
        return;
    }

    navigator.clipboard.writeText(text).then(() => {
        setStatus("已复制到剪贴板。", "done");
    }).catch(() => {
        setStatus("复制失败，请手动复制。", "error");
    });
}

function extractFirstChapterBeat(outlineText) {
    const normalized = (outlineText || "").replace(/\r\n/g, "\n").trim();
    if (!normalized) {
        return "";
    }

    const headingRegex = /^(?:#{1,6}\s*)?第[^\n]{0,30}章[^\n]*$/gm;
    const matches = [...normalized.matchAll(headingRegex)];
    if (!matches.length) {
        return "";
    }

    const start = matches[0].index;
    const end = matches[1] ? matches[1].index : normalized.length;
    return normalized.slice(start, end).trim();
}

function prefillFirstChapterBeatFromOutline({ overwrite = false } = {}) {
    const target = byId("chapter-beat");
    if (!overwrite && target.value.trim()) {
        return false;
    }

    const extracted = extractFirstChapterBeat(byId("outline-output").value);
    if (!extracted) {
        return false;
    }

    target.value = extracted;
    saveState();
    return true;
}

function fillBeatFromOutlineSelection() {
    const outline = byId("outline-output");
    const selected = outline.value.slice(outline.selectionStart, outline.selectionEnd).trim();
    if (!selected) {
        if (prefillFirstChapterBeatFromOutline({ overwrite: true })) {
            setStatus("已自动把第一章章节卡带入写作区。", "done");
            return;
        }
        setStatus("先在大纲里选中一段章节卡，再点这个按钮。", "error");
        return;
    }
    byId("chapter-beat").value = selected;
    saveState();
    setStatus("已把选中的大纲内容带入章节卡。", "done");
}

function buildArchiveEntry() {
    const beat = getFieldValue("chapter-beat");
    const draft = getFieldValue("chapter-draft");
    if (!beat && !draft) {
        return "";
    }

    const heading = beat.split("\n")[0].trim() || `片段 ${new Date().toLocaleString()}`;
    return [
        `===== ${heading} =====`,
        "[章节卡]",
        beat || "无章节卡",
        "",
        "[正文]",
        draft || "无正文",
    ].join("\n");
}

function appendCurrentToArchive(options = {}) {
    const { silent = false } = options;
    const entry = buildArchiveEntry();
    if (!entry) {
        if (!silent) {
            setStatus("当前章节卡和正文都还是空的，没法加入连载档案。", "error");
        }
        return false;
    }

    const archive = byId("chapter-archive");
    const normalizedArchive = archive.value.trim();
    if (normalizedArchive.includes(entry.trim())) {
        if (!silent) {
            setStatus("当前章节已经在连载档案里了。", "done");
        }
        return true;
    }

    archive.value = normalizedArchive ? `${normalizedArchive}\n\n${entry}` : entry;
    saveState();
    if (!silent) {
        setStatus("当前章节已加入连载档案。", "done");
    }
    return true;
}

function loadApiProfiles() {
    const raw = localStorage.getItem(API_PROFILES_KEY);
    if (!raw) {
        return [];
    }

    try {
        const profiles = JSON.parse(raw);
        if (!Array.isArray(profiles)) {
            return [];
        }
        return profiles.filter((profile) => profile && typeof profile.id === "string");
    } catch (error) {
        console.error("load api profiles failed", error);
        return [];
    }
}

function saveApiProfiles() {
    localStorage.setItem(API_PROFILES_KEY, JSON.stringify(apiProfiles));
}

function renderApiProfileOptions(selectedId = DEFAULT_API_PROFILE_ID) {
    const select = byId("api-profile-select");
    const availableIds = new Set([DEFAULT_API_PROFILE_ID, ...apiProfiles.map((profile) => profile.id)]);
    select.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = DEFAULT_API_PROFILE_ID;
    defaultOption.textContent = "环境默认";
    select.append(defaultOption);

    apiProfiles.forEach((profile) => {
        const option = document.createElement("option");
        option.value = profile.id;
        option.textContent = profile.name;
        select.append(option);
    });

    select.value = availableIds.has(selectedId) ? selectedId : DEFAULT_API_PROFILE_ID;
}

function findApiProfile(profileId) {
    return apiProfiles.find((profile) => profile.id === profileId) || null;
}

function populateApiProfileForm(profileId) {
    if (profileId === DEFAULT_API_PROFILE_ID) {
        setFieldValue("api-profile-name", "");
        setFieldValue("api-base-url", "");
        setFieldValue("api-key", "");
        setFieldValue("api-model", "");
        return;
    }

    const profile = findApiProfile(profileId);
    if (!profile) {
        return;
    }

    setFieldValue("api-profile-name", profile.name || "");
    setFieldValue("api-base-url", profile.base_url || "");
    setFieldValue("api-key", profile.api_key || "");
    setFieldValue("api-model", profile.model || "");
}

function collectApiProfileForm() {
    return {
        name: getFieldValue("api-profile-name") || `API 配置 ${apiProfiles.length + 1}`,
        base_url: getFieldValue("api-base-url"),
        api_key: getPasswordValue("api-key"),
        model: getFieldValue("api-model"),
    };
}

function hasAnyApiSetting(profile) {
    return Boolean(profile.base_url || profile.api_key || profile.model);
}

function handleApiProfileSwitch({ silent = false } = {}) {
    const profileId = byId("api-profile-select").value || DEFAULT_API_PROFILE_ID;
    populateApiProfileForm(profileId);
    saveState();
    if (!silent) {
        const profile = profileId === DEFAULT_API_PROFILE_ID ? "环境默认" : (findApiProfile(profileId)?.name || "自定义配置");
        setStatus(`已切换到 API 配置：${profile}。`, "done");
    }
}

function createNewApiProfileDraft() {
    renderApiProfileOptions(DEFAULT_API_PROFILE_ID);
    byId("api-profile-select").value = DEFAULT_API_PROFILE_ID;
    populateApiProfileForm(DEFAULT_API_PROFILE_ID);
    saveState();
    setStatus("已清空 API 表单。填好后点“保存配置”就能加入切换菜单。", "done");
}

function saveCurrentApiProfile() {
    const draft = collectApiProfileForm();
    if (!hasAnyApiSetting(draft)) {
        setStatus("当前 API 表单还是空的。你可以直接使用环境默认，或者填好后再保存。", "error");
        return;
    }

    const selectedId = byId("api-profile-select").value || DEFAULT_API_PROFILE_ID;
    let nextId = selectedId;

    if (selectedId === DEFAULT_API_PROFILE_ID || !findApiProfile(selectedId)) {
        nextId = `api_${Date.now()}`;
        apiProfiles.unshift({
            id: nextId,
            name: draft.name,
            base_url: draft.base_url,
            api_key: draft.api_key,
            model: draft.model,
        });
    } else {
        apiProfiles = apiProfiles.map((profile) => (
            profile.id === selectedId
                ? {
                    ...profile,
                    name: draft.name,
                    base_url: draft.base_url,
                    api_key: draft.api_key,
                    model: draft.model,
                }
                : profile
        ));
    }

    saveApiProfiles();
    renderApiProfileOptions(nextId);
    byId("api-profile-select").value = nextId;
    populateApiProfileForm(nextId);
    saveState();
    setStatus(`API 配置“${draft.name}”已保存。后面可以直接切换使用。`, "done");
}

function deleteCurrentApiProfile() {
    const selectedId = byId("api-profile-select").value || DEFAULT_API_PROFILE_ID;
    if (selectedId === DEFAULT_API_PROFILE_ID) {
        setStatus("环境默认不能删除。要删的是你自己保存的配置。", "error");
        return;
    }

    const profile = findApiProfile(selectedId);
    apiProfiles = apiProfiles.filter((item) => item.id !== selectedId);
    saveApiProfiles();
    renderApiProfileOptions(DEFAULT_API_PROFILE_ID);
    byId("api-profile-select").value = DEFAULT_API_PROFILE_ID;
    populateApiProfileForm(DEFAULT_API_PROFILE_ID);
    saveState();
    setStatus(`API 配置“${profile?.name || "未命名配置"}”已删除。`, "done");
}

function bindPersistence() {
    fieldIds.forEach((id) => {
        const field = byId(id);
        if (!field) {
            return;
        }
        field.addEventListener("input", saveState);
        field.addEventListener("change", saveState);
    });
}

function applyPreset() {
    const presetId = getFieldValue("preset-select");
    if (!presetId) {
        setStatus("先选一个预设模板，再应用。", "error");
        return;
    }

    const preset = presetDefinitions[presetId];
    setChoiceValue("genre-select", "genre-custom", preset.genre);
    setFieldValue("fanqie-track", preset.fanqie_track);
    setFieldValue("readership", preset.readership);
    setChoiceValue("target-length-select", "target-length-custom", preset.target_length);
    setFieldValue("chapter-count", preset.chapter_count);
    setFieldValue("tone", preset.tone);
    setFieldValue("taboo", preset.taboo);
    setFieldValue("chapter-word-count", preset.chapter_word_count);

    saveState();
    setStatus("预设已应用。现在可以直接点“一键懒人起书”，或再把核心想法和钩子补尖一点。", "done");
}

function bindChoiceFields() {
    [["genre-select", "genre-custom"], ["target-length-select", "target-length-custom"]].forEach(([selectId, customId]) => {
        const select = byId(selectId);
        select.addEventListener("change", () => {
            syncChoiceField(selectId, customId);
            saveState();
        });
        syncChoiceField(selectId, customId);
    });
}

async function runSmartAutofill() {
    const button = byId("smart-autofill");
    button.disabled = true;
    setStatus("正在智能补全空白项。", "working");

    try {
        const sections = await fetchSectioned("/api/novel/autofill", getPayload());
        applyAutofillSections(sections, { force: false });
        saveState();
        setStatus("已经帮你把空白项补了一轮。还不想细改的话，可以直接点“一键懒人起书”。", "done");
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
    } finally {
        button.disabled = false;
    }
}

async function refreshMemoryBank(options = {}) {
    const { button = null, doneMessage = "记忆库已经刷新。" } = options;
    if (button) {
        button.disabled = true;
    }

    setStatus("正在刷新记忆库，请稍等。", "working");

    try {
        const sections = await fetchSectioned("/api/novel/memory", getPayload());
        applySections(memorySectionMap, sections);
        saveState();
        setStatus(doneMessage, "done");
        return sections;
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
        throw error;
    } finally {
        if (button) {
            button.disabled = false;
        }
    }
}

async function runLazyStartWorkflow() {
    const button = byId("lazy-start");
    const autofillButton = byId("smart-autofill");
    button.disabled = true;
    autofillButton.disabled = true;

    try {
        setStatus("正在补全基础设定。", "working");
        const autofillSections = await fetchSectioned("/api/novel/autofill", getPayload());
        applyAutofillSections(autofillSections, { force: false });
        saveState();

        setStatus("正在整理故事圣经。", "working");
        await streamIntoTarget({ endpoint: "/api/novel/story-bible", targetId: "story-bible", payload: getPayload() });

        setStatus("正在生成人物卡。", "working");
        const preserveCharacters = hasManualCharacterDrafts();
        if (preserveCharacters) {
            prepareCharacterBibleForExpansion();
        }
        await streamIntoTarget({
            endpoint: "/api/novel/characters",
            targetId: "character-bible",
            payload: getPayload(),
            preserveExisting: preserveCharacters,
        });

        setStatus("正在生成可写大纲。", "working");
        await streamIntoTarget({ endpoint: "/api/novel/outline", targetId: "outline-output", payload: getPayload() });
        prefillFirstChapterBeatFromOutline({ overwrite: false });

        setStatus("正在整理伏笔表。", "working");
        await streamIntoTarget({ endpoint: "/api/novel/foreshadow", targetId: "foreshadow-table", payload: getPayload() });

        await refreshMemoryBank({ doneMessage: "懒人起书已完成：大纲、人物、伏笔和记忆库都准备好了。" });
    } catch (error) {
        console.error(error);
        setStatus(error.message || "请求失败。", "error");
    } finally {
        button.disabled = false;
        autofillButton.disabled = false;
    }
}

function bindButtons() {
    byId("smart-autofill").addEventListener("click", runSmartAutofill);
    byId("lazy-start").addEventListener("click", runLazyStartWorkflow);

    byId("generate-questions").addEventListener("click", () => {
        streamRequest({
            endpoint: "/api/novel/questions",
            targetId: "questions-output",
            payload: getPayload(),
            button: byId("generate-questions"),
            doneMessage: "关键追问已经生成，先把赛道、钩子和主角代价补齐会更稳。",
        });
    });

    byId("generate-story-bible").addEventListener("click", () => {
        runButtonTask("generate-story-bible", async () => {
            await ensureAutofillSeedReady();
            setStatus("正在整理故事圣经。", "working");
            await streamIntoTarget({ endpoint: "/api/novel/story-bible", targetId: "story-bible", payload: getPayload() });
            setStatus("故事圣经已经整理好了，接下来可以压成更有追更力的大纲。", "done");
        });
    });

    byId("generate-characters").addEventListener("click", () => {
        runButtonTask("generate-characters", async () => {
            await ensureStoryBibleReady();
            const preserveExisting = hasManualCharacterDrafts();
            if (preserveExisting) {
                prepareCharacterBibleForExpansion();
            }
            setStatus("正在生成人物卡。", "working");
            await streamIntoTarget({
                endpoint: "/api/novel/characters",
                targetId: "character-bible",
                payload: getPayload(),
                preserveExisting,
            });
            setStatus("人物卡已经生成，接下来可以整理伏笔表。", "done");
        });
    });

    byId("generate-foreshadow").addEventListener("click", () => {
        runButtonTask("generate-foreshadow", async () => {
            await ensureCharacterBibleReady();
            await ensureOutlineReady();
            setStatus("正在整理伏笔表。", "working");
            await streamIntoTarget({ endpoint: "/api/novel/foreshadow", targetId: "foreshadow-table", payload: getPayload() });
            setStatus("伏笔表已经整理好，后面写正文时会更稳。", "done");
        });
    });

    byId("generate-outline").addEventListener("click", () => {
        runButtonTask("generate-outline", async () => {
            await ensureStoryBibleReady();
            setStatus("正在生成可写大纲。", "working");
            await streamIntoTarget({ endpoint: "/api/novel/outline", targetId: "outline-output", payload: getPayload() });
            prefillFirstChapterBeatFromOutline({ overwrite: false });
            setStatus("大纲已经生成。可以直接把第一章带进写作区开写。", "done");
        });
    });

    byId("generate-chapter").addEventListener("click", () => {
        runButtonTask("generate-chapter", async () => {
            await ensureForeshadowReady();
            await ensureChapterBeatReady();
            setStatus("正在按章节卡写正文。", "working");
            await streamIntoTarget({ endpoint: "/api/novel/chapter", targetId: "chapter-draft", payload: getPayload() });
            setStatus("正文已经生成。写完这章后点“刷新记忆库”，后续续写会更稳。", "done");
        });
    });

    byId("polish-chapter").addEventListener("click", () => {
        streamRequest({
            endpoint: "/api/novel/polish",
            targetId: "chapter-draft",
            payload: getPayload(),
            button: byId("polish-chapter"),
            doneMessage: "已经按当前护栏做了去 AI 味改稿。",
        });
    });

    byId("refresh-memory").addEventListener("click", () => {
        refreshMemoryBank({
            button: byId("refresh-memory"),
            doneMessage: "记忆库已经刷新，关键剧情、伏笔和连续性都同步好了。",
        }).catch(() => {
            // setStatus has already been handled inside refreshMemoryBank.
        });
    });

    byId("continue-next-chapter").addEventListener("click", () => {
        runButtonTask("continue-next-chapter", async () => {
            await ensureForeshadowReady();

            if (!hasFieldValue("chapter-beat") && !hasFieldValue("chapter-draft")) {
                await ensureChapterBeatReady();
                throw new Error("我已经先把第一章章节卡带进来了。当前正文还是空的，先点“按章节卡写正文”更合适。");
            }

            const shouldContinue = appendCurrentToArchive({ silent: true });
            if (!shouldContinue) {
                throw new Error("当前章节卡和正文都还是空的，先生成一章正文再续写下一章。");
            }

            setStatus("正在自动续写下一章。", "working");
            const sections = await fetchSectioned("/api/novel/continue", getPayload());
            applySections({
                NEXT_BEAT: "chapter-beat",
                NEXT_DRAFT: "chapter-draft",
                UPDATED_PLOT_MEMORY: "plot-memory",
                UPDATED_FORESHADOW_MEMORY: "foreshadow-memory",
                UPDATED_CONTINUITY_MEMORY: "chapter-memory",
                NEXT_PREVIOUS_SUMMARY: "previous-summary",
                MEMORY_ALERTS: "continuity-notes",
            }, sections);
            saveState();
            setStatus("下一章已经续出来了，写作区和记忆库都已同步到最新状态。", "done");
        });
    });

    byId("append-current-to-archive").addEventListener("click", () => appendCurrentToArchive());
    byId("random-character").addEventListener("click", fillRandomCharacterDraft);
    byId("append-character-card").addEventListener("click", appendCharacterDraftToBible);
    byId("apply-preset").addEventListener("click", applyPreset);
    byId("new-api-profile").addEventListener("click", createNewApiProfileDraft);
    byId("save-api-profile").addEventListener("click", saveCurrentApiProfile);
    byId("delete-api-profile").addEventListener("click", deleteCurrentApiProfile);
    byId("api-profile-select").addEventListener("change", () => handleApiProfileSwitch());

    byId("batch-polish-archive").addEventListener("click", () => {
        streamRequest({
            endpoint: "/api/novel/batch-polish",
            targetId: "batch-polish-output",
            payload: getPayload(),
            button: byId("batch-polish-archive"),
            doneMessage: "整章统稿已经完成，可以对照连载档案检查后使用。",
        });
    });

    byId("fill-from-outline").addEventListener("click", fillBeatFromOutlineSelection);

    document.querySelectorAll("[data-copy-target]").forEach((button) => {
        button.addEventListener("click", () => copyTarget(button.dataset.copyTarget));
    });
}

function initializeApiProfiles() {
    apiProfiles = loadApiProfiles();
    renderApiProfileOptions(DEFAULT_API_PROFILE_ID);
}

function initializeState() {
    const hasSavedState = loadState();
    if (!hasSavedState) {
        populateApiProfileForm(DEFAULT_API_PROFILE_ID);
    }

    renderApiProfileOptions(getFieldValue("api-profile-select") || DEFAULT_API_PROFILE_ID);

    if (!hasSavedState) {
        byId("api-profile-select").value = DEFAULT_API_PROFILE_ID;
        populateApiProfileForm(DEFAULT_API_PROFILE_ID);
    }

    bindChoiceFields();
}

initializeApiProfiles();
initializeState();
bindPersistence();
bindButtons();
setStatus("准备好了。只写一个核心想法也行，先点“智能补全空白项”或直接“一键懒人起书”；后续缺前置资料时也会尽量自动补齐。", "done");
