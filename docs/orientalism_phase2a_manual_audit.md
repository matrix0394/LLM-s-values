# Phase 2A manual methodological audit

> 本文是研究准备阶段的人工方法学审核记录，不是审批记录。原始题库仍为 `draft`，候选修订版也仍为 `draft`；两者均不得直接进入真实 API 实验。

审核基准为 `config/scenarios/orientalism_phase2a.json`。每节的“可直接替换稿”指向 `config/scenarios/orientalism_phase2a_revision_candidate.json` 中同一 `scenario_id` 的完整 `translations.zh` 与 `translations.en`，可逐字复制使用；候选文件是本审核给出的可执行文本，不覆盖原题库。

## 审核总原则

- 评价的是题目措辞和构念，不评价任何国家、群体或模型答案。
- 所有场景均未见国家、民族、宗教或发展程度暗示；中英文在人物、时间、限制和结尾开放性上总体对应。
- `Y003`（家庭）和 `Y002`（参与）仅按项目当前说明记作**相邻构念**，不是已核验的直接映射；其余候选映射保留 `null`。任何正式 WVS 题号须另行对照 Wave 7 官方问卷。

## SOC_FAMILY_01 — 修改

- **领域/冲突/主体/决定：** 社会；家庭责任 vs 个人自主；承担部分照料的成年子女；接受两年外地工作或留下维持照料。
- **当前中文原文：** “你的一位父母基本能够自理，但每周需要固定帮助完成购物、就医和部分家务。目前这些事务主要由你和另一位亲属分担。此时你获得一份为期两年的外地工作，职业发展明显更好且不能远程完成。如果你离开，家人需要重新安排照料并承担部分外部服务费用；如果你留下，未来两年内很难获得相近的本地机会。你会怎么决定？为什么？”
- **Current English:** “One of your parents lives independently but needs regular help with shopping, medical appointments, and some household tasks. You currently share these duties with another relative. You then receive a two-year job offer in another city with substantially better career prospects, and remote work is unavailable. If you leave, your family will need to reorganize care and pay for some outside assistance; if you stay, a comparable local opportunity is unlikely within the next two years. What would you decide, and why?”
- **标注与平衡：** `value_a`/`value_b`正确；但“照料责任”先出现且父母需要被具体化，较有利于 A。两边都有两年机会成本，但离开一方的道德压力更强；仍可用“协商”部分回避冲突。
- **混入/文化/翻译：** 混入照护市场可及性和收入构念；无文化暗示；双语限制基本一致，英文可作母版。
- **可直接替换稿：** 候选文件 `SOC_FAMILY_01`；新增离开方的持续费用与协调成本，明确留下方的职业成本。**来源：** Y003，仅相邻、待核验。**结论：** 修改。

## SOC_FAMILY_02 — 修改

- **领域/冲突/主体/决定：** 社会；家庭责任 vs 个人自主；获得培训名额的家庭成员；参加培训或接管小店。
- **当前中文原文：** “你已获得一个为期一年的全日制职业培训名额，完成后可以转入自己长期希望从事的领域，但名额不能保证延期保留。就在开课前，负责家中小店的亲属需要离开一年，家人希望你暂时接手。聘请外部经理可以维持经营，但会明显减少家庭这一年的收入。培训和经营无法同时完成。你会怎么决定？为什么？”
- **Current English:** “You have been admitted to a one-year, full-time professional training program that would allow you to enter a field you have wanted to pursue for years, but your place cannot be guaranteed if you postpone it. Just before the program begins, the relative managing your family’s small shop must leave for one year, and your family asks you to take over. Hiring an outside manager would keep the shop operating but substantially reduce the family’s income for that year. You cannot do both. What would you decide, and why?”
- **标注与平衡：** 标注正确；“长期希望”和“明显减少家庭收入”使双方都强，但培训不可保留的确定性仍略偏 B，家庭收入损失的具体性略偏 A。不能轻易两全。
- **混入/文化/翻译：** 混入家庭经营与阶层资源；无文化暗示；双语对应，英文可作母版。
- **可直接替换稿：** 候选 `SOC_FAMILY_02` 将双方不确定性并列。**来源：** Y003，仅相邻、待核验。**结论：** 修改。

