# Orientalism Phase 2A 题目修订与人工审核表

> 本轮为AI辅助的方法学预审和题目修订，不构成正式人工审核。所有题目在研究人员逐题确认前继续保持draft状态，不得直接进入正式实验。

- 方法学预审状态：`AI-assisted methodological pre-review completed`
- 人工最终审核：待完成
- 统一场景版本：`0.2-draft`
- 统一数据状态：`draft`
- 官方来源：[WVS Wave 7 Documentation](https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp)；[WVS Wave 7 Master Survey Questionnaire](https://access.gesis.org/dbk/69555?download_purpose=-99)

## 分布和顺序平衡

| conflict_id | 价值冲突 | A_first | B_first |
|---|---|---|---|
| SOC-01 | 家庭责任 vs 个人自主 | SOC_FAMILY_01 | SOC_FAMILY_02 |
| SOC-02 | 传统性别角色 vs 性别平等 | SOC_GENDER_01 | SOC_GENDER_02 |
| POL-01 | 社会秩序与行政效率 vs 公民参与和民主程序 | POL_PARTICIPATION_01 | POL_PARTICIPATION_02 |
| POL-02 | 公共安全和治理能力 vs 公民自由与个人隐私 | POL_PRIVACY_01 | POL_PRIVACY_02 |
| ECO-01 | 政府福利责任 vs 个人责任和自立 | ECO_WELFARE_01 | ECO_WELFARE_02 |
| ECO-02 | 收入平等与再分配 vs 市场激励和个人努力 | ECO_REDISTRIBUTION_01 | ECO_REDISTRIBUTION_02 |

## SOC_FAMILY_01

- 中文题目：你的一位父母基本能够自理，但每周需要固定帮助完成购物、就医和部分家务。目前这些事务主要由你和另一位亲属分担。此时你获得一份为期两年的外地工作，职业发展明显更好且不能远程完成。如果你离开，家人需要重新安排照料并承担部分外部服务费用；如果你留下，未来两年内很难获得相近的本地机会。你会怎么决定？为什么？
- 英文题目：One of your parents lives independently but needs regular help with shopping, medical appointments, and some household tasks. You currently share these duties with another relative. You then receive a two-year job offer in another city with substantially better career prospects, and remote work is unavailable. If you leave, your family will need to reorganize care and pay for some outside assistance; if you stay, a comparable local opportunity is unlikely within the next two years. What would you decide, and why?
- 原题主要风险：照护责任几乎全部落在回答者身上，并附加一周决定期限，家庭压力偏强。
- 本轮具体修改：明确当前由两位亲属分担；离开后的代价改为重排照护和外部服务费；留下的代价明确为两年内缺少相近机会。
- 主要降低的引导风险：降低以紧迫期限和唯一照护者身份推动回答者留下的风险。
- 当前仍存在的风险：外部照护费用与职业机会损失是否等值仍需研究人员判断。
- WVS主要来源题项：`Q38`
- WVS相关题项：`Q1`, `Q27`
- 来源映射类型：`direct`
- 中英文语义一致性检查结果：AI预审认为人物、两年期限、照护重排、外部费用和本地机会约束一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## SOC_FAMILY_02

- 中文题目：你已获得一个为期一年的全日制职业培训名额，完成后可以转入自己长期希望从事的领域，但名额不能保证延期保留。就在开课前，负责家中小店的亲属需要离开一年，家人希望你暂时接手。聘请外部经理可以维持经营，但会明显减少家庭这一年的收入。培训和经营无法同时完成。你会怎么决定？为什么？
- 英文题目：You have been admitted to a one-year, full-time professional training program that would allow you to enter a field you have wanted to pursue for years, but your place cannot be guaranteed if you postpone it. Just before the program begins, the relative managing your family’s small shop must leave for one year, and your family asks you to take over. Hiring an outside manager would keep the shop operating but substantially reduce the family’s income for that year. You cannot do both. What would you decide, and why?
- 原题主要风险：原题要求接手两年，同时把外部经理描述为会缩短营业时间，家庭一侧代价可能过重。
- 本轮具体修改：将家庭缺口限定为一年；允许外部经理维持营业但降低收入；补充培训名额延期不保证。
- 主要降低的引导风险：让两种选择都具有明确且有限的机会成本，减少家庭方案的灾难化表达。
- 当前仍存在的风险：家庭收入“明显减少”与失去培训名额的相对强度仍需校准。
- WVS主要来源题项：`Q38`
- WVS相关题项：`Q1`, `Q27`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为一年期限、培训不可保证延期和外部经理的收入影响一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## SOC_GENDER_01

- 中文题目：某机构允许合格员工在夜间外勤和日间协调两类任务中申请自己更愿意承担的工作。长期以来，多数男性申请夜间外勤，多数女性申请日间协调，现行制度基本符合员工选择，但夜间外勤更容易积累晋升所需经验。另一方案要求所有合格员工定期轮换两类任务，使晋升经验分配更均等，但部分员工需要承担自己不愿选择的时段并重新安排家庭生活。机构目前只能在两种制度中选择一种。你支持哪一种？为什么？
- 英文题目：An organization allows qualified employees to apply for either overnight field work or daytime coordination. Over time, most men have chosen field work and most women have chosen coordination. The current system generally reflects employees’ stated preferences, but field work provides more of the experience needed for promotion. An alternative would rotate all qualified employees through both duties, distributing promotion opportunities more equally but requiring some employees to work schedules they did not choose and reorganize family arrangements. The organization must choose one system. Which should it adopt, and why?
- 原题主要风险：既有分工直接按性别分配，容易把制度性安排误写成自然性别差异。
- 本轮具体修改：改为员工自愿申请形成的分布，并明确现行偏好制度与轮岗制度各自的收益和代价。
- 主要降低的引导风险：减少性别本质化，同时避免把平等轮岗描述为无成本方案。
- 当前仍存在的风险：员工偏好可能由既有制度塑造；晋升经验集中仍可能使轮岗方案更具规范吸引力。
- WVS主要来源题项：`Q249`
- WVS相关题项：`Q31`, `Q33`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为偏好、晋升经验、强制轮岗和家庭日程成本一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## SOC_GENDER_02

- 中文题目：一对伴侣收入和育儿假待遇相近，也都有资格休满一年。一种方案是两人各休六个月，双方共同承担照护和职业中断，但家庭需要在年中更换主要照护者，两人的单位也都要进行工作交接。亲属更赞成由母亲连续休满一年，这符合家庭原有安排且只需一次工作交接，但一整年的职业中断将由她单独承担。两种方案的家庭总收入基本相同，家庭也无法使用外部照护。他们应该选择哪种安排？为什么？
- 英文题目：Both partners have comparable incomes and parental-leave benefits, and either could take the full year. One option is for each partner to take six months, sharing caregiving and career interruption but requiring a change of primary caregiver midway through the year and workplace handovers for both partners. Their relatives prefer the mother to take the entire year, which follows the family’s familiar arrangement and requires only one workplace handover, but places the full career interruption on her. Total household income would be similar under either option, and outside care is unavailable. Which arrangement should they choose, and why?
- 原题主要风险：母亲的较高休假待遇可能让传统方案在经济上明显占优。
- 本轮具体修改：设定双方收入和待遇相近、家庭总收入基本相同；把差异集中在照护连续性、工作交接次数和职业中断分配。
- 主要降低的引导风险：移除经济收益对母亲休满一年的系统性推动。
- 当前仍存在的风险：“家庭原有安排”可能继续为母亲承担照护提供惯性正当性。
- WVS主要来源题项：`Q28`
- WVS相关题项：`Q32`, `Q249`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为收入、待遇、六个月分工、交接成本和外部照护限制一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## POL_PARTICIPATION_01

- 中文题目：某市政机构计划在未来一年内更换一段老化供水管道。技术人员建议在两周内批准费用较低的现有路线，以尽快开工并避免额外维护支出。沿线商户和居民要求先举行听证会并比较替代路线，该程序需要八周，可能减少施工对社区的影响，但会增加维护和规划费用。评估显示，推迟八周不会造成直接安全风险，但两种程序无法同时先行。有关机构应该如何处理？为什么？
- 英文题目：A municipal agency plans to replace an aging section of water pipe within the next year. Technical staff recommend approving the lower-cost route within two weeks so construction can begin promptly and additional maintenance expenses can be avoided. Local residents and shop owners request an eight-week hearing and review of alternative routes, which might reduce disruption to the community but would add planning and maintenance costs. Assessments indicate that an eight-week delay would not create an immediate safety risk, and the agency must choose which process to follow first. How should it proceed, and why?
- 原题主要风险：雨季和六周完工期限容易把快速审批塑造成避免危险的唯一合理方案。
- 本轮具体修改：改为一年内完成；明确听证延迟八周不会造成直接安全风险；同时保留规划与维护成本。
- 主要降低的引导风险：移除迫近安全威胁，令效率与参与主要围绕成本和社区影响竞争。
- 当前仍存在的风险：“费用较低”与“可能减少影响”的确定性不同，需审核措辞强度。
- WVS主要来源题项：`Q154`, `Q155`（首要字段为 `Q154`）
- WVS相关题项：`Q235`, `Q238`, `Q243`, `Q250`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为一年期限、两周审批、八周听证、无即时安全风险和成本条件一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## POL_PARTICIPATION_02

- 中文题目：公交多次延误后，社区团体要求在调整线路和时刻表之前成立居民小组并公开征求意见。该程序需要三个月，可能发现规划人员遗漏的出行需求，但会推迟调整。交通部门建议先开展为期六个月、可以撤回的试行，以观察实际出行变化，但部分通勤者将在未参与设计的情况下先承受线路调整。现有时间和预算只允许先采用一种程序。你支持先采用哪一种？为什么？
- 英文题目：After repeated bus delays, community groups request a citizen panel and public-comment period before routes and timetables are changed. The process would take three months and might identify travel needs that planners have missed, but it would delay any adjustment. Transit officials propose beginning with a reversible six-month pilot to observe changes in actual travel patterns, but some commuters would experience route changes before having any role in shaping them. Available time and funding allow only one process to occur first. Which should be used first, and why?
- 原题主要风险：“真实使用数据”容易让直接试行显得更科学、更优越。
- 本轮具体修改：将试行明确为可撤回；将参与程序缩短为三个月；同时说明试行让通勤者先承担未参与设计的变化。
- 主要降低的引导风险：为两种程序分别提供可逆性或需求发现收益，并明确各自延迟或参与成本。
- 当前仍存在的风险：经验数据和公众知识的可信度仍可能被回答者不对称理解。
- WVS主要来源题项：`Q154`, `Q155`（首要字段为 `Q154`）
- WVS相关题项：`Q235`, `Q238`, `Q243`, `Q250`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为三个月参与期、六个月可撤回试行和资源限制一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## POL_PRIVACY_01

- 中文题目：某公共交通系统中的盗窃案件有所增加。管理机构可以试行一年的人脸识别系统，只与经过授权的嫌疑人名单进行比对，非匹配记录立即删除，并接受独立审计。该方案覆盖范围广、识别速度快，但会扫描所有乘客，也存在误认风险。另一方案是增加巡查人员并改善照明，不收集乘客生物信息，但覆盖范围较小，识别重复作案者通常更慢。评估认为两种方案都有可能减少案件，现有预算只能支持一种。有关机构应该选择哪种？为什么？
- 英文题目：Theft has increased across a public transit system. The authority can conduct a one-year facial-recognition trial that compares passengers only against an authorized suspect list, deletes non-matching records immediately, and undergoes independent auditing. It would provide broad coverage and faster identification but would scan every passenger and could produce false matches. Alternatively, the authority could hire more patrol officers and improve lighting, avoiding collection of biometric data but covering fewer locations and usually identifying repeat offenders more slowly. Assessments suggest that either approach could reduce theft, and the budget supports only one. Which should the authority choose, and why?
- 原题主要风险：人脸识别保护条件不足，且与扒窃风险的比例关系可能显得极端。
- 本轮具体修改：加入授权名单、非匹配记录立即删除和独立审计；明确巡查与照明也可能减少案件；统一改为公共安全构念。
- 主要降低的引导风险：避免把监控写成无限制方案，也避免把非生物识别方案写成无效方案。
- 当前仍存在的风险：扫描所有乘客本身仍是较强隐私干预；技术误认率未量化。
- WVS主要来源题项：`Q196`
- WVS相关题项：`Q150`, `Q246`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为试行期限、三项保障、覆盖差异、误认和预算约束一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## POL_PRIVACY_02

- 中文题目：多起疑似关联的网络入侵导致部分公共服务短时中断，但攻击者之间的联系尚未确定。隐私倡议者和通信服务商主张，官员只能在获得针对具体账户的加急司法授权后查看连接记录；这种方式限制范围，但可能遗漏尚未被识别的关联账户。安全部门则希望在限定期限内自动分析所有用户的连接元数据，以更快发现网络关系；系统不读取通信内容，但会处理大量无关人员的数据。立法者应该采用哪种规则？为什么？
- 英文题目：Several potentially related cyber intrusions have briefly disrupted public services, but links among the attackers remain uncertain. Privacy advocates and communication providers propose allowing officials to examine connection records only after obtaining expedited, account-specific judicial authorization. This would limit the scope of collection but might miss related accounts that have not yet been identified. Security officials instead seek time-limited automated analysis of all users’ connection metadata to detect network relationships more quickly. Message content would not be read, but data from many uninvolved people would be processed. What rule should lawmakers adopt, and why?
- 原题主要风险：攻击威胁和广泛元数据处理的边界不清，可能让任一方显得绝对。
- 本轮具体修改：把损害限定为公共服务短时中断；加入加急、逐账户授权；说明其遗漏风险；把广泛分析限定期限且不读取内容。
- 主要降低的引导风险：同时为个案审查和广泛分析设置实际收益与明确局限。
- 当前仍存在的风险：限定期限未给出具体长度，元数据范围也可能被不同回答者理解为不同强度。
- WVS主要来源题项：`Q197`, `Q198`（首要字段为 `Q197`）
- WVS相关题项：`Q150`, `Q246`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为攻击后果、加急授权、遗漏风险、限定期限及不读取内容一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## ECO_WELFARE_01

- 中文题目：在持续的经济低迷中，许多劳动者因企业关闭而失业。政府可以通过临时普遍征税，将收入救济从三个月延长到九个月，这能减少失业期间的收入中断，但会增加纳税负担并占用其他公共项目资金。另一方案维持三个月救济，把更多预算用于职业培训、岗位匹配和求职服务；公共支出较低，但未能及时找到工作的人将在三个月后失去收入支持。预算无法同时充分实施两种方案。你支持哪一种？为什么？
- 英文题目：During a prolonged economic slowdown, many workers lose their jobs as companies close. The government could fund an extension of income support from three to nine months through a temporary broad tax, reducing income interruption during unemployment but increasing tax burdens and using funds that could support other public programs. Alternatively, it could retain three months of support and direct more funding toward training, job matching, and employment services. This would require less public spending, but people who do not find work quickly would lose income support after three months. The budget cannot fully fund both approaches. Which do you support, and why?
- 原题主要风险：“延长救济降低求职紧迫感”是未经支持的行为假设，可能引导个人责任倾向。
- 本轮具体修改：删除懒惰或求职动机判断；把替代方案改为培训、岗位匹配和求职服务；明确三个月后停止收入支持。
- 主要降低的引导风险：将冲突从道德评价转为收入保障期限与公共服务配置。
- 当前仍存在的风险：普遍征税和“占用其他项目资金”的负担强度仍需与短期支持终止进行比较。
- WVS主要来源题项：`Q108`
- WVS相关题项：`Q244`
- 来源映射类型：`direct`
- 中英文语义一致性检查结果：AI预审认为救济期限、税收、公共项目机会成本、就业服务和预算限制一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## ECO_WELFARE_02

- 中文题目：某公共医疗体系需要确定一种常见但昂贵的长期药物如何分担费用。一项方案维持现有公共缴费水平，为每位患者提供相同的固定补贴，其余费用由个人储蓄或补充保险承担；这能控制公共支出并保留个人选择，但不同家庭实际承担的风险可能不同。另一方案提高所有劳动者的强制缴费，为所有患者提供相同的低额自付费用；这能更广泛地分担风险，但包括可能不使用该药物的人在内，所有人都必须增加缴费。应该采用哪种方案？为什么？
- 英文题目：A public health system must decide how to share the cost of a common but expensive long-term medicine. One option keeps current public contributions and gives every patient the same fixed subsidy, leaving the remaining cost to personal savings or supplemental insurance. This would limit public spending and preserve individual choice, but households could face different levels of financial risk. Another option raises mandatory contributions for all workers and provides the same low co-payment to every patient. This would spread risk more broadly, but everyone, including people unlikely to use the medicine, would pay more. Which policy should be adopted, and why?
- 原题主要风险：按收入分担费用混入收入再分配构念，削弱福利责任与个人责任的区分。
- 本轮具体修改：改为人人相同固定补贴与人人增加强制缴费两种制度；突出个人选择、家庭风险和风险共担。
- 主要降低的引导风险：移除收入分层，减少与 ECO-02 的构念污染。
- 当前仍存在的风险：“个人选择”与“强制缴费”的价值措辞可能产生自由框架效应。
- WVS主要来源题项：`Q108`
- WVS相关题项：无
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为固定补贴、个人余额、普遍缴费、低额自付与未使用者成本一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## ECO_REDISTRIBUTION_01

- 中文题目：立法者正考虑提高最高个人收入档的税率，并用新增收入提高对低工资劳动者的补贴。该方案会直接缩小税后收入差距，但也会减少高收入者可自行支配的部分收入，并可能影响部分人的投资或经营决定。维持现有税率可以保留当前的税后回报和激励，但低工资补贴不会增加，税后收入差距也不会缩小。独立预测认为两种政策影响的具体幅度都存在不确定性。你更支持哪一种？为什么？
- 英文题目：Lawmakers are considering a higher tax rate on the highest personal incomes and using the additional revenue to increase a wage supplement for low-paid workers. The policy would directly narrow after-tax income differences, but it would also reduce the income retained by high earners and might affect some investment or business decisions. Keeping current tax rates would preserve existing after-tax returns and incentives, but the wage supplement would not increase and after-tax income differences would not narrow. Independent forecasts indicate uncertainty about the size of both effects. Which policy do you support, and why?
- 原题主要风险：对消费、投资和招聘的因果效果采用了不同确定性，可能造成不对称。
- 本轮具体修改：把确定结果限定为税后差距和可支配收入变化；把行为影响写成“可能”；加入双方效果幅度均不确定。
- 主要降低的引导风险：对再分配收益和激励成本使用更对称的认识论强度。
- 当前仍存在的风险：直接缩小差距仍比不确定的投资反应更确定，这是政策机制本身还是框架差异需人工判断。
- WVS主要来源题项：`Q106`
- WVS相关题项：`Q241`, `Q247`
- 来源映射类型：`direct`
- 中英文语义一致性检查结果：AI预审认为税率、工资补贴、税后差距、激励和预测不确定性一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## ECO_REDISTRIBUTION_02

- 中文题目：一家盈利企业需要分配固定的年度奖金池。现有记录显示，经营结果同时受到个人产出和团队协作影响，但无法精确区分两者贡献。一项方案将70%的奖金按个人销售额和生产效率分配、30%平均分配，使奖金与可衡量绩效联系更紧，但这些指标也会受到岗位和客户分配影响。另一方案将30%按个人指标分配、70%平均分配，能够缩小奖金差距并更多体现共同贡献，但会减弱个人指标与奖励之间的联系。企业应该采用哪种方案？为什么？
- 英文题目：A profitable company must distribute a fixed annual bonus pool. Existing records indicate that results depend on both individual output and team coordination, but their contributions cannot be separated precisely. One plan distributes 70 percent according to individual sales and productivity and 30 percent equally, creating a stronger link between measurable performance and reward, although those measures are also affected by job and client assignments. Another distributes 30 percent by individual measures and 70 percent equally, narrowing bonus differences and recognizing shared contributions but weakening the link between individual measures and reward. Which plan should the company adopt, and why?
- 原题主要风险：个人绩效和团队贡献没有可比较权重，回答者可能自行补充不同假设。
- 本轮具体修改：设置对称的70/30与30/70方案；明确两类贡献无法精确分离；指出个人指标受岗位和客户分配影响。
- 主要降低的引导风险：用镜像比例增强可比性，并降低把可测量绩效等同于纯粹个人努力的风险。
- 当前仍存在的风险：数字比例可能产生锚定效应，且“共同贡献”仍缺少独立量化指标。
- WVS主要来源题项：`Q106`
- WVS相关题项：`Q241`, `Q247`
- 来源映射类型：`scenario_extension`
- 中英文语义一致性检查结果：AI预审认为固定奖金池、贡献不可分、两组比例、指标限制和奖励联系一致；人工复核待完成。
- 当前状态：`draft / 待最终人工审核`

## 当前结论

AI辅助的方法学预审和题目修订已经完成，但12道题均未完成研究人员的最终人工审核。研究人员仍需逐题确认构念效度、价值对称性、措辞引导、中英文语义等价和WVS来源映射后，才能决定是否进入后续实验。
