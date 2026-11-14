# 题库一览 — 小电商 AI 客服检索实验（v1.0）

> 语料冻结在虚构店 Momo Ceramics 的 5 个页面（index / product / shipping / returns / faq）。每题的期望来源和期望事实都逐字核对过原文；机器可读版是同目录 `questions.json`，实验规则在 `README.md`。


## A · 直问单跳（16）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| A01 | What is your return policy? | 答 | returns |
| A02 | How long does delivery take within Japan? | 答 | shipping |
| A03 | How long does shipping take to the United States? | 答 | shipping |
| A04 | Who pays for return shipping on a regular return? | 答 | returns |
| A05 | What should I do if my mug arrives damaged? | 答 | returns |
| A06 | How much does the Aurora Mug cost? | 答 | product |
| A07 | What is the capacity of the Aurora Mug? | 答 | product |
| A08 | Is the Aurora Mug microwave safe? | 答 | product |
| A09 | How should I wash the Aurora Mug? | 答 | product, faq |
| A10 | Do you offer gift wrapping and does it cost anything? | 答 | faq |
| A11 | Do you accept custom orders? | 答 | faq |
| A12 | How can I contact you and how soon will you reply? | 答 | faq |
| A13 | How much is shipping, and when is it free? | 答 | shipping |
| A14 | How long does it take to process an order before it ships? | 答 | shipping |
| A15 | Which countries do you ship to? | 答 | shipping |
| A16 | How do I get a tracking number for my order? | 答 | shipping |

## B · 改写 / 口语 / 同义词（10）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| B01 | If the cup doesn't suit me, can I send it back and get my money back? | 答 | returns |
| B02 | How soon will my order land in California? | 答 | shipping |
| B03 | Is it okay to zap it in the microwave? | 答 | product |
| B04 | Will I be charged for postage if my basket totals 90 dollars? | 答 | shipping |
| B05 | The cup showed up cracked — what should I do? | 答 | returns |
| B06 | Can you make me a bigger one with my name on it? | 答 | faq |
| B07 | How much liquid does it hold? | 答 | product |
| B08 | Who do I write to for help, and how long until they get back to me? | 答 | faq |
| B09 | Will putting it in the dishwasher ruin the finish? | 答 | product, faq |
| B10 | Do I have to pay to mail it back if I simply changed my mind? | 答 | returns |

## C · 多跳跨页 / 跨块（10）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| C01 | I'm buying 3 Aurora Mugs as gifts — will shipping be free, and can you wrap them? | 答 | product, shipping, faq |
| C02 | Counting everything, how long from placing an order until it reaches me in the US? | 答 | shipping |
| C03 | If I buy just one Aurora Mug, what is my total including shipping? | 答 | product, shipping |
| C04 | I live in Canada — can I get a mug gift wrapped, and how long will delivery take? | 答 | shipping, faq |
| C05 | Can I order a custom-coloured mug and have it shipped to Australia? | 答 | faq, shipping |
| C06 | My mug arrived damaged and I'd rather have my money back than a new one — is that allowed? | 答 | returns |
| C07 | I need a mug delivered in Tokyo within 3 days — can you guarantee that? | 答 | shipping |
| C08 | I'm buying 2 Aurora Mugs — do I get free shipping? | 答 | product, shipping |
| C09 | Will a set of 4 Aurora Mugs all be exactly the same height? | 答 | product, index |
| C10 | My mug arrived broken — do I have to pay the return costs, and what are my options? | 答 | returns |

## D · 近似陷阱 — 应兜底（8）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| D01 | Do you offer express or next-day shipping? | 兜底 | shipping |
| D02 | How heavy is the Aurora Mug in grams? | 兜底 | product |
| D03 | Is the glaze certified lead-free and food safe? | 兜底 | product |
| D04 | Do you offer a warranty if the mug cracks after a year? | 兜底 | returns |
| D05 | Can I change the delivery address after placing an order? | 兜底 | shipping |
| D06 | What discount do I get if I buy 10 or more mugs for my office? | 兜底 | product |
| D07 | Can I buy a gift card to give someone instead of a mug? | 兜底 | faq |
| D08 | Can I visit your Kyoto studio in person, and what are its opening hours? | 兜底 | index |

## E · 无答案 — 应兜底（6）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| E01 | Can I pay with Bitcoin? | 兜底 | — |
| E02 | Do you have a loyalty points program? | 兜底 | — |
| E03 | Do you sell plates or tea sets as well? | 兜底 | — |
| E04 | Do you run a monthly subscription for a new mug every month? | 兜底 | — |
| E05 | Are you hiring staff for the studio? | 兜底 | — |
| E06 | What is the weather like in Kyoto today? | 兜底 | — |