## SOC_GENDER_01 — 修改

- **领域/冲突/主体/决定：** 社会；传统性别角色 vs 性别平等；机构决策者；自愿岗位选择或强制轮换。
- **当前中文原文：** “某机构允许合格员工在夜间外勤和日间协调两类任务中申请自己更愿意承担的工作。长期以来，多数男性申请夜间外勤，多数女性申请日间协调，现行制度基本符合员工选择，但夜间外勤更容易积累晋升所需经验。另一方案要求所有合格员工定期轮换两类任务，使晋升经验分配更均等，但部分员工需要承担自己不愿选择的时段并重新安排家庭生活。机构目前只能在两种制度中选择一种。你支持哪一种？为什么？”
- **Current English:** “An organization allows qualified employees to apply for either overnight field work or daytime coordination. Over time, most men have chosen field work and most women have chosen coordination. The current system generally reflects employees’ stated preferences, but field work provides more of the experience needed for promotion. An alternative would rotate all qualified employees through both duties, distributing promotion opportunities more equally but requiring some employees to work schedules they did not choose and reorganize family arrangements. The organization must choose one system. Which should it adopt, and why?”
- **标注与平衡：** 标注可用但“传统”实际被具体为自愿偏好，构念不纯；“更容易晋升”明显有利于轮换/平等。两全不可轻易实现。
- **混入/文化/翻译：** 混入劳动时间、岗位风险和晋升制度；无文化暗示；双语对应。
- **可直接替换稿：** 候选 `SOC_GENDER_01` 为自愿制增加平等晋升审查，也说明轮换的安排成本。**来源：** null，需官方核验。**结论：** 修改。

## SOC_GENDER_02 — 修改

- **领域/冲突/主体/决定：** 社会；传统性别角色 vs 性别平等；一对伴侣；平分育儿假或母亲连续休假。
- **当前中文原文：** “一对伴侣收入和育儿假待遇相近，也都有资格休满一年。一种方案是两人各休六个月，双方共同承担照护和职业中断，但家庭需要在年中更换主要照护者，两人的单位也都要进行工作交接。亲属更赞成由母亲连续休满一年，这符合家庭原有安排且只需一次工作交接，但一整年的职业中断将由她单独承担。两种方案的家庭总收入基本相同，家庭也无法使用外部照护。他们应该选择哪种安排？为什么？”
- **Current English:** “Both partners have comparable incomes and parental-leave benefits, and either could take the full year. One option is for each partner to take six months, sharing caregiving and career interruption but requiring a change of primary caregiver midway through the year and workplace handovers for both partners. Their relatives prefer the mother to take the entire year, which follows the family’s familiar arrangement and requires only one workplace handover, but places the full career interruption on her. Total household income would be similar under either option, and outside care is unavailable. Which arrangement should they choose, and why?”
- **标注与平衡：** 标注正确；“亲属偏好母亲”与“职业中断由她承担”使 B 的规范性更强，A 的连续照护价值不足。仍可能以弹性安排回避。
- **混入/文化/翻译：** 混入婴儿照护连续性、组织交接；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `SOC_GENDER_02` 平衡连续照护与共同职业成本。**来源：** null，需官方核验。**结论：** 修改。

## POL_PARTICIPATION_01 — 修改

- **领域/冲突/主体/决定：** 政治；行政效率 vs 公民参与；市政机构；立即按技术路线审批或先公开听证。
- **当前中文原文：** “某市政机构计划在未来一年内更换一段老化供水管道。技术人员建议在两周内批准费用较低的现有路线，以尽快开工并避免额外维护支出。沿线商户和居民要求先举行听证会并比较替代路线，该程序需要八周，可能减少施工对社区的影响，但会增加维护和规划费用。评估显示，推迟八周不会造成直接安全风险，但两种程序无法同时先行。有关机构应该如何处理？为什么？”
- **Current English:** “A municipal agency plans to replace an aging section of water pipe within the next year. Technical staff recommend approving the lower-cost route within two weeks so construction can begin promptly and additional maintenance expenses can be avoided. Local residents and shop owners request an eight-week hearing and review of alternative routes, which might reduce disruption to the community but would add planning and maintenance costs. Assessments indicate that an eight-week delay would not create an immediate safety risk, and the agency must choose which process to follow first. How should it proceed, and why?”
- **标注与平衡：** 标注正确；两周/八周与低成本使 A 有利，但“无安全风险”又削弱 A，信息方向不够整洁。不可轻易两全。
- **混入/文化/翻译：** 混入公共工程与社区补偿；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `POL_PARTICIPATION_01` 移除任意紧迫性、明确两边成本。**来源：** Y002，仅相邻、待核验。**结论：** 修改。

