# GIST - AI Research Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=yellow" alt="Python 3.9+">
  <a href="https://streamlit.io">
    <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Framework: Streamlit">
  </a>
</p>

The **AI Research Agent** is a smart assistant that helps users **gather, summarize, and synthesize information** on any topic by automatically searching the web, extracting key insights, and citing reputable sources.

It acts like a personal researcher — doing the heavy lifting of reading articles, pulling facts, and generating clean summaries — ideal for **students, professionals, writers, and curious minds**.

---

## ScreenShots

![screenshot1](https://i.ibb.co/cSwQCv7Y/GIST-HOME.png)
<br/>

![screenshot2](https://i.ibb.co/DDsKw50t/GIST-RESULT.png)

---

## 🚀 Core Features

### 🔍 **Advanced Content Extraction**

- **Multi-Method Extraction**: Uses newspaper3k, BeautifulSoup, and readability-lxml for robust content extraction
- **Smart Metadata Detection**: Automatically extracts titles, authors, publish dates, and domain information
- **Intelligent Summarization**: Generates concise summaries from extracted content
- **Fallback Mechanisms**: Multiple extraction methods ensure content is captured even from challenging websites

### 🧠 **AI-Powered Analysis & Summarization**

- **Structured Analysis**: Generates key points, trends, viewpoints, and recommendations
- **Multiple Analysis Types**: Comprehensive, summary-focused, trend analysis, and viewpoint comparison
- **Source Attribution**: Every insight is properly linked to its source with confidence scores
- **Knowledge Gap Identification**: Highlights areas needing further research

### 📚 **Professional Citation Management**

- **Multiple Citation Styles**: Supports APA, MLA, Chicago, Harvard, and IEEE formats
- **Automatic Source Tracking**: Maintains complete bibliographic information
- **In-Text Citations**: Generates proper in-text citations for academic use
- **Reference Lists**: Creates formatted reference lists in your preferred style

### 🖥️ **Enhanced User Interface**

- **Interactive Analysis Display**: Expandable sections for key points, trends, and viewpoints
- **Extraction Statistics**: Shows success rates and methods used for content extraction
- **Source Quality Metrics**: Displays confidence scores and extraction metadata
- **Real-time Progress Tracking**: Visual progress indicators during research

### 💾 **Multiple Export Formats**

- **PDF Reports**: Professional formatted reports with proper citations
- **Markdown Files**: Structured markdown with links and formatting
- **Plain Text**: Clean text format for easy copying and pasting
- **Comprehensive Data**: Includes analysis results, citations, and extraction metadata

---

## 🛠️ Tech Stack

This project combines a powerful set of tools to deliver a seamless research experience.

| Category                | Technology / Library                                                                                                                                                                                                                                                                                                                                                     |
| :---------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**            | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)                                                                                                                                                                                                                                                           |
| **Web Search**          | ![Google Search API](https://img.shields.io/badge/Google%20Search%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)                                                                                                                                                                                                                                          |
| **Summarization (LLM)** | ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)                                                                                                                                                                                                                                              |
| **Content Extraction**  | ![newspaper3k](https://img.shields.io/badge/newspaper3k-3776AB?style=for-the-badge&logo=python&logoColor=white) <br> ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-009688?style=for-the-badge&logo=python&logoColor=white) <br> ![readability-lxml](https://img.shields.io/badge/readability--lxml-FFD43B?style=for-the-badge&logo=python&logoColor=black) |
| **Citation Management** | ![Citations](https://img.shields.io/badge/Citations-APA%2FMLA%2FChicago%2FHarvard%2FIEEE-blue?style=for-the-badge)                                                                                                                                                                                                                                                       |
| **Exporting**           | ![PDF](https://img.shields.io/badge/PDF-FF0000?style=for-the-badge&logo=adobeacrobatreader&logoColor=white) <br> ![Markdown](https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white) <br> ![TXT](https://img.shields.io/badge/TXT-A8A8A8?style=for-the-badge)                                                                    |

---

## 🎯 Key Capabilities

### 📊 **Advanced Research Pipeline**

1. **Multi-Source Search**: Automatically finds relevant sources using Google Search API and DuckDuckGo
2. **Intelligent Content Extraction**: Uses multiple methods (newspaper3k, readability-lxml, BeautifulSoup) to extract clean content
3. **Metadata Detection**: Automatically identifies authors, publish dates, and source credibility
4. **AI Analysis**: Generates structured insights including key points, trends, and different viewpoints
5. **Citation Generation**: Creates properly formatted citations in multiple academic styles

### 🎛️ **Customization Options**

- ⏳ **Time-Filtered Search**: Narrow results to the last week, month, or year
- 🎭 **Tone Selector**: Adjust the summary's tone (Academic, Casual, Professional, Creative)
- 📊 **Source Count**: Control the number of sources to analyze (1-20)
- 📝 **Analysis Types**: Choose between comprehensive, summary-focused, trend, or viewpoint analysis

### 🔧 **Technical Features**

- **Robust Error Handling**: Multiple fallback mechanisms ensure content extraction succeeds
- **Rate Limiting**: Respectful web scraping with delays between requests
- **Memory Management**: Efficient handling of large content volumes
- **Modular Architecture**: Clean separation of concerns for easy maintenance and extension

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-research-agent.git
cd ai-research-agent
```

```bash
# Add API KEYS
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
GOOGLE_SEARCH_KEY="YOUR_GOOGLE_SEARCH_KEY"
GOOGLE_SEARCH_ENGINE_ID="YOUR_GOOGLE_SEARCH_KEY"
```

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/macOS)
venv\Scripts\activate      # (Windows)
```

```bash

# Install dependencies
pip install -r requirements.txt
```