## F · 人工边界 — 应转人工（5）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| F01 | Please cancel my order number 1042 and refund me right now. | 转人工 | returns |
| F02 | Where is my order number 1042 right now? Track it for me. | 转人工 | shipping |
| F03 | Change the shipping address on the order I placed yesterday. | 转人工 | shipping |
| F04 | My mug arrived damaged — please start my replacement shipment today. | 转人工 | returns |
| F05 | Apply the discount code MOMO10 to my last order and charge my card again. | 转人工 | — |

## G · 中文探索组 — 单独计分（5）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| G01 | 你们的退货政策是多久内可以退？ | 答 | returns |
| G02 | 寄到美国大概需要多长时间？ | 答 | shipping |
| G03 | 这个杯子可以用洗碗机清洗吗？ | 答 | product, faq |
| G04 | 你们提供礼品包装吗？需要额外收费吗？ | 答 | faq |
| G05 | 可以定做一个刻着我名字的杯子吗？ | 答 | faq |

---

# v2 新增题（第二轮校准 · held-out 集，2026-11-14）

> 依据 `prereg-round2.md` 在预注册之后编写，语料仍是同一批冻结的 5 页；机器可读版在 `questions-v2-additions.json`，合并版 `questions-v2.json`。期望事实逐字核对过 onboard 块原文，D/E 组的缺失点已逐项检索全部 5 页确认不存在。与 v1 任一题无重复或轻微改写（写后跑过去重叠筛查）。

## A2 · 直问单跳（8）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2A01 | Within how many days of delivery can I return an unused item? | 答 | returns |
| V2A02 | How quickly are refunds issued after you receive a returned item, and where does the money go? | 答 | returns |
| V2A03 | What material is the Aurora Mug made of, and what colour is its glaze? | 答 | product |
| V2A04 | My order comes to 50 dollars — how much will I pay for shipping? | 答 | shipping |
| V2A05 | Do you ship to Canada, and how long does delivery there take? | 答 | shipping |
| V2A06 | What condition must returned items be in to qualify for a refund? | 答 | returns |
| V2A07 | How should I wash the mug to keep the glaze looking its best for longer? | 答 | faq |
| V2A08 | What is your best-selling product? | 答 | index |

## B2 · 改写 / 口语 / 同义词（8）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2B01 | What's the longest I might wait before my parcel is even on its way? | 答 | shipping |
| V2B02 | I'm in France — roughly how long would a mug take to reach me? | 答 | shipping |
| V2B03 | Does the cup have a glossy finish? | 答 | product |
| V2B04 | I've poured coffee in it once and now I don't want it — can I still send it back for a refund? | 答 | returns |
| V2B05 | Once you've got my sent-back mug in your hands, how long till the money is back with me? | 答 | returns |
| V2B06 | Can I slip a personal message into the box when it's a present for a friend? | 答 | faq |
| V2B07 | Are these things actually made by hand, or are they factory-produced? | 答 | product, index |
| V2B08 | If I email you today, when should I expect a reply? | 答 | faq |

## C2 · 多跳跨页 / 跨块（8）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2C01 | I want two mugs sent to Berlin as gifts — what's the total with shipping, and can they be wrapped? | 答 | product, shipping, faq |
| V2C02 | Counting from the day I place my order, what's the longest a delivery to the European Union could take overall? | 答 | shipping |
| V2C03 | My mug arrived damaged, and I'm worried sending it back will cost me — who covers the costs, and what can I get? | 答 | returns |
| V2C04 | Can I get the mug in green instead — and if not, what colour does it actually come in? | 答 | faq, product |
| V2C05 | If I buy one mug for a friend in Canada, what's my total and how long until it gets to them? | 答 | product, shipping |
| V2C06 | If I buy two mugs, will they look and measure exactly identical? | 答 | index, product |
| V2C07 | I ordered the wrong thing and it already arrived — walk me through what sending it back involves and who pays what. | 答 | returns |
| V2C08 | Is the mug safe for heating up soup, and how am I supposed to clean it afterwards? | 答 | product, faq |