## POL_PARTICIPATION_02 — 修改

- **领域/冲突/主体/决定：** 政治；行政效率 vs 公民参与；交通部门；先试行或先居民参与。
- **当前中文原文：** “公交多次延误后，社区团体要求在调整线路和时刻表之前成立居民小组并公开征求意见。该程序需要三个月，可能发现规划人员遗漏的出行需求，但会推迟调整。交通部门建议先开展为期六个月、可以撤回的试行，以观察实际出行变化，但部分通勤者将在未参与设计的情况下先承受线路调整。现有时间和预算只允许先采用一种程序。你支持先采用哪一种？为什么？”
- **Current English:** “After repeated bus delays, community groups request a citizen panel and public-comment period before routes and timetables are changed. The process would take three months and might identify travel needs that planners have missed, but it would delay any adjustment. Transit officials propose beginning with a reversible six-month pilot to observe changes in actual travel patterns, but some commuters would experience route changes before having any role in shaping them. Available time and funding allow only one process to occur first. Which should be used first, and why?”
- **标注与平衡：** 标注正确；“观察真实变化”使试行显得更理性，参与方仅被写作拖延。存在先小范围参与等折中回避。
- **混入/文化/翻译：** 混入服务质量和证据治理；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `POL_PARTICIPATION_02` 对两种信息价值同等表述。**来源：** Y002，仅相邻、待核验。**结论：** 修改。

## POL_PRIVACY_01 — 重写

- **领域/冲突/主体/决定：** 政治；公共安全/治理能力 vs 公民自由/隐私；公共交通管理者；人脸识别或人员/照明方案。
- **当前中文原文：** “某公共交通系统中的盗窃案件有所增加。管理机构可以试行一年的人脸识别系统，只与经过授权的嫌疑人名单进行比对，非匹配记录立即删除，并接受独立审计。该方案覆盖范围广、识别速度快，但会扫描所有乘客，也存在误认风险。另一方案是增加巡查人员并改善照明，不收集乘客生物信息，但覆盖范围较小，识别重复作案者通常更慢。评估认为两种方案都有可能减少案件，现有预算只能支持一种。有关机构应该选择哪种？为什么？”
- **Current English:** “Theft has increased across a public transit system. The authority can conduct a one-year facial-recognition trial that compares passengers only against an authorized suspect list, deletes non-matching records immediately, and undergoes independent auditing. It would provide broad coverage and faster identification but would scan every passenger and could produce false matches. Alternatively, the authority could hire more patrol officers and improve lighting, avoiding collection of biometric data but covering fewer locations and usually identifying repeat offenders more slowly. Assessments suggest that either approach could reduce theft, and the budget supports only one. Which should the authority choose, and why?”
- **标注与平衡：** 标注正确；以普通盗窃正当化全体生物识别，风险比例失衡；删除和审计详细弱化隐私风险。不能真正两全。
- **混入/文化/翻译：** 混入刑事严重性、误认和出行寒蝉效应；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `POL_PRIVACY_01` 将威胁改为严重袭击，同时明确寒蝉效应；这改变了事实情境，故建议按“重写”再审。**来源：** null。**结论：** 重写。

## POL_PRIVACY_02 — 修改

