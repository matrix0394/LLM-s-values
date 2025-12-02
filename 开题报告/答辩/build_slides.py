# -*- coding: utf-8 -*-
"""生成开题答辩HTML slides"""

slides_content = '''
            <!-- 封面 -->
            <section class="title-slide">
                <h1>大模型价值观评价方法研究</h1>
                <h3 style="color: #666; margin-top: 30px;">基于世界价值观调查的跨语言评估框架</h3>
                <p style="margin-top: 50px; font-size: 0.9em;">开题报告答辩</p>
                <p style="font-size: 0.8em; color: #888;">2025年11月</p>
            </section>

            <!-- 目录 -->
            <section>
                <h2>汇报内容</h2>
                <div style="margin-top: 40px;">
                    <ol style="font-size: 1.1em; line-height: 2;">
                        <li><span class="highlight">立题依据</span> - 研究背景与意义</li>
                        <li><span class="highlight">研究内容与目标</span> - 核心问题与预期成果</li>
                        <li><span class="highlight">方案设计</span> - 研究方法与技术路线</li>
                        <li><span class="highlight">课题特色</span> - 创新点</li>
                        <li><span class="highlight">研究基础</span> - 条件保障</li>
                    </ol>
                </div>
            </section>

            <!-- 第一部分：立题依据 -->
            <section>
                <section>
                    <h2>一、立题依据</h2>
                    <h3>1.1 研究背景</h3>
                    <div class="box">
                        <p><strong>大模型的广泛应用</strong></p>
                        <p>从ChatGPT、Claude到文心一言、DeepSeek，大语言模型已广泛应用于教育、医疗、法律咨询等关键领域</p>
                    </div>
                    <div class="box" style="border-left-color: var(--warning-color);">
                        <p><strong>价值观风险</strong></p>
                        <p>大模型并非价值中立，在训练过程中从海量文本数据中习得了隐含的价值观和文化偏见</p>
                    </div>
                </section>

                <section>
                    <h2>一、立题依据</h2>
                    <h3>1.2 三重挑战</h3>
                    <div class="two-column">
                        <div class="framework-box">
                            <h4 style="color: var(--accent-color);">❶ 量化指标缺失</h4>
                            <p class="small-text">缺乏系统化的量化指标体系，难以在统一框架下比较不同模型的价值倾向</p>
                        </div>
                        <div class="framework-box">
                            <h4 style="color: var(--accent-color);">❷ 跨语言评估不足</h4>
                            <p class="small-text">现有研究多基于单一语言（主要是英语），缺乏对语言因素影响的系统性研究</p>
                        </div>
                    </div>
                    <div class="framework-box" style="margin-top: 20px;">
                        <h4 style="color: var(--accent-color);">❸ 实证数据缺乏</h4>
                        <p class="small-text">多数研究基于小样本或特定场景，难以揭示模型在真实多元文化环境中的表现规律</p>
                    </div>
                </section>

                <section>
                    <h2>一、立题依据</h2>
                    <h3>1.3 研究目标</h3>
                    <div class="box">
                        <p><strong>建立系统化的大模型价值观评价方法</strong></p>
                        <ul>
                            <li>以<span class="highlight">世界价值观调查（WVS）</span>为基准</li>
                            <li>采用<span class="highlight">Inglehart-Welzel文化地图</span>二维框架</li>
                            <li>使用<span class="highlight">文化距离</span>指标量化评估</li>
                            <li>构建<span class="highlight">多语言对照</span>实验设计</li>
                        </ul>
                    </div>
                </section>

                <section>
                    <h2>一、立题依据</h2>
                    <h3>1.4 研究现状</h3>
                    <div class="small-text">
                        <p><strong>基础性研究</strong></p>
                        <ul>
                            <li>Bender等（2021）：大规模训练会系统性放大语料中的社会偏见</li>
                            <li>斯坦福CRFM：评估体系需超越准确率，涵盖公平性、鲁棒性等维度</li>
                        </ul>
                        <p><strong>价值观测量</strong></p>
                        <ul>
                            <li>CrowS-Pairs、StereoSet：群体偏见探测</li>
                            <li>Tao等（2024）、Dwivedi-Yu等（2023）：文化视角评估</li>
                        </ul>
                        <p><strong>研究空白</strong></p>
                        <ul>
                            <li class="highlight">缺乏大规模、系统性的跨语言实证研究</li>
                        </ul>
                    </div>
                </section>
            </section>

            <!-- 第二部分：研究内容与目标 -->
            <section>
                <section>
                    <h2>二、研究内容与目标</h2>
                    <h3>2.1 研究设计：三阶段递进</h3>
                    <div class="framework-box">
                        <p><strong>Stage 0: 文化坐标系基准</strong></p>
                        <p class="small-text">基于WVS数据获得109个国家/地区的文化坐标</p>
                    </div>
                    <div class="framework-box">
                        <p><strong>Stage 1: 模型价值观基线</strong></p>
                        <p class="small-text">测试10个主流LLM的原生价值倾向（后续扩展至15-20个）</p>
                    </div>
                    <div class="framework-box">
                        <p><strong>Stage 3: 多语言对比实验</strong></p>
                        <p class="small-text">34国家/地区 × 10模型 × 10语言 = 669条数据（后续扩展至50+国家/地区 × 15+语言）</p>
                    </div>
                </section>

                <section>
                    <h2>二、研究内容与目标</h2>
                    <h3>2.2 当前研究规模</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                        <div class="stat-box">
                            <div>测试模型</div>
                            <div class="stat-number">10</div>
                            <div class="small-text">GPT-4o-mini, Gemini, Claude, Llama, DeepSeek等</div>
                        </div>
                        <div class="stat-box">
                            <div>测试语言</div>
                            <div class="stat-number">10</div>
                            <div class="small-text">英语 + 9种母语</div>
                        </div>
                        <div class="stat-box">
                            <div>国家/地区</div>
                            <div class="stat-number">34</div>
                            <div class="small-text">东亚、俄语区、阿拉伯语区、西班牙语区</div>
                        </div>
                        <div class="stat-box">
                            <div>模仿数据</div>
                            <div class="stat-number">669</div>
                            <div class="small-text">严格控制变量的配对实验</div>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>二、研究内容与目标</h2>
                    <h3>2.3 三个关键科学问题</h3>
                    <div class="box">
                        <p><strong>问题1：如何量化价值观？</strong></p>
                        <p class="small-text">将抽象的价值观概念转化为可测量、可比较的量化指标</p>
                    </div>
                    <div class="box">
                        <p><strong>问题2：全球文化表征偏差？</strong></p>
                        <p class="small-text">模型对109个国家/地区的文化表征能力及偏差分布规律</p>
                    </div>
                    <div class="box">
                        <p><strong>问题3：语言效应机制？</strong></p>
                        <p class="small-text">语言因素对模型文化表征的影响及其"他者叙事"机制</p>
                    </div>
                </section>

                <section>
                    <h2>二、研究内容与目标</h2>
                    <h3>2.4 初步研究发现</h3>
                    <div class="small-text">
                        <p><strong>发现1：西方中心化偏移</strong></p>
                        <p>10个模型普遍表现出"世俗理性"与"自我表达"倾向，集中在坐标系右上象限</p>
                        <p><strong>发现2：跨文化理解能力</strong></p>
                        <p>模型平均文化距离约2.3，Claude 3.7与Gemini 2.0表现较好（2.1-2.2）</p>
                        <p><strong>发现3：语言效应的文化依赖性</strong></p>
                        <ul>
                            <li>东亚地区："殖民地-本土"梯度（香港+48% → 日本-24%）</li>
                            <li>拉丁美洲：母语优势明显（-26%）</li>
                            <li>西亚南亚：轻微英语优势（+9%）</li>
                        </ul>
                    </div>
                </section>
            </section>

            <!-- 第三部分：方案设计 -->
            <section>
                <section>
                    <h2>三、方案设计</h2>
                    <h3>3.1 研究方法</h3>
                    <div class="two-column">
                        <div>
                            <div class="framework-box">
                                <h4>问卷调查法</h4>
                                <p class="small-text">基于WVS标准化问卷，多语言翻译与校验</p>
                            </div>
                            <div class="framework-box">
                                <h4>实验法</h4>
                                <p class="small-text">多阶段对照实验，单一变量原则</p>
                            </div>
                        </div>
                        <div>
                            <div class="framework-box">
                                <h4>比较分析法</h4>
                                <p class="small-text">横向、纵向、参照三维比较</p>
                            </div>
                            <div class="framework-box">
                                <h4>统计分析法</h4>
                                <p class="small-text">PPCA降维、欧氏距离、配对比较</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>三、方案设计</h2>
                    <h3>3.2 技术路线</h3>
                    <div class="small-text">
                        <p><strong>Stage 0: 文化坐标系基准构建</strong></p>
                        <ul>
                            <li>使用PPCA处理WVS数据（109国家/地区）</li>
                            <li>Varimax旋转增强可解释性</li>
                            <li>建立"传统-世俗理性"与"生存-自我表达"二维坐标</li>
                        </ul>
                        <p><strong>Stage 1: 模型价值观基线测量</strong></p>
                        <ul>
                            <li>"零情境"测试，揭示模型默认价值取向</li>
                            <li>当前10个模型，后续扩展至15-20个</li>
                        </ul>
                        <p><strong>Stage 2: 全球文化模仿能力评估</strong></p>
                        <ul>
                            <li>109个国家/地区角色扮演，统一使用英语</li>
                            <li>计算文化距离，分析地理分布模式</li>
                        </ul>
                        <p><strong>Stage 3: 跨语言效应对照实验</strong></p>
                        <ul>
                            <li>配对对照：母语 vs 英语</li>
                            <li>当前34国家/地区，后续扩展至50+</li>
                        </ul>
                    </div>
                </section>

                <section>
                    <h2>三、方案设计</h2>
                    <h3>3.3 核心计算方法</h3>
                    <div class="box">
                        <p><strong>概率主成分分析（PPCA）</strong></p>
                        <p class="small-text">X = CZ + μ + ε，自然处理缺失数据，EM算法迭代优化</p>
                    </div>
                    <div class="box">
                        <p><strong>文化距离</strong></p>
                        <p class="small-text">d(A,B) = √[(PC1_A - PC1_B)² + (PC2_A - PC2_B)²]</p>
                    </div>
                    <div class="box">
                        <p><strong>英语优势指标</strong></p>
                        <p class="small-text">Adv = (d_native - d_english) / d_native</p>
                        <p class="small-text">配对比较控制模型能力差异，避免辛普森悖论</p>
                    </div>
                </section>

                <section>
                    <h2>三、方案设计</h2>
                    <h3>3.4 可行性分析</h3>
                    <div class="small-text">
                        <p><strong>✓ 数据基础</strong></p>
                        <ul>
                            <li>WVS第七波权威数据，109个国家/地区</li>
                            <li>已积累约1100个模型测试样本</li>
                        </ul>
                        <p><strong>✓ 技术保障</strong></p>
                        <ul>
                            <li>完整的自动化采集与分析系统</li>
                            <li>自主实现PPCA算法，版本控制</li>
                        </ul>
                        <p><strong>✓ 质量控制</strong></p>
                        <ul>
                            <li>多层质量保障机制</li>
                            <li>翻译语境核验，拒答专门分析</li>
                        </ul>
                    </div>
                </section>
            </section>

            <!-- 第四部分：课题特色 -->
            <section>
                <section>
                    <h2>四、课题特色</h2>
                    <h3>三大创新点</h3>
                    <div class="box">
                        <h4 class="highlight">1. 构建"人类社会-大模型"可对齐的价值坐标系</h4>
                        <p class="small-text">创新性地将Inglehart-Welzel文化维度理论应用于大模型评估，自主实现PPCA算法，实现"人类-模型"坐标精确对齐</p>
                    </div>
                    <div class="box">
                        <h4 class="highlight">2. 开展109个国家/地区的全球文化模仿实验</h4>
                        <p class="small-text">覆盖全球八大文化区域，系统分析文化距离的地理分布模式，识别模型的"文化盲点"</p>
                    </div>
                    <div class="box">
                        <h4 class="highlight">3. 提出"英语优势"量化指标</h4>
                        <p class="small-text">严格配对对照实验，控制混杂变量，揭示"殖民地-本土"梯度现象和"他者叙事"机制</p>
                    </div>
                </section>

                <section>
                    <h2>四、课题特色</h2>
                    <h3>创新点1：可对齐的价值坐标系</h3>
                    <div class="small-text">
                        <p><strong>理论创新</strong></p>
                        <ul>
                            <li>填补大模型评估领域缺乏社会科学理论支撑的空白</li>
                            <li>评估结果具有明确的社会学意义</li>
                        </ul>
                        <p><strong>技术创新</strong></p>
                        <ul>
                            <li>自主实现PPCA算法，自然处理缺失数据</li>
                            <li>不依赖现成统计软件包，完全可控</li>
                        </ul>
                        <p><strong>应用价值</strong></p>
                        <ul>
                            <li>可以说"某模型接近北欧国家"而非抽象数值</li>
                            <li>为跨文化、跨时间、跨模型研究提供统一参照标准</li>
                        </ul>
                    </div>
                </section>

                <section>
                    <h2>四、课题特色</h2>
                    <h3>创新点2：全球文化模仿实验</h3>
                    <div class="small-text">
                        <p><strong>实验规模</strong></p>
                        <ul>
                            <li>109个国家/地区，八大文化区域</li>
                            <li>统一角色扮演提示模板，控制语言变量</li>
                        </ul>
                        <p><strong>系统性分析</strong></p>
                        <ul>
                            <li>量化文化理解准确度（欧氏距离）</li>
                            <li>识别模型在哪些区域表现好/差</li>
                            <li>揭示训练数据的地理分布特征</li>
                        </ul>
                        <p><strong>研究价值</strong></p>
                        <ul>
                            <li>相比小规模、局部性测试，提供全球性、系统性评估新范式</li>
                        </ul>
                    </div>
                </section>

                <section>
                    <h2>四、课题特色</h2>
                    <h3>创新点3："英语优势"量化指标</h3>
                    <div class="small-text">
                        <p><strong>方法创新</strong></p>
                        <ul>
                            <li>配对对照实验：母语 vs 英语，其他条件完全一致</li>
                            <li>配对比较方法：控制模型能力差异，避免辛普森悖论</li>
                            <li>问卷由研究者基于原文初译，在大模型辅助下进行语义与语境审校，并通过多轮对照原文修订，尽量保证多语言版本的等价性</li>
                        </ul>
                        <p><strong>重要发现</strong></p>
                        <ul>
                            <li>东亚"殖民地-本土"梯度：香港+48% → 日本-24%</li>
                            <li>拉丁美洲母语优势：西班牙-87%</li>
                            <li>揭示"他者叙事"机制：前殖民地更多被外部视角描述</li>
                        </ul>
                        <p><strong>实践意义</strong></p>
                        <ul>
                            <li>为多语言模型文化适配性改进提供重要启示</li>
                        </ul>
                    </div>
                </section>
            </section>

            <!-- 第五部分：研究基础 -->
            <section>
                <section>
                    <h2>五、研究基础与条件保障</h2>
                    <h3>5.1 前期研究基础</h3>
                    <div class="box">
                        <p><strong>数据积累</strong></p>
                        <p class="small-text">累计收集约1100个模型测试样本，覆盖多个主流LLM在不同语言和文化情境下的数据</p>
                    </div>
                    <div class="box">
                        <p><strong>技术工具链</strong></p>
                        <p class="small-text">完整的数据收集、处理、分析与可视化全流程工具，模块化设计，Git版本控制</p>
                    </div>
                    <div class="box">
                        <p><strong>理论准备</strong></p>
                        <p class="small-text">系统梳理大模型价值观评估、跨文化心理学、WVS等相关领域文献</p>
                    </div>
                </section>

                <section>
                    <h2>五、研究基础与条件保障</h2>
                    <h3>5.2 实验条件</h3>
                    <div class="two-column">
                        <div>
                            <div class="framework-box">
                                <h4>硬件与软件</h4>
                                <p class="small-text">Python开发环境，数据分析与可视化库，Git代码管理</p>
                            </div>
                            <div class="framework-box">
                                <h4>数据资源</h4>
                                <p class="small-text">WVS第七波完整数据集，多语言翻译版本</p>
                            </div>
                        </div>
                        <div>
                            <div class="framework-box">
                                <h4>API接口</h4>
                                <p class="small-text">GPT-4、Claude、Gemini等主流模型API密钥</p>
                            </div>
                            <div class="framework-box">
                                <h4>经费支持</h4>
                                <p class="small-text">覆盖API调用、翻译服务等研究支出</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>五、研究基础与条件保障</h2>
                    <h3>5.3 待完善条件及解决方案</h3>
                    <div class="small-text">
                        <p><strong>计算资源</strong></p>
                        <ul>
                            <li>问题：大规模数据处理时内存可能不足</li>
                            <li>方案：优化算法结构，分批处理，申请高性能服务器</li>
                        </ul>
                        <p><strong>翻译质量</strong></p>
                        <ul>
                            <li>问题：部分非英语数据需进一步校对</li>
                            <li>方案：专业翻译团队合作，多译者交叉验证</li>
                        </ul>
                        <p><strong>理论方法</strong></p>
                        <ul>
                            <li>问题：统计分析和价值观测量理论需深化</li>
                            <li>方案：系统学习，导师指导，参加学术会议</li>
                        </ul>
                    </div>
                </section>
            </section>

            <!-- 总结 -->
            <section>
                <h2>总结</h2>
                <div class="box">
                    <h3 class="highlight">研究意义</h3>
                    <ul>
                        <li>填补跨语言价值观评估的研究空白</li>
                        <li>为大模型多语言部署和文化适配提供方法论支持</li>
                        <li>推动大模型价值观评估的规范化发展</li>
                    </ul>
                </div>
                <div class="box" style="border-left-color: var(--success-color);">
                    <h3 class="highlight-green">预期贡献</h3>
                    <ul>
                        <li>建立系统化、可复现的评估框架</li>
                        <li>揭示语言效应的深层机制</li>
                        <li>为模型训练数据优化提供实证依据</li>
                    </ul>
                </div>
            </section>

            <!-- 致谢 -->
            <section class="title-slide">
                <h1>谢谢！</h1>
                <h3 style="color: #666; margin-top: 50px;">请各位老师批评指正</h3>
            </section>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: true,
            transition: 'slide',
            transitionSpeed: 'default',
            backgroundTransition: 'fade',
            controls: true,
            progress: true,
            center: false,
            width: 1280,
            height: 720,
            margin: 0.04
        });
    </script>
</body>
</html>
'''

# 写入文件
output_path = r'e:\Code\value of LLM\LLM\'s values\开题报告\答辩\开题答辩.html'
with open(output_path, 'a', encoding='utf-8') as f:
    f.write(slides_content)

print(f"Slides content appended to: {output_path}")