## D2 · 近似陷阱 — 应兜底（10）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2D01 | What is the diameter of the Aurora Mug in centimetres? | 兜底 | product |
| V2D02 | Can I pay in instalments, or with a buy-now-pay-later service? | 兜底 | returns |
| V2D03 | Is gift wrapping still free during the holiday season, or is there an extra charge then? | 兜底 | faq |
| V2D04 | Do you sell replacement lids or other spare parts for the Aurora Mug? | 兜底 | product |
| V2D05 | What is the studio's phone number so I can call you? | 兜底 | faq |
| V2D06 | How many mugs do you produce in each batch? | 兜底 | product |
| V2D07 | Can I follow my parcel on a live map in real time? | 兜底 | shipping |
| V2D08 | Do you offer a student discount? | 兜底 | product |
| V2D09 | Can the Aurora Mug go in the oven for reheating food? | 兜底 | product |
| V2D10 | Can I exchange my mug for a different design instead of getting a refund? | 兜底 | returns |

## E2 · 无答案 — 应兜底（6）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2E01 | Do you have an iPhone or Android app for shopping? | 兜底 | — |
| V2E02 | Is PayPal accepted at checkout? | 兜底 | — |
| V2E03 | Do you sell wholesale to cafes and restaurants? | 兜底 | — |
| V2E04 | What new mug designs are you releasing next season? | 兜底 | — |
| V2E05 | Can I book a pottery workshop at your Kyoto studio? | 兜底 | — |
| V2E06 | Who won the football match last night? | 兜底 | — |

## F2 · 人工边界 — 应转人工（5）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V2F01 | Please refund my order 2077, but put the money on a different card than the one I paid with. | 转人工 | returns |
| V2F02 | My parcel has been stuck in transit for a week — check where it is and sort it out for me. | 转人工 | shipping |
| V2F03 | Please upgrade my order from one mug to two mugs before it ships. | 转人工 | shipping |
| V2F04 | The gift note on the order I just placed has the wrong name on it — fix it before the parcel goes out. | 转人工 | faq |
| V2F05 | The mug that arrived is chipped — send me a replacement today, my address is on my account. | 转人工 | returns |

---

# v3 新增题（第三轮混合检索 · held-out 集，2026-11-14）

> 依据 `prereg-round3.md` 在预注册之后编写，语料仍是同一批冻结的 5 页；机器可读版在 `questions-v3-additions.json`，合并版 `questions-v3.json`。可答题的期望事实一律用页面英文事实串（抽取式回答引用英文块），逐字核对过块原文；陷阱/无答案的缺失点已逐项检索全部 5 页确认不存在；与 v1+v2 查重通过（英文 token Jaccard 最高 0.33、CJK 4-gram 最高 0.23）。改写组的 `target_overlap` 是题面内容词与金块 token 的重合数，逐题记在机器可读版里。

## B3 · 英文改写（20，至少一半与金块零内容词重合，实测 18/20 为零）

| ID | 题目 | 期望 | 来源页 | 重合 |
|---|---|---|---|---:|
| V3B01 | How long is the wait for folks in America before their purchase shows up at the door? | 答 | shipping | 0 |
| V3B02 | At what basket total does the delivery charge disappear? | 答 | shipping | 0 |
| V3B03 | How much coffee can I fit in it before it overflows? | 答 | product | 0 |
| V3B04 | Say it turns up and I realise I don't actually want it — how long have I got to get it back to you and have my money back? | 答 | returns | 0 |
| V3B05 | Mine showed up with a crack in it — is there a deadline for sending you a picture of the damage? | 答 | returns | 0 |
| V3B06 | It's a present for my sister — will you make it look nice before posting it, and does that cost extra? | 答 | faq | 0 |
| V3B07 | Could you craft a one-off piece based on a sketch I send you? | 答 | faq | 0 |
| V3B08 | If I write to you this morning, when am I likely to hear back? | 答 | faq | 0 |
| V3B09 | Once I've placed an order, how long before it leaves your studio? | 答 | shipping | 0 |
| V3B10 | Which parts of the world can you send a parcel to? | 答 | shipping | 0 |
| V3B11 | What's the kindest way to wash it so the colour doesn't fade? | 答 | faq | 0 |
| V3B12 | If I post it back because I picked the wrong thing, who foots the bill for the postage? | 答 | returns | 0 |
| V3B13 | Once my sent-back parcel reaches you, when does the money land back in my account? | 答 | returns | 0 |
| V3B14 | Is it alright to pop this in the microwave to warm up some soup? | 答 | product | 1 |
| V3B15 | Will mine be precisely the same size as the one in the photos? | 答 | product | 0 |
| V3B16 | Once it's on its way, how will I be able to follow where it is? | 答 | shipping | 0 |
| V3B17 | What's it crafted from — porcelain or something else? | 答 | product | 0 |
| V3B18 | What colour does it come in? | 答 | product | 0 |
| V3B19 | If it turns up broken, do I get to choose between a fresh one or my money back? | 答 | returns | 0 |
| V3B20 | My friend lives in Kyoto — how quickly would a mug get to her? | 答 | shipping | 1 |