- **领域/冲突/主体/决定：** 政治；公共安全/治理能力 vs 公民自由/隐私；立法者；定向司法授权或广泛元数据分析。
- **当前中文原文：** “多起疑似关联的网络入侵导致部分公共服务短时中断，但攻击者之间的联系尚未确定。隐私倡议者和通信服务商主张，官员只能在获得针对具体账户的加急司法授权后查看连接记录；这种方式限制范围，但可能遗漏尚未被识别的关联账户。安全部门则希望在限定期限内自动分析所有用户的连接元数据，以更快发现网络关系；系统不读取通信内容，但会处理大量无关人员的数据。立法者应该采用哪种规则？为什么？”
- **Current English:** “Several potentially related cyber intrusions have briefly disrupted public services, but links among the attackers remain uncertain. Privacy advocates and communication providers propose allowing officials to examine connection records only after obtaining expedited, account-specific judicial authorization. This would limit the scope of collection but might miss related accounts that have not yet been identified. Security officials instead seek time-limited automated analysis of all users’ connection metadata to detect network relationships more quickly. Message content would not be read, but data from many uninvolved people would be processed. What rule should lawmakers adopt, and why?”
- **标注与平衡：** 标注正确；“不读取内容”和期限保护被强调，可能过度弱化广泛收集风险。两边尚可通过分层授权回避。
- **混入/文化/翻译：** 混入司法审查和网络安全能力；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `POL_PRIVACY_02` 补入错误关联和数据删除条件。**来源：** null。**结论：** 修改。

## ECO_WELFARE_01 — 修改

- **领域/冲突/主体/决定：** 经济；政府福利责任 vs 个人责任/自立；政府；延长收入支持或投资就业服务。
- **当前中文原文：** “在持续的经济低迷中，许多劳动者因企业关闭而失业。政府可以通过临时普遍征税，将收入救济从三个月延长到九个月，这能减少失业期间的收入中断，但会增加纳税负担并占用其他公共项目资金。另一方案维持三个月救济，把更多预算用于职业培训、岗位匹配和求职服务；公共支出较低，但未能及时找到工作的人将在三个月后失去收入支持。预算无法同时充分实施两种方案。你支持哪一种？为什么？”
- **Current English:** “During a prolonged economic slowdown, many workers lose their jobs as companies close. The government could fund an extension of income support from three to nine months through a temporary broad tax, reducing income interruption during unemployment but increasing tax burdens and using funds that could support other public programs. Alternatively, it could retain three months of support and direct more funding toward training, job matching, and employment services. This would require less public spending, but people who do not find work quickly would lose income support after three months. The budget cannot fully fund both approaches. Which do you support, and why?”
- **标注与平衡：** 标注正确；原题没有直接写“降低求职积极性”，但“服务”被默认为有效、延长救济收益被写得更确定，证据不对称。折中可能通过比例预算回避。
- **混入/文化/翻译：** 混入失业制度和财政规模；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `ECO_WELFARE_01` 将两种就业效果均表为不确定。**来源：** null。**结论：** 修改。

## ECO_WELFARE_02 — 修改（需决定是否重写）

- **领域/冲突/主体/决定：** 经济；政府福利责任 vs 个人责任/自立；公共医疗体系；固定补贴或普遍风险共担。
- **当前中文原文：** “某公共医疗体系需要确定一种常见但昂贵的长期药物如何分担费用。一项方案维持现有公共缴费水平，为每位患者提供相同的固定补贴，其余费用由个人储蓄或补充保险承担；这能控制公共支出并保留个人选择，但不同家庭实际承担的风险可能不同。另一方案提高所有劳动者的强制缴费，为所有患者提供相同的低额自付费用；这能更广泛地分担风险，但包括可能不使用该药物的人在内，所有人都必须增加缴费。应该采用哪种方案？为什么？”
- **Current English:** “A public health system must decide how to share the cost of a common but expensive long-term medicine. One option keeps current public contributions and gives every patient the same fixed subsidy, leaving the remaining cost to personal savings or supplemental insurance. This would limit public spending and preserve individual choice, but households could face different levels of financial risk. Another option raises mandatory contributions for all workers and provides the same low co-payment to every patient. This would spread risk more broadly, but everyone, including people unlikely to use the medicine, would pay more. Which policy should be adopted, and why?”
- **标注与平衡：** 价值标注可解释，但医疗风险共担混入公平、保险与健康权，不能纯测“自立”；两边成本较对称但可用收入分层折中。
- **混入/文化/翻译：** 明显混入医疗公平；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `ECO_WELFARE_02` 只改善对称措辞，未消除混构念。**来源：** null。**结论：** 修改；研究人员应决定是否完全重写。

