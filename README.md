# 报销处理 Skill

这个 skill 用来处理报销材料，按模板整理成可直接继续处理的 Excel 结果。它会结合图片、PDF 和文档内容做分类、提取和填充，并尽量保持原有表格里的公式不被破坏。

## 中文

### 先决条件

1. 运行这个 skill 的模型必须支持看图和多模态输入。
2. 依赖需要先装好：
   ```bash
   python3 -m pip install docling openpyxl pandas
   ```
3. 运行前要先做环境检查：
   ```bash
   python3 engine/check_env.py
   ```

### 目录规范

请把输入文件按下面方式放好：

- `input/工作餐/`
- `input/招待/`

工作餐和招待不要只靠文件名区分，优先按目录放置。其他材料可以放在同级输入目录中，再由系统一起扫描。

### 隐私边界

- 首次引导时产生的本地配置，只保存在当前用户机器上。
- 默认保存位置是 `~/.reimburse/`。
- 不要把个人信息、公司信息、账号信息或运行时数据写进仓库文件。

### 运行流程

#### 第一步：首次引导

如果是第一次运行，或者用户明确要求重新设置，先问这三个问题：

1. 报销主体的全名或关键字是什么
2. 工作餐默认人数是多少
3. 工作餐常见的最大人数是多少

回答后，把结果保存到本地配置里，后续直接复用。

#### 第二步：检查和扫描

1. 先做环境检查，确认依赖可用。
2. 扫描输入目录里的所有文件。
3. 如果遇到 OFD 文件，优先找同名 PDF；没有 PDF 时再让用户补充。
4. 用具备视觉能力的模型或可解析文档的工具，识别每个文件的类型、日期、金额和归属主体。

#### 第三步：分类和整理

1. 区分酒店、工作餐、招待、交通、电话等材料。
2. 工作餐和招待必须以目录为准，不要只看文件名。
3. 如果有差旅申请类材料，提取出发地、目的地和事由，整理成简短说明，方便后续填写机票等条目。
4. 根据识别结果，把数据整理成适合模板填写的结构。
5. 如果主体识别第一次失败，先做二次语义/多模态复查，再自动归入已配置主体并在报告中提示复核，不输出 `UNKNOWN_ENTITY` 桶。

#### 第四步：写入模板

1. 按模板把内容写入 Excel。
2. 尽量保留原有公式和自动计算。
3. 如果行数不够，就先扩展再写入，不要硬塞。

#### 第五步：校验和汇报

1. 检查输出文件是否生成。
2. 抽查金额和合计是否合理。
3. 给出运行摘要和需要人工确认的地方。
4. 如果工作餐人数需要修正，后续按紧凑格式回复，例如 `2,3,2,1`。

### 适用方式

- 通过支持 skill 的代理工具调用。
- 或者直接用命令行运行。

### 命令行示例

```bash
PYTHONPATH=. python3 reimburse.py --input-dir <invoices_folder> --template <template.xlsx> --output-dir <output_folder>
```

如果需要重新走首次引导：

```bash
PYTHONPATH=. python3 reimburse.py --setup --input-dir <invoices_folder> --template <template.xlsx> --output-dir <output_folder>
```

### 输出

- 终端会给出本次处理摘要。
- 输出目录里会生成运行报告文件，供后续查看。

## English

### Prerequisites

1. The model running this skill must support vision and multimodal input.
2. Install the required libraries:
   ```bash
   python3 -m pip install docling openpyxl pandas
   ```
3. Run the environment check before processing:
   ```bash
   python3 engine/check_env.py
   ```

### Folder Rules

Organize dining files using these folders:

- `input/工作餐/`
- `input/招待/`

Use folders as the source of truth. Do not rely only on file names.

### Privacy Boundary

- First-run configuration is stored locally on the current user machine.
- Default storage location: `~/.reimburse/`.
- Do not write personal data, company data, account data, or runtime data into repository files.

### Workflow

#### 1. First-Run Guidance

On the first run, or when reset is requested, ask for:

1. The reimbursement entity full name or keyword
2. The default headcount for work meals
3. The usual maximum headcount for work meals

Save the answers to local configuration and reuse them later.

#### 2. Check and Scan

1. Run the environment check first.
2. Scan all files in the input directory.
3. If an OFD file appears, prefer a same-name PDF; otherwise ask for a PDF copy.
4. Use a vision-capable model or document parser to identify file type, date, amount, and entity.

#### 3. Classify and Organize

1. Separate hotel, work meal, hospitality, transport, and phone-related materials.
2. Work meal and hospitality classification must follow the folder structure, not only file names.
3. If travel application material exists, extract origin, destination, and reason for concise flight descriptions.
4. Convert the results into a template-friendly structure.
5. If entity recognition fails in the first pass, run a second semantic/multimodal review, then assign into configured entity buckets with a review note (no final `UNKNOWN_ENTITY` bucket).

#### 4. Write to Template

1. Fill the Excel template with the prepared data.
2. Preserve existing formulas and automatic calculations whenever possible.
3. If the sheet runs out of rows, expand first and then write.

#### 5. Validate and Report

1. Verify that output files were created.
2. Spot-check totals and amounts.
3. Provide a run summary and any manual review points.
4. If work-meal headcount needs correction, use compact replies such as `2,3,2,1`.

### Usage

```bash
PYTHONPATH=. python3 reimburse.py --input-dir <invoices_folder> --template <template.xlsx> --output-dir <output_folder>
```

To rerun first-run guidance:

```bash
PYTHONPATH=. python3 reimburse.py --setup --input-dir <invoices_folder> --template <template.xlsx> --output-dir <output_folder>
```

### Output

- A terminal summary is printed after each run.
- A report file is written to the output directory for follow-up.