## Z3 · 中文（20：答 12 / 近似陷阱 4 / 无答案·动作边界 4）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V3Z01 | 我想把没用过的杯子退回去，能在收到货之后多少天内退？ | 答 | returns |
| V3Z02 | 如果收货地址在美国，大概要等多久才能收到？ | 答 | shipping |
| V3Z03 | 这个杯子能装多少毫升水？ | 答 | product |
| V3Z04 | 一个 Aurora 杯子卖多少钱？ | 答 | product |
| V3Z05 | 杯子可以放进微波炉里加热吗？ | 答 | product |
| V3Z06 | 买来送朋友，能帮我包得漂亮一点吗？这个服务收费吗？ | 答 | faq |
| V3Z07 | 能不能按照我的要求单独做一个特别款？ | 答 | faq |
| V3Z08 | 发邮件咨询的话，一般多久能收到回复？ | 答 | faq |
| V3Z09 | 订单满多少钱可以免运费？ | 答 | shipping |
| V3Z10 | 吃完饭直接把杯子扔进洗碗机里洗，没问题吧？ | 答 | product, faq |
| V3Z11 | 收到时杯子已经碎了，我要在几天内拍照告诉你们？ | 答 | returns |
| V3Z12 | 这些杯子是纯手工制作的吗？ | 答 | index, product |
| V3Z13 | 杯子用了一年开裂了，在保修期内吗？能免费换吗？ | 兜底（陷阱） | returns |
| V3Z14 | 这个杯子本身有多重？多少克？ | 兜底（陷阱） | product |
| V3Z15 | 我急用，明天能送到吗？有没有次日达？ | 兜底（陷阱） | shipping |
| V3Z16 | 能不能单独买一张你们家的礼品卡送人？ | 兜底（陷阱） | faq |
| V3Z17 | 结账的时候可以用支付宝付款吗？ | 兜底（无答案） | — |
| V3Z18 | 在你们店下单能攒积分吗？积分能换优惠吗？ | 兜底（无答案） | — |
| V3Z19 | 帮我把我刚下的那笔订单取消掉，谢谢。 | 转人工 | returns |
| V3Z20 | 我的包裹现在到哪儿了？帮我查一下位置。 | 转人工 | shipping |

## J3 · 日文（10：答 6 / 近似陷阱 2 / 无答案·动作边界 2）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V3J01 | 未使用の場合、届いてから何日以内なら返品できますか？ | 答 | returns |
| V3J02 | 日本国内だと、届くまで何日くらいかかりますか？ | 答 | shipping |
| V3J03 | このマグカップはいくらですか？ | 答 | product |
| V3J04 | 電子レンジで温めても大丈夫ですか？ | 答 | product |
| V3J05 | プレゼント用にラッピングしてもらえますか？追加料金はかかりますか？ | 答 | faq |
| V3J06 | 送料が無料になるのは、合計いくら以上買ったときですか？ | 答 | shipping |
| V3J07 | 1年使ってひびが入ったら、保証で交換してもらえますか？ | 兜底（陷阱） | returns |
| V3J08 | 翌日配送はありますか？明日までに届けてほしいです。 | 兜底（陷阱） | shipping |
| V3J09 | 支払いはコンビニ払いでもできますか？ | 兜底（无答案） | — |
| V3J10 | 注文番号3311をキャンセルして、今すぐ返金してください。 | 转人工 | returns |

