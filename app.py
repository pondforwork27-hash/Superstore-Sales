import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Geographic Sales Insights",
    page_icon="🗺️",
    layout="wide"
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* แก้ปัญหาการบังกัน: บังคับให้เนื้อหาหลักเริ่มต่ำลงมา */
    .main .block-container {
        padding-top: 150px !important; 
    }
    .filter-bar {
        background: linear-gradient(135deg, #3a6f8f 0%, #4a85a8 50%, #5a9abf 100%);
        border: 1px solid #7ab3d0;
        border-bottom: 1px solid rgba(180,220,255,0.3);
        border-radius: 0 0 14px 14px;
        padding: 12px 20px 10px 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        position: relative; overflow: hidden;
    }
    /* ── Filter label and input text colors ── */
    .filter-bar label { color: #ffffff !important; font-size: 0.75rem !important; font-weight: 600 !important; }
    .filter-bar [data-baseweb="select"] input { color: #ffffff !important; }
    .filter-bar [data-baseweb="select"] input::placeholder { color: #ffffff !important; opacity: 1 !important; }
    .filter-bar [data-baseweb="select"] [class$="placeholder"],
    .filter-bar [data-baseweb="select"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
    [data-testid="stMultiSelect"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
    /* ── Multiselect selected tags ── */
    span[data-baseweb="tag"] {
        background: linear-gradient(135deg, #2d6080, #3a7a9e) !important;
        border: 1px solid #a8d4f0 !important;
        border-radius: 20px !important;
        color: #ffffff !important;
    }
    span[data-baseweb="tag"] span { color: #ffffff !important; }
    span[data-baseweb="tag"] [role="presentation"] svg { fill: #d0eeff !important; }
    /* multiselect container */
    [data-baseweb="select"] > div {
        background: rgba(58,111,143,0.75) !important;
        border: 1px solid #7ab3d0 !important;
        border-radius: 8px !important;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: #d0eeff !important;
        box-shadow: 0 0 0 2px rgba(200,230,255,0.3) !important;
    }
    /* dropdown menu */
    [data-baseweb="popover"] ul { background: #3a6f8f !important; border: 1px solid #7ab3d0 !important; }
    [data-baseweb="popover"] li { color: #e8f4ff !important; }
    [data-baseweb="popover"] li:hover { background: #2d6080 !important; color: #fff !important; }
    [data-baseweb="popover"] li[aria-selected="true"] {
        background: #245070 !important;
        color: #d0eeff !important;
    }
    .filter-bar::before {
        content: '';
        position: absolute; top:0; left:0; right:0; bottom:0;
        background:
            radial-gradient(circle at 15% 60%, rgba(66,153,225,0.07) 0%, transparent 55%),
            radial-gradient(circle at 85% 20%, rgba(99,179,237,0.05) 0%, transparent 45%);
        pointer-events: none;
    }
    .filter-title {
        font-size: 0.68rem; font-weight: 700; color: #63b3ed;
        text-transform: uppercase; letter-spacing: 0.13em; margin-bottom: 8px;
    }
    .active-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; margin-bottom:2px; }
    .pill {
        display:inline-flex; align-items:center; gap:5px;
        background:rgba(30,58,95,0.9); border:1px solid #2d5a8a;
        border-radius:16px; padding:3px 10px; font-size:0.73rem; color:#90cdf4;
    }
    .pill.state { border-color:#e94560; color:#feb2b2; }
    .state-badge {
        display:inline-flex; align-items:center; gap:8px;
        background:linear-gradient(90deg,#1e3a5f,#2d5a8a);
        border:1px solid #4299e1; border-radius:20px;
        padding:5px 14px; font-size:0.8rem; color:#90cdf4; margin-bottom:10px;
    }
    .state-badge strong { color:#fff; }
    .insight-card {
        background:linear-gradient(135deg,#0d1b2a 0%,#1b2a3b 100%);
        border-left:4px solid #4299e1; border-radius:8px;
        padding:14px 18px; margin-bottom:10px; color:#f0f0f0;
    }
    .insight-card.warn  { border-left-color:#ed8936; }
    .insight-card.good  { border-left-color:#48bb78; }
    .insight-card.alert { border-left-color:#e94560; }
    .insight-card .icon { font-size:1.3rem; }
    .insight-card .label {
        font-size:0.7rem; color:#a0aec0;
        text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px;
    }
    .insight-card .value { font-size:1.35rem; font-weight:700; color:#fff; }
    .insight-card .detail { font-size:0.82rem; color:#90cdf4; margin-top:3px; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Sentinel + JS: true fixed-position filter ─────────────────────────────────
st.markdown('<span id="filter-sentinel"></span>', unsafe_allow_html=True)
import streamlit.components.v1 as _stc
_stc.html("""
<script>
(function () {
  var DONE = false;
  function fixFilter() {
    if (DONE) return;
    var sentinel = document.getElementById('filter-sentinel');
    if (!sentinel) return;
    var block = sentinel;
    var found = false;
    for (var i = 0; i < 12; i++) {
      if (!block.parentElement) return;
      block = block.parentElement;
      if (block.getAttribute('data-testid') === 'stVerticalBlock') {
        if (block.querySelector('.filter-bar')) { found = true; break; }
      }
    }
    if (!found) return;
    if (block.getAttribute('data-filter-fixed') === '1') return;
    block.setAttribute('data-filter-fixed', '1');
    DONE = true;
    function applyFixed() {
      var parentRect = block.parentElement.getBoundingClientRect();
      block.style.cssText = [
        'position:fixed',
        'top:0',
        'left:' + parentRect.left + 'px',
        'width:' + parentRect.width + 'px',
        'z-index:9999',
        'background:rgba(8,15,26,0.96)',
        'backdrop-filter:blur(8px)',
        '-webkit-backdrop-filter:blur(8px)',
      ].join(';');
    }
    applyFixed();
    window.addEventListener('resize', applyFixed);
  }
  fixFilter();
  new MutationObserver(function(muts) {
    muts.forEach(function(m) { if (m.addedNodes.length) fixFilter(); });
  }).observe(document.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

# [ ... โค้ดส่วนที่เหลือของคุณตรงนี้ ... ]
