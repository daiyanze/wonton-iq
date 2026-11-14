# 客服体检 — 演示脚本 + 招呼话术（中英各一版）

> 用途：给真实小店商家当场看价值，**先演示、后谈试用、最后才谈付费**。
> 状态：试水材料，未对外发送。等 Dai 提供真实店铺网址或批准后才联系任何商家。
> 产品口径（演示时不越界）：第一版只引用商家站内原文回答并附出处；答不出就记录并转人工；**不查订单、不办退款、不对接 WooCommerce / Shopify**（那是第二步）。不承诺站内没写的政策。

---

## 一、什么是「客服体检」（一句话）

输入商家自己的网址，现场抓取他站内的产品 / FAQ / 物流 / 退换页，生成：

1. **顾客最可能问的 20 个问题**（见第三节框架，按他的品类替换）
2. **逐题实测结果**：能答（带原文出处）/ 答不全 / 站内根本没写清
3. **widget 预览**：顾客实际提问时看到的样子

体检的价值不只是「能答多少」，更是**当场指出他站内没写清、顾客却一定会问的那几题**——那正是商家现在靠私信和邮件硬扛的部分。

---

## 二、演示脚本（10 分钟版，屏幕共享或当面）

### 0:00–1:00 开场：先说他的问题，不说产品

中文口播：
> 「小店客服最耗时间的，往往不是难题，是同一批问题反复回——多久发货、能不能退、怎么保养。你站上其实写了不少，只是顾客不去翻，都来问你。我花 3 分钟，用你自己的网址跑一遍，看这些问题现在能不能被自动答掉、答得对不对。你全程看着，不用装任何东西。」

要点：不提 AI 多智能，只提「少回重复消息」。

### 1:00–3:00 现场开通：让他看「≤3 分钟」这件事本身

操作：打开开通页 → 贴入他的网址 → 开始抓取。

边做边说：
> 「我只抓你公开的产品、FAQ、物流和退换页，不碰后台、不碰订单。」

报结果（照实报数，不夸大）：抓到 X 页 / X 个知识块 / 用时 X 分 X 秒。
- 若抓取不全（如某政策页没抓到）：当场承认，记下来——这本身就是体检发现，不要遮掩。

### 3:00–7:00 逐题实测：20 题里挑 6 题现场打

按这个顺序打，每题停 10 秒让他看出处：

| 顺序 | 题型 | 为什么先打这题 |
|---|---|---|
| 1 | 物流时效（如「多久能到？」） | 最高频，命中最容易建立信任 |
| 2 | 退换政策（如「不合适能退吗？」） | 最敏感，必须让他亲眼看到是**引用原文**、不是编的 |
| 3 | 产品使用 / 保养 | 展示不只会答政策题 |
| 4 | 一道站内没写清的题 | 预期落空题：系统应兜底转人工、不编造 → 引出「未答清单」 |
| 5 | 订单类题（如「我的订单到哪了？」） | 主动演示边界：第一版不查订单，直接转人工，不要等他问 |
| 6 | 他现场随口出的一题 | 把主动权给他，这是全场最有说服力的一题 |

每答对一题只说一句：
> 「这条是引用的你退换页原文，下面有出处链接，顾客能自己点开核对。」

兜底题出现时说：
> 「这题你站上没写，系统不会编，它会记进未答列表、引导顾客留联系方式转你处理。你每周看一眼这个列表，就知道 FAQ 该补哪几条。」

### 7:00–9:00 看商家视图：未答 + 转人工

打开 `/admin/<site_id>`，指给他看：未答问题列表、转人工记录。

口播：
> 「你得到的不是一个黑盒机器人，是两个东西：一个帮顾客自助查的帮助中心 / 小窗，和一份『顾客问了但你没答上』的清单。第二份清单往往比第一个更值钱。」

然后打开 widget 预览，让他在自己店页面（预览）右下角点开提问一次。

### 9:00–10:00 收尾：只提一周免费试用，不报价逼单

口播：
> 「今天只是拿你公开页面测的，不算数。要不要这样：你授权我用你真实站点跑一周，顾客问题真实进来，一周后我们一起看三个数——答对多少、兜底有没有乱编、你少回了多少条。一周后觉得没用，直接关掉，不收费。觉得有用，再谈一个月多少钱。」

- 他问价格：给档位不给死价——「试水价 $49–99 / 月，按店大小定，一周试用结束再定，现在不用决定。」
- 他问 Shopify / WooCommerce 对接：直说「第一版是独立帮助中心 + 嵌入小窗，不进你的平台后台；对接是第二步，等试用证明有人愿意用再做。」
- 他问「会不会答错惹麻烦」：直说机制——「只引用你站内原文，答不出就转人工；政策你改了，重新抓一遍就更新。最坏情况是答不出，不会是编一个政策出来。」

### 演示禁忌

- 不说「全自动客服」「替代人工」「查订单 / 办退款」——第一版做不到。
- 不用虚构同行案例、不用「已有 X 家在用」——目前只有虚构店 Momo Ceramics 烟测。
- 抓取失败、答错当场认，记进体检结论；遮掩一次，信任全没。

---

## 三、20 个问题怎么生成（按品类套框架，不编政策）

从他站内页面抽题，**问题可以预设，答案只能来自站内原文**。默认配比（共 20）：