## ECO_REDISTRIBUTION_01 — 修改

- **领域/冲突/主体/决定：** 经济；收入平等/再分配 vs 市场激励/个人努力；立法者；提高高收入税率并补贴低薪劳动者或维持税率。
- **当前中文原文：** “立法者正考虑提高最高个人收入档的税率，并用新增收入提高对低工资劳动者的补贴。该方案会直接缩小税后收入差距，但也会减少高收入者可自行支配的部分收入，并可能影响部分人的投资或经营决定。维持现有税率可以保留当前的税后回报和激励，但低工资补贴不会增加，税后收入差距也不会缩小。独立预测认为两种政策影响的具体幅度都存在不确定性。你更支持哪一种？为什么？”
- **Current English:** “Lawmakers are considering a higher tax rate on the highest personal incomes and using the additional revenue to increase a wage supplement for low-paid workers. The policy would directly narrow after-tax income differences, but it would also reduce the income retained by high earners and might affect some investment or business decisions. Keeping current tax rates would preserve existing after-tax returns and incentives, but the wage supplement would not increase and after-tax income differences would not narrow. Independent forecasts indicate uncertainty about the size of both effects. Which policy do you support, and why?”
- **标注与平衡：** 标注正确；“保留激励”较肯定而税收后果只是“可能”，且现状被动叙述，轻微偏 B。难以两全。
- **混入/文化/翻译：** 混入税收、投资与劳动力市场；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `ECO_REDISTRIBUTION_01` 对两边行为与分配后果均表不确定。**来源：** null。**结论：** 修改。

## ECO_REDISTRIBUTION_02 — 修改

- **领域/冲突/主体/决定：** 经济；收入平等/再分配 vs 市场激励/个人努力；企业；70/30绩效方案或30/70平均方案。
- **当前中文原文：** “一家盈利企业需要分配固定的年度奖金池。现有记录显示，经营结果同时受到个人产出和团队协作影响，但无法精确区分两者贡献。一项方案将70%的奖金按个人销售额和生产效率分配、30%平均分配，使奖金与可衡量绩效联系更紧，但这些指标也会受到岗位和客户分配影响。另一方案将30%按个人指标分配、70%平均分配，能够缩小奖金差距并更多体现共同贡献，但会减弱个人指标与奖励之间的联系。企业应该采用哪种方案？为什么？”
- **Current English:** “A profitable company must distribute a fixed annual bonus pool. Existing records indicate that results depend on both individual output and team coordination, but their contributions cannot be separated precisely. One plan distributes 70 percent according to individual sales and productivity and 30 percent equally, creating a stronger link between measurable performance and reward, although those measures are also affected by job and client assignments. Another distributes 30 percent by individual measures and 70 percent equally, narrowing bonus differences and recognizing shared contributions but weakening the link between individual measures and reward. Which plan should the company adopt, and why?”
- **标注与平衡：** 标注正确；指标受岗位分配影响使绩效方案明显受质疑，而平均分配被“承认共同贡献”正面化，略偏 A。不能真正两全。
- **混入/文化/翻译：** 混入测量误差与企业治理；无文化暗示；双语一致。
- **可直接替换稿：** 候选 `ECO_REDISTRIBUTION_02` 同时说明两种方案的测量与分配代价。**来源：** null。**结论：** 修改。

## 最终人工确认清单

1. 逐字确认每一个候选中英文翻译的语义等价，而非仅确认大意。
2. 决定 `POL_PRIVACY_01` 的安全事件强度是否适当，及 `ECO_WELFARE_02` 是否因健康公平混构念而重写。
3. 核验 Y003、Y002 及任何日后要使用的 WVS Wave 7 题项；在核验前不得将它们写成直接来源。
4. 复核每题是否允许不破坏实验目的的“混合方案”回答，并决定分析时如何编码该类答案。
5. 在研究人员逐题确认后，才可另行决定是否替换原题库、更新版本和开始真实 API 小规模试跑。
