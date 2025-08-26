# 🧠 MinionS Protocol - Cost-Efficient Local-Remote LLM Collaboration

This example demonstrates the **MinionS protocol**, a groundbreaking approach for cost-efficient collaboration between
small on-device models and large cloud models.
Based on research from Stanford's Hazy Research lab, MinionS achieves **5.7× cost reduction**
while maintaining **97.9% of cloud model performance**.

## 🚀 Getting Started

### Requirements

+ **[Docker Desktop] 4.43.0+ or [Docker Engine]** installed.
+ **A laptop or workstation with a GPU** (e.g., a MacBook) for running open models locally. If you
  don't have a GPU, you can alternatively use **[Docker Offload]**.
+ If you're using [Docker Engine] on Linux or [Docker Desktop] on Windows, ensure that the
  [Docker Model Runner requirements] are met (specifically that GPU
  support is enabled) and the necessary drivers are installed.
+ If you're using Docker Engine on Linux, ensure you have [Docker Compose] 2.38.1 or later installed.
+ An [OpenAI API Key](https://platform.openai.com/api-keys) 🔑.

### Quick Start

1. **Clone the official MinionS repository and navigate to the Docker setup:**

    ```bash
    git clone https://github.com/HazyResearch/minions.git
    cd minions/apps/minions-docker
    ```

2. **Set your OpenAI API key:**

    ```bash
    export OPENAI_API_KEY=sk-your-key-here
    ```

3. **Customize the model for better accuracy (recommended):**

   Edit the `docker-compose.minions.yml` file to use qwen3 instead of llama3.2:

    ```yaml
    models:
      worker:
        model: ai/qwen3  # Changed from ai/llama3.2 for better accuracy (8B vs 3B params)
        context_size: 10000
    ```

4. **Launch the MinionS protocol:**

    ```bash
    docker compose -f docker-compose.minions.yml up --build
    ```

5. **Open your browser** and navigate to `http://localhost:8080` to access the interactive interface.

## 🧠 What is the MinionS Protocol?

The MinionS protocol enables **cost-efficient collaboration** between:

+ **Local Model** (on-device): Handles document reading, context processing, and initial analysis
+ **Remote Model** (cloud): Provides supervision, final reasoning, and quality assurance

### Key Innovation: Decomposition Strategy

Unlike simple chat protocols, MinionS uses a sophisticated **decompose-execute-aggregate** approach:

1. **Decompose**: Remote model breaks complex tasks into simple, parallel subtasks
2. **Execute**: Local model processes subtasks in parallel on document chunks  
3. **Aggregate**: Remote model synthesizes results and provides final answers

## 📊 Cost Analysis & Performance

### Academic Research Results

Based on the [Stanford research paper](https://arxiv.org/pdf/2502.15964), MinionS demonstrates:

| Protocol | Cost Reduction | Performance Recovery | Use Case |
|----------|---------------|---------------------|----------|
| **MinionS (8B local)** | **5.7× cheaper** | **97.9%** of remote performance | Production ready |
| **MinionS (3B local)** | **6.0× cheaper** | **93.4%** of remote performance | Resource constrained |
| Minion (simple chat) | 30.4× cheaper | 87.0% of remote performance | Basic tasks |

### Real-World Token Usage

**Research Paper Analysis Example:**

+ **Task**: "What are the three evaluation datasets used in the paper?"
+ **Remote-only**: ~30,064 tokens
+ **MinionS**: ~7,500-15,388 tokens  
+ **Savings**: 50-75% token reduction

## 🎯 Interactive Demo: Compare Remote vs MinionS

The MinionS interface includes a **toggle feature** that lets you compare:

### Remote-Only Mode

+ Processes the entire document with cloud model
+ Higher token usage and cost
+ Baseline performance

### MinionS Mode  

+ Local model reads and processes document chunks
+ Remote model provides supervision and final answers
+ Dramatically reduced cloud costs
+ Maintained quality

## 🎮 Step-by-Step Demo

### Example: Research Paper Analysis

1. **Start the system** following the Quick Start guide above

2. **Load the MinionS research paper** as your document:
   - Download: <https://arxiv.org/pdf/2502.15964>
   - Upload through the web interface

3. **Ask the example question**:

   ```text
   Task: "What are the three evaluation datasets used in the paper?"
   Document Metadata: "Research Paper"
   ```

4. **Compare modes**:
   - **Remote-only**: Watch token usage (~30k tokens)
   - **MinionS**: See the dramatic reduction (~7.5-15k tokens)

5. **Expected answer**: "The three evaluation datasets are FinanceBench, LongHealth, and QASPER"

### Model Customization

**Recommended**: Upgrade from llama3.2 (3B) to qwen3 (8B) for better accuracy:

```yaml
# In docker-compose.minions.yml
models:
  worker:
    model: ai/qwen3        # 8B parameters - better accuracy
    # model: ai/llama3.2   # 3B parameters - faster download
    context_size: 10000
```

**Trade-offs**:

+ **qwen3**: Slightly slower to download, significantly better accuracy
+ **llama3.2**: Faster to pull, adequate for simple tasks

## 🤝 When to Use MinionS

### ✅ Ideal Use Cases

+ **Document Analysis**: Financial reports, medical records, research papers
+ **Long Context Tasks**: Multi-page document processing
+ **Cost-Sensitive Applications**: High-volume document processing
+ **Privacy-Conscious**: Keep sensitive data local while leveraging cloud intelligence

## 🧹 Cleanup

To stop and remove containers:

```bash
cd minions/apps/minions-docker
docker compose -f docker-compose.minions.yml down -v
```

## 📚 Additional Resources

### Official MinionS Resources

+ **Research Paper**: [Minions: Cost-efficient Collaboration Between On-device and Cloud Language Models](https://arxiv.org/pdf/2502.15964)
+ **GitHub Repository**: [HazyResearch/minions](https://github.com/HazyResearch/minions)
+ **Docker Setup**: [minions-docker](https://github.com/HazyResearch/minions/tree/main/apps/minions-docker)

### Academic Citation

```bibtex
@article{narayan2025minions,
  title={Minions: Cost-efficient Collaboration Between On-device and Cloud Language Models},
  author={Narayan, Avanika and Biderman, Dan and Eyuboglu, Sabri and May, Avner and Linderman, Scott and Zou, James and R{\'e}, Christopher},
  journal={arXiv preprint arXiv:2502.15964},
  year={2025}
}
```

## 🏆 Key Benefits Summary

+ **💰 Cost Reduction**: 5.7× cheaper than remote-only processing
+ **🎯 High Accuracy**: Maintains 97.9% of cloud model performance  
+ **🔧 Easy Customization**: Simple model swapping (llama3.2 → qwen3)

---

## 📎 Credits

+ **Research**: [Stanford Hazy Research Lab](https://hazyresearch.stanford.edu/)
+ **Authors**: Avanika Narayan, Dan Biderman, Sabri Eyuboglu, and team
+ **Implementation**: [HazyResearch/minions](https://github.com/HazyResearch/minions)
+ **Docker Integration**: Compose for Agents community

[Docker Compose]: https://github.com/docker/compose
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[Docker Engine]: https://docs.docker.com/engine/
[Docker Model Runner requirements]: https://docs.docker.com/ai/model-runner/
[Docker Offload]: https://www.docker.com/products/docker-offload/