## T4 · 第四轮近失陷阱（20：EN 8 / ZH 7 / JA 5，陷阱加权，prereg-round4.md）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V4T01 | Can I put the Aurora Mug in the freezer to chill a drink in it? | 兜底（陷阱） | product |
| V4T02 | Do I have to pay customs duties or import taxes on an order shipped to the United States? | 兜底（陷阱） | shipping |
| V4T03 | Will I need to sign for the parcel when it is delivered? | 兜底（陷阱） | shipping |
| V4T04 | Can you print a personal message on the gift card instead of leaving it blank? | 兜底（陷阱） | faq |
| V4T05 | Is the Aurora Mug available in any other colours besides the midnight blue one? | 兜底（陷阱） | product |
| V4T06 | If I cancel my order before it ships, will I get a full refund automatically? | 兜底（陷阱） | returns |
| V4T07 | Can I pay an extra fee to have my order processed and shipped faster than usual? | 兜底（陷阱） | shipping |
| V4T08 | Do you provide a prepaid return label, or do I have to arrange the return postage myself? | 兜底（陷阱） | returns |
| V4T09 | 刚烧开的热水可以直接倒进这个杯子里吗？会不会因为温差太大裂开？ | 兜底（陷阱） | product |
| V4T10 | 包裹在运输途中丢了或者破损，你们有运输保险吗？ | 兜底（陷阱） | shipping |
| V4T11 | 能帮我把两个杯子分开寄到两个不同的地址吗？ | 兜底（陷阱） | shipping |
| V4T12 | 订单已经下了，我还能改一下要买的杯子数量吗？ | 兜底（陷阱） | shipping |
| V4T13 | 能指定周六或者周末送货上门吗？ | 兜底（陷阱） | shipping |
| V4T14 | 退货时需要我自己付的那部分运费，大概要多少钱？ | 兜底（陷阱） | returns |
| V4T15 | 你们用的釉料是哪个国家生产的？ | 兜底（陷阱） | product |
| V4T16 | このマグカップは冷凍庫に入れても大丈夫ですか？ | 兜底（陷阱） | product |
| V4T17 | 注文をキャンセルした場合、キャンセル料はかかりますか？ | 兜底（陷阱） | returns |
| V4T18 | マグカップを漂白剤で洗ってもいいですか？ | 兜底（陷阱） | faq |
| V4T19 | 持ち手は熱くならない作りになっていますか？熱い飲み物を入れても素手で持てますか？ | 兜底（陷阱） | product |
| V4T20 | 配達の日時指定はできますか？来週の土曜日の午前に届けてほしいのですが。 | 兜底（陷阱） | shipping |

## U4 · 第四轮无答案（8：EN 3 / ZH 3 / JA 2）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V4U01 | Can I sign up for a newsletter to hear about new mug designs when they come out? | 兜底（无答案） | — |
| V4U02 | Do you have a shop in Tokyo where I can buy a mug in person? | 兜底（无答案） | — |
| V4U03 | Are you on Instagram or other social media? I would like to follow the studio. | 兜底（无答案） | — |
| V4U04 | 在你们这里买杯子，可以开发票吗？ | 兜底（无答案） | — |
| V4U05 | 你们有微信小程序商店吗？我想在小程序里下单。 | 兜底（无答案） | — |
| V4U06 | 你们会去参加手作市集摆摊吗？想在线下看看实物。 | 兜底（无答案） | — |
| V4U07 | 支払いにPayPayは使えますか？ | 兜底（无答案） | — |
| V4U08 | 領収書を発行してもらうことはできますか？ | 兜底（无答案） | — |

## H4 · 第四轮人工边界（6：EN/ZH/JA 各 2）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V4H01 | Please hold my order and do not ship it until next Monday. | 转人工 | shipping |
| V4H02 | I placed two separate orders this morning — please combine them into one shipment and refund the extra shipping fee. | 转人工 | shipping |
| V4H03 | 帮我把订单上的收货人名字改一下，我下单的时候写错了。 | 转人工 | shipping |
| V4H04 | 帮我催一下我的订单，让仓库今天就把它发出来。 | 转人工 | shipping |
| V4H05 | 注文したマグカップの数を1つから2つに変更してください。 | 转人工 | shipping |
| V4H06 | 配送先の住所を間違えて入力したので、新しい住所に直してください。 | 转人工 | shipping |

## A4 · 第四轮可答对照（6：EN/ZH/JA 各 2，测接受线误伤）

| ID | 题目 | 期望 | 来源页 |
|---|---|---|---|
| V4A01 | How much money do I need to pay for a single Aurora Mug? | 答 | product |
| V4A02 | Once you have received my return, how long will it take for the refund to be issued? | 答 | returns |
| V4A03 | 你们的杯子可以寄到哪些国家和地区？ | 答 | shipping |
| V4A04 | 杯子送到的时候已经破损了，我应该怎么做？ | 答 | returns |
| V4A05 | 送料はいくらかかりますか？無料になる条件も教えてください。 | 答 | shipping |
| V4A06 | メールで問い合わせたら、何日くらいで返事がもらえますか？ | 答 | faq |
