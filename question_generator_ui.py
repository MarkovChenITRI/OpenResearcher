"""
OpenResearcher Web UI - Question Generator
Simple web interface for generating research questions
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    print("Installing streamlit...")
    subprocess.check_call(["pip", "install", "streamlit"])
    import streamlit as st

# Page config
st.set_page_config(
    page_title="OpenResearcher Question Generator",
    page_icon="🔬",
    layout="wide"
)

# Title
st.title("🔬 OpenResearcher - Question Generator")
st.markdown("---")

# Mode selection
mode = st.radio(
    "選擇模式",
    ["快速模式（單一問題）", "批次模式（多個問題）", "範本模式（預設範本）"],
    horizontal=True
)

questions = []

if mode == "快速模式（單一問題）":
    st.header("📌 快速模式")
    
    question = st.text_area("請輸入您的研究問題", height=100)
    qid = st.text_input("問題 ID（可選，留空自動生成）")
    
    if st.button("生成問題檔案", type="primary"):
        if question:
            if not qid:
                qid = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            questions.append({
                "qid": qid,
                "question": question,
                "answer": ""
            })
            
            st.success("✅ 問題已新增！")
        else:
            st.error("請輸入問題")

elif mode == "批次模式（多個問題）":
    st.header("📋 批次模式")
    
    num_questions = st.number_input("問題數量", min_value=1, max_value=20, value=3)
    
    for i in range(num_questions):
        with st.expander(f"問題 #{i+1}", expanded=(i==0)):
            cols = st.columns([3, 1])
            with cols[0]:
                q = st.text_area(
                    f"問題 #{i+1}",
                    key=f"q_{i}",
                    height=100
                )
            with cols[1]:
                qid = st.text_input(
                    "問題 ID",
                    value=f"q{i+1}",
                    key=f"qid_{i}"
                )
            
            if q:
                questions.append({
                    "qid": qid,
                    "question": q,
                    "answer": ""
                })

elif mode == "範本模式（預設範本）":
    st.header("📚 範本模式")
    
    template_type = st.selectbox(
        "選擇研究類型",
        [
            "文獻調查（Literature Survey）",
            "論文撰寫（Paper Writing）",
            "技術比較（Technology Comparison）",
            "市場研究（Market Research）",
            "實驗設計（Experiment Design）"
        ]
    )
    
    topic = st.text_input("研究主題", placeholder="例如：Vision Transformer")
    
    if st.button("生成範本", type="primary") and topic:
        if "文獻調查" in template_type:
            questions = [
                {
                    "qid": "survey_overview",
                    "question": f"Provide a comprehensive survey of {topic} (2020-2026). Include: 1) Historical development, 2) Top 15-20 papers with full citations, 3) Key innovations, 4) Performance benchmarks, 5) Current limitations. All papers must include links.",
                    "answer": ""
                },
                {
                    "qid": "survey_sota",
                    "question": f"Identify state-of-the-art methods in {topic}. Compare: 1) Performance metrics, 2) Computational efficiency, 3) Practical applications. Create comparison table with sources.",
                    "answer": ""
                },
                {
                    "qid": "survey_trends",
                    "question": f"Analyze future research trends in {topic} based on recent papers (2024-2026). Include emerging directions and open challenges.",
                    "answer": ""
                }
            ]
        
        elif "論文撰寫" in template_type:
            questions = [
                {
                    "qid": "paper_introduction",
                    "question": f"Write an Introduction section for a paper on '{topic}'. Include: 1) Broad context and motivation, 2) Problem statement, 3) Existing solutions and limitations, 4) Research gap, 5) Contribution, 6) Organization. Use academic style with recent citations (2022-2026).",
                    "answer": ""
                },
                {
                    "qid": "paper_related_work",
                    "question": f"Write a Related Work section for '{topic}'. Organize into subsections with 5-8 papers each. Include full citations and quantitative comparisons.",
                    "answer": ""
                }
            ]
        
        elif "技術比較" in template_type:
            questions = [
                {
                    "qid": "tech_comparison",
                    "question": f"Compare top approaches/tools for {topic}. Create comparison table: features, performance, pros/cons, use cases, pricing. Include 10+ items with sources.",
                    "answer": ""
                }
            ]
        
        elif "市場研究" in template_type:
            questions = [
                {
                    "qid": "market_overview",
                    "question": f"Research {topic} market landscape: major players, market share, trends (2024-2026), growth projections. Provide sources.",
                    "answer": ""
                }
            ]
        
        elif "實驗設計" in template_type:
            questions = [
                {
                    "qid": "exp_dataset",
                    "question": f"Identify datasets for evaluating {topic}: name, size, download link, previous works, benchmarks. List 5+ datasets.",
                    "answer": ""
                },
                {
                    "qid": "exp_baselines",
                    "question": f"Identify baseline methods for {topic}: method name, papers, performance, GitHub links, hyperparameters. List 5-10 baselines.",
                    "answer": ""
                }
            ]
        
        st.success(f"✅ 已生成 {len(questions)} 個範本問題！")

# Preview and save
if questions:
    st.markdown("---")
    st.header("📋 問題預覽")
    
    for i, q in enumerate(questions):
        with st.expander(f"[{q['qid']}] 預覽", expanded=(i==0)):
            st.code(q['question'], language="text")
    
    # Save options
    st.markdown("---")
    st.header("💾 儲存與執行")
    
    cols = st.columns(2)
    
    with cols[0]:
        filename = st.text_input(
            "檔案名稱",
            value=f"research_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
    
    with cols[1]:
        output_dir = st.text_input(
            "輸出目錄",
            value="results/research"
        )
    
    if st.button("💾 儲存問題檔案", type="primary"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ 已儲存到: {filename}")
        
        # Show JSON
        with st.expander("查看 JSON 內容"):
            st.json(questions)
        
        # Generate command
        st.markdown("---")
        st.subheader("🚀 執行命令")
        
        command = f"""python deploy_agent.py \\
    --vllm_server_url AZURE_OPENAI \\
    --dataset_name custom \\
    --data_path {filename} \\
    --browser_backend serper \\
    --output_dir {output_dir} \\
    --model_name_or_path gpt-5.4"""
        
        st.code(command, language="bash")
        
        st.info(f"預計執行時間: {len(questions) * 15} - {len(questions) * 30} 分鐘")
        
        if st.button("▶️ 立即執行研究"):
            with st.spinner("研究執行中..."):
                try:
                    result = subprocess.run([
                        "python", "deploy_agent.py",
                        "--vllm_server_url", "AZURE_OPENAI",
                        "--dataset_name", "custom",
                        "--data_path", filename,
                        "--browser_backend", "serper",
                        "--output_dir", output_dir,
                        "--model_name_or_path", "gpt-5.4"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        st.success("✅ 研究完成！")
                        
                        # Show results
                        result_file = Path(output_dir) / "node_0_shard_0.jsonl"
                        if result_file.exists():
                            with open(result_file, 'r', encoding='utf-8') as f:
                                results = [json.loads(line) for line in f]
                            
                            st.markdown("---")
                            st.header("📊 研究結果")
                            
                            for result in results:
                                with st.expander(f"[{result['qid']}] {result['question'][:100]}..."):
                                    st.markdown(result['answer'])
                    else:
                        st.error(f"❌ 執行失敗: {result.stderr}")
                
                except Exception as e:
                    st.error(f"❌ 錯誤: {str(e)}")

# Sidebar with tips
with st.sidebar:
    st.header("💡 使用提示")
    
    st.markdown("""
    ### 快速模式
    適合單一研究問題
    
    ### 批次模式
    適合多個獨立問題
    
    ### 範本模式
    使用預設的研究範本：
    - 文獻調查
    - 論文撰寫
    - 技術比較
    - 市場研究
    - 實驗設計
    
    ---
    
    ### 問題撰寫技巧
    
    ✅ **好的問題**：
    - 具體明確
    - 指定時間範圍
    - 要求引用來源
    - 說明輸出格式
    
    ❌ **避免**：
    - 過於籠統
    - 沒有具體要求
    - 範圍太廣
    
    ---
    
    ### 範例問題
    
    **文獻調查**：
    ```
    Survey Vision Transformer 
    papers (2020-2026). 
    List top 15 papers with:
    1) Citations
    2) Innovations
    3) Benchmarks
    4) Links
    ```
    
    **論文撰寫**：
    ```
    Write Introduction for 
    'VLM Fine-tuning'. 
    Include: context, problem,
    gap, contribution.
    Use 2022-2026 citations.
    ```
    """)
    
    st.markdown("---")
    st.markdown("🔬 **OpenResearcher + Azure GPT-5.4**")
    st.markdown("深度研究工具")

# Footer
st.markdown("---")
st.caption("💡 提示：儲存後可以手動編輯 JSON 檔案來調整問題")