| 类别 | 题数 | 例题模板（把〈产品〉换成他的真实商品） |
|---|---|---|
| 物流配送 | 4 | 多久发货？/ 多久能到？/ 运费多少、满多少免邮？/ 发哪些地区、能不能发海外？ |
| 退换售后 | 4 | 不合适能退吗、几天内？/ 退货运费谁出？/ 换货怎么操作？/ 退款多久到账？（站内没写 → 应兜底） |
| 产品与使用 | 4 | 〈产品〉是什么材质 / 规格？/ 怎么使用 / 保养 / 清洗？/ 有哪些颜色 / 尺寸？/ 手工品个体差异大吗？ |
| 下单与支付 | 3 | 怎么下单？/ 能用哪些支付方式？/ 能改地址 / 改订单吗？（订单类 → 转人工） |
| 定制 / 礼品 / 库存 | 3 | 能定制吗？/ 能礼品包装 / 代写贺卡吗？/ 没货了何时补、能预订吗？ |
| 联系与保障 | 2 | 怎么联系你们、多久回复？/ 产品有保修 / 质量问题怎么办？ |

生成规则：
1. 每题标注**预期出处页**（产品页 / 物流页 / 退换页 / FAQ / 站内无）。
2. 站内无出处的题不删——它们是体检的「缺口题」，专门用来测兜底、并提示商家补 FAQ。
3. 语言跟商家站点走：英文站出英文题，中文站出中文题，不混排。

Momo Ceramics 示例（虚构店，仅示意格式）：「How long does shipping take?」→ 命中物流页原文；「Can I pay with Bitcoin?」→ 站内无 → 正确兜底转人工（烟测已验证）。

---

## 四、招呼话术 · 中文版

### 4.1 首次联系（私信 / 邮件，≤150 字，不带价格、不带产品链接）

> 你好，我是 Dai，独立开发者。最近在做一个给小独立站用的客服自助工具：贴上网址就能把你站里的物流、退换、FAQ 变成顾客能自助问的帮助中心，答不了的问题会整理成清单转给你。
>
> 想免费帮你做一次「客服体检」：用你自己的网址，当场测顾客最常问的 20 个问题能答对几题、哪几题你站上还没写清。全程约 10 分钟，你看着我跑，不用装任何东西，也不用先付费。有兴趣我把体检结果发你看？

发出前检查：称呼换成店主名 / 店名；提一句他店里某个具体产品（证明不是群发）；只发一次，不连环追。

### 4.2 对方说「好，发来看看」

> 好，我需要你确认一句：可以用你的公开网址做这次演示抓取吗？只抓产品、FAQ、物流、退换这些公开页，不碰后台和订单。
>
> 跑完我发你三样：20 题逐题结果（能答的带原文出处）、站内没写清的问题清单、一个能点开试问的预览链接。你看完觉得有用，我们再聊要不要试用一周；没用就到这，不打扰。

### 4.3 对方问价格

> 试水阶段是 $49–99 / 月，看店的规模和问题量定。建议先别急着谈价：先免费试用一周，看答对率和你实际少回多少消息，再决定值不值。一周内随时关，不收费。

### 4.4 对方没回复（只跟进一次，3–5 天后）

> 上次那条补一句：体检不用你准备任何材料，我用你公开网址跑完直接把结果发你，10 分钟看完。不需要的话回个「不用」就行，我不再发了。

跟进后仍无回复 → 停，记进试水清单的「无回复」栏，不再联系。

### 4.5 对方拒绝

> 明白，谢谢你看完。如果以后重复问题多到回不过来，随时找我，我把这次的话留在这。祝生意顺利。

---

## 五、招呼话术 · 英文版

### 5.1 First contact (DM / email, no price, no product link)

> Hi, I'm Dai, an independent developer. I'm building a small support tool for independent stores: you paste your store URL and it turns your existing shipping, returns and FAQ pages into a help centre customers can ask directly. Anything it can't answer gets collected into a list for you instead of being made up.
>
> I'd like to run a free "support checkup" on your store: I'll test the 20 questions your customers most likely ask, show you which ones your site already answers (with the source quoted), and which ones aren't covered on your site at all. It takes about 10 minutes, you watch it run, nothing to install and nothing to pay. Want me to send you the results?

Before sending: use the owner's / store's name; mention one specific product from their store; send once only.

### 5.2 If they say yes

> Great — one quick confirmation first: may I crawl your public pages for this demo? Only product, FAQ, shipping and returns pages. No admin access, no order data.
>
> You'll get three things: the 20 questions with a result for each (answered ones quote your own text with a source link), a list of questions your site doesn't cover yet, and a preview link you can try yourself. If it's useful we can talk about a one-week trial; if not, that's the end of it.

### 5.3 If they ask about price

> During this test phase it's $49–99/month depending on store size and question volume. But I'd rather not start there: try it free for a week first, look at how many questions it answers correctly and how many repeat messages it saves you, then decide. You can switch it off any time during the week, no charge.

### 5.4 One follow-up only (3–5 days later, if no reply)

> Quick add to my last note: the checkup needs nothing from you — I run it on your public URL and send the results, 10 minutes to read. If it's not for you, just reply "no thanks" and I won't message again.

Still no reply → stop, log as "no reply" in the trial checklist.

### 5.5 If they decline

> Understood, thanks for reading this far. If repeat questions ever start eating your day, you know where to find me. Good luck with the store.

---

## 六、演示结束当场要落的三个数

1. 20 题：命中 ___ / 20（过关线 ≥14，见执行清单）
2. 兜底：未答题是否 100% 进未答列表、有无一条编造（有编造 = 当场判不过关）
3. 商家原话：他对「试用一周」的回答，逐字记进执行清单的付费信号判定表，不 paraphrase 成「有兴趣」。
